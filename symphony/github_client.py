from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from urllib import parse
from urllib import error, request

from .config import GitHubConfig
from .models import GitHubIssue, IssueComment, ProjectStatusField, PullRequestFile, PullRequestInfo


class GitHubClientError(RuntimeError):
    """Raised when Symphony cannot read or write GitHub state."""


class GitHubClient:
    GRAPHQL_ENDPOINT = "https://api.github.com/graphql"
    REST_ENDPOINT = "https://api.github.com"

    def __init__(self, config: GitHubConfig):
        self._config = config
        self._status_field: ProjectStatusField | None = None

    def get_status_field(self) -> ProjectStatusField:
        if self._status_field is not None:
            return self._status_field

        root = self._query_owner_project(
            """
            query($owner:String!, $number:Int!) {
              OWNER(login:$owner) {
                projectV2(number:$number) {
                  id
                  fields(first:50) {
                    nodes {
                      __typename
                      ... on ProjectV2SingleSelectField {
                        id
                        name
                        options {
                          id
                          name
                        }
                      }
                    }
                  }
                }
              }
            }
            """
        )
        project = root["projectV2"]
        for field in project["fields"]["nodes"]:
            if field.get("__typename") != "ProjectV2SingleSelectField":
                continue
            if field.get("name") != self._config.status_field:
                continue
            options = {option["name"]: option["id"] for option in field.get("options", [])}
            self._status_field = ProjectStatusField(
                project_id=project["id"],
                field_id=field["id"],
                options=options,
            )
            return self._status_field

        raise GitHubClientError(
            f"Project {self._config.project_number} is missing single-select field {self._config.status_field!r}"
        )

    def list_project_issues(self) -> list[GitHubIssue]:
        issues: list[GitHubIssue] = []
        cursor: str | None = None
        while True:
            root = self._query_owner_project(
                """
                query($owner:String!, $number:Int!, $after:String) {
                  OWNER(login:$owner) {
                    projectV2(number:$number) {
                      items(first:100, after:$after) {
                        pageInfo {
                          hasNextPage
                          endCursor
                        }
                        nodes {
                          id
                          fieldValues(first:20) {
                            nodes {
                              __typename
                              ... on ProjectV2ItemFieldSingleSelectValue {
                                name
                                optionId
                                field {
                                  ... on ProjectV2SingleSelectField {
                                    name
                                  }
                                }
                              }
                            }
                          }
                          content {
                            __typename
                            ... on Issue {
                              id
                              number
                              title
                              body
                              state
                              url
                              createdAt
                              updatedAt
                              repository {
                                nameWithOwner
                              }
                              labels(first:20) {
                                nodes {
                                  name
                                }
                              }
                              assignees(first:10) {
                                nodes {
                                  login
                                }
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
                """,
                after=cursor,
            )
            items = root["projectV2"]["items"]
            for node in items["nodes"]:
                issue = self._normalize_issue_node(node)
                if issue is not None:
                    issues.append(issue)
            if not items["pageInfo"]["hasNextPage"]:
                break
            cursor = items["pageInfo"]["endCursor"]
        return issues

    def pick_next_ready_issue(self, issue_number: int | None = None) -> GitHubIssue | None:
        return self.pick_next_issue_by_status((self._config.ready_state,), issue_number=issue_number, honor_blockers=True)

    def pick_next_inbox_issue(self, issue_number: int | None = None) -> GitHubIssue | None:
        return self.pick_next_issue_by_status(("Inbox",), issue_number=issue_number, honor_blockers=False)

    def pick_next_issue_by_status(
        self,
        statuses: tuple[str, ...],
        issue_number: int | None = None,
        honor_blockers: bool = True,
    ) -> GitHubIssue | None:
        blockers = set(self._config.blocker_labels)
        candidates = []
        for issue in self.list_project_issues():
            if issue.project_status not in statuses:
                continue
            if issue.state.upper() != "OPEN":
                continue
            if honor_blockers and blockers.intersection(issue.labels):
                continue
            if issue_number is not None and issue.number != issue_number:
                continue
            candidates.append(issue)
        candidates.sort(key=lambda issue: issue.created_at)
        return candidates[0] if candidates else None

    def get_project_issue(self, issue_number: int) -> GitHubIssue | None:
        for issue in self.list_project_issues():
            if issue.number == issue_number:
                return issue
        return None

    def update_status(self, issue: GitHubIssue, new_state: str) -> None:
        status_field = self.get_status_field()
        option_id = status_field.options.get(new_state)
        if option_id is None:
            raise GitHubClientError(f"Unknown project status option: {new_state}")

        self._graphql(
            """
            mutation($projectId:ID!, $itemId:ID!, $fieldId:ID!, $optionId:String!) {
              updateProjectV2ItemFieldValue(
                input: {
                  projectId: $projectId
                  itemId: $itemId
                  fieldId: $fieldId
                  value: { singleSelectOptionId: $optionId }
                }
              ) {
                projectV2Item {
                  id
                }
              }
            }
            """,
            {
                "projectId": status_field.project_id,
                "itemId": issue.project_item_id,
                "fieldId": status_field.field_id,
                "optionId": option_id,
            },
        )

    def add_issue_to_project(self, issue: GitHubIssue, initial_state: str = "Inbox") -> GitHubIssue:
        status_field = self.get_status_field()
        added = self._graphql(
            """
            mutation($projectId:ID!, $contentId:ID!) {
              addProjectV2ItemById(input: { projectId: $projectId, contentId: $contentId }) {
                item {
                  id
                }
              }
            }
            """,
            {
                "projectId": status_field.project_id,
                "contentId": issue.node_id,
            },
        )
        project_item_id = added["addProjectV2ItemById"]["item"]["id"]
        projected = GitHubIssue(
            node_id=issue.node_id,
            project_item_id=project_item_id,
            repository_full_name=issue.repository_full_name,
            number=issue.number,
            title=issue.title,
            body=issue.body,
            state=issue.state,
            url=issue.url,
            created_at=issue.created_at,
            updated_at=issue.updated_at,
            labels=issue.labels,
            assignees=issue.assignees,
            project_status=initial_state,
        )
        self.update_status(projected, initial_state)
        return projected

    def create_issue_comment(self, issue_number: int, body: str) -> str:
        payload = self._rest(
            "POST",
            f"/repos/{self._config.owner}/{self._config.repo}/issues/{issue_number}/comments",
            {"body": body},
        )
        return str(payload.get("html_url", ""))

    def list_issue_comments(self, issue_number: int) -> tuple[IssueComment, ...]:
        payload = self._rest(
            "GET",
            f"/repos/{self._config.owner}/{self._config.repo}/issues/{issue_number}/comments?per_page=100",
        )
        comments = []
        for comment in payload or []:
            comments.append(
                IssueComment(
                    id=int(comment["id"]),
                    url=comment["html_url"],
                    body=comment.get("body", "") or "",
                    created_at=_parse_datetime(comment["created_at"]),
                    updated_at=_parse_datetime(comment["updated_at"]),
                )
            )
        return tuple(comments)

    def create_issue(self, title: str, body: str, labels: tuple[str, ...] = ()) -> GitHubIssue:
        payload = self._rest(
            "POST",
            f"/repos/{self._config.owner}/{self._config.repo}/issues",
            {"title": title, "body": body, "labels": list(labels)},
        )
        return self._normalize_repo_issue(payload)

    def update_issue(self, issue_number: int, *, body: str | None = None, state: str | None = None) -> GitHubIssue:
        payload: dict[str, Any] = {}
        if body is not None:
            payload["body"] = body
        if state is not None:
            payload["state"] = state
        updated = self._rest("PATCH", f"/repos/{self._config.owner}/{self._config.repo}/issues/{issue_number}", payload)
        return self._normalize_repo_issue(updated)

    def find_open_issue_by_title(self, title: str) -> GitHubIssue | None:
        payload = self._rest("GET", f"/repos/{self._config.owner}/{self._config.repo}/issues?state=open&per_page=100")
        for item in payload or []:
            if "pull_request" in item:
                continue
            if str(item.get("title", "")).strip() == title:
                return self._normalize_repo_issue(item)
        return None

    def get_or_create_draft_pull_request(
        self,
        branch_name: str,
        base_branch: str,
        title: str,
        body: str,
    ) -> PullRequestInfo:
        existing = self.find_open_pull_request(branch_name)
        if existing is not None:
            return existing

        payload = self._rest(
            "POST",
            f"/repos/{self._config.owner}/{self._config.repo}/pulls",
            {
                "title": title,
                "head": branch_name,
                "base": base_branch,
                "body": body,
                "draft": True,
            },
        )
        return PullRequestInfo(
            number=int(payload["number"]),
            url=payload["html_url"],
            title=payload["title"],
            is_draft=bool(payload.get("draft", True)),
            existing=False,
            head_ref_name=str(payload.get("head", {}).get("ref", branch_name)),
            base_ref_name=str(payload.get("base", {}).get("ref", base_branch)),
            body=payload.get("body", "") or "",
            created_at=_parse_datetime(payload["created_at"]) if payload.get("created_at") else None,
            updated_at=_parse_datetime(payload["updated_at"]) if payload.get("updated_at") else None,
            state=str(payload.get("state", "open")).upper(),
            merged=bool(payload.get("merged_at")),
        )

    def find_open_pull_request(self, branch_name: str) -> PullRequestInfo | None:
        return self.find_pull_request(branch_name, state="open")

    def get_pull_request(self, pull_request_number: int) -> PullRequestInfo:
        payload = self._rest("GET", f"/repos/{self._config.owner}/{self._config.repo}/pulls/{pull_request_number}")
        return self._normalize_pull_request(payload, existing=True)

    def list_open_symphony_pull_requests(self, branch_prefix: str, base_branch: str) -> tuple[PullRequestInfo, ...]:
        payload = self._rest("GET", f"/repos/{self._config.owner}/{self._config.repo}/pulls?state=open&per_page=100")
        pull_requests: list[PullRequestInfo] = []
        for item in payload or []:
            info = self._normalize_pull_request(item, existing=True)
            if not info.head_ref_name.startswith(f"{branch_prefix}/"):
                continue
            if info.base_ref_name != base_branch:
                continue
            pull_requests.append(info)
        pull_requests.sort(key=lambda pull_request: pull_request.created_at or datetime.min)
        return tuple(pull_requests)

    def list_pull_request_files(self, pull_request_number: int) -> tuple[PullRequestFile, ...]:
        payload = self._rest(
            "GET",
            f"/repos/{self._config.owner}/{self._config.repo}/pulls/{pull_request_number}/files?per_page=100",
        )
        files = []
        for item in payload or []:
            files.append(
                PullRequestFile(
                    filename=item["filename"],
                    status=str(item.get("status", "modified")),
                    additions=int(item.get("additions", 0)),
                    deletions=int(item.get("deletions", 0)),
                    patch=item.get("patch", "") or "",
                )
            )
        return tuple(files)

    def find_pull_request(self, branch_name: str, state: str = "all") -> PullRequestInfo | None:
        query = parse.urlencode(
            {
                "state": state,
                "head": f"{self._config.owner}:{branch_name}",
            }
        )
        payload = self._rest("GET", f"/repos/{self._config.owner}/{self._config.repo}/pulls?{query}")
        if not payload:
            return None
        pull = payload[0]
        return PullRequestInfo(
            **self._normalize_pull_request(pull, existing=True).__dict__,
        )

    def _normalize_issue_node(self, node: dict[str, Any]) -> GitHubIssue | None:
        content = node.get("content")
        if not content or content.get("__typename") != "Issue":
            return None

        expected_repo = f"{self._config.owner}/{self._config.repo}"
        repository_full_name = content["repository"]["nameWithOwner"]
        if repository_full_name != expected_repo:
            return None

        project_status = ""
        for field_value in node.get("fieldValues", {}).get("nodes", []):
            if field_value.get("__typename") != "ProjectV2ItemFieldSingleSelectValue":
                continue
            if field_value.get("field", {}).get("name") == self._config.status_field:
                project_status = field_value.get("name") or ""
                break

        return GitHubIssue(
            node_id=content["id"],
            project_item_id=node["id"],
            repository_full_name=repository_full_name,
            number=int(content["number"]),
            title=content["title"],
            body=content.get("body") or "",
            state=content["state"],
            url=content["url"],
            created_at=_parse_datetime(content["createdAt"]),
            updated_at=_parse_datetime(content["updatedAt"]),
            labels=tuple(sorted(label["name"].strip().lower() for label in content["labels"]["nodes"])),
            assignees=tuple(sorted(assignee["login"] for assignee in content["assignees"]["nodes"])),
            project_status=project_status,
        )

    def _normalize_repo_issue(self, payload: dict[str, Any]) -> GitHubIssue:
        labels = tuple(sorted((label.get("name", "") or "").strip().lower() for label in payload.get("labels", [])))
        assignees = tuple(sorted((assignee.get("login", "") or "").strip() for assignee in payload.get("assignees", [])))
        return GitHubIssue(
            node_id=str(payload.get("node_id", "")),
            project_item_id="",
            repository_full_name=f"{self._config.owner}/{self._config.repo}",
            number=int(payload["number"]),
            title=payload.get("title", "") or "",
            body=payload.get("body", "") or "",
            state=str(payload.get("state", "OPEN")).upper(),
            url=payload.get("html_url") or payload.get("url") or "",
            created_at=_parse_datetime(payload["created_at"]) if payload.get("created_at") else datetime.min,
            updated_at=_parse_datetime(payload["updated_at"]) if payload.get("updated_at") else datetime.min,
            labels=labels,
            assignees=assignees,
            project_status="",
        )

    def _normalize_pull_request(self, payload: dict[str, Any], *, existing: bool) -> PullRequestInfo:
        return PullRequestInfo(
            number=int(payload["number"]),
            url=payload["html_url"],
            title=payload["title"],
            is_draft=bool(payload.get("draft", False)),
            existing=existing,
            head_ref_name=str(payload.get("head", {}).get("ref", "")),
            base_ref_name=str(payload.get("base", {}).get("ref", "")),
            body=payload.get("body", "") or "",
            created_at=_parse_datetime(payload["created_at"]) if payload.get("created_at") else None,
            updated_at=_parse_datetime(payload["updated_at"]) if payload.get("updated_at") else None,
            state=str(payload.get("state", "open")).upper(),
            merged=bool(payload.get("merged_at")),
        )

    def _query_owner_project(self, query: str, after: str | None = None) -> dict[str, Any]:
        owner_target = "user" if self._config.owner_type == "user" else "organization"
        materialized_query = query.replace("OWNER", owner_target)
        variables: dict[str, Any] = {
            "owner": self._config.owner,
            "number": self._config.project_number,
        }
        if after is not None:
            variables["after"] = after
        data = self._graphql(materialized_query, variables)
        owner_root = data.get(owner_target)
        if owner_root is None:
            raise GitHubClientError(f"Could not resolve GitHub {self._config.owner_type} {self._config.owner!r}")
        if owner_root.get("projectV2") is None:
            raise GitHubClientError(
                f"Could not resolve project {self._config.project_number} for {self._config.owner}"
            )
        return owner_root

    def _graphql(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
        req = request.Request(
            self.GRAPHQL_ENDPOINT,
            data=payload,
            headers={
                "Authorization": f"Bearer {self._config.token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "dowagermod-symphony/0.1",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=30) as response:
                body = response.read().decode("utf-8")
        except error.HTTPError as exc:
            raise GitHubClientError(f"GitHub GraphQL HTTP error: {exc.code}") from exc
        except error.URLError as exc:
            raise GitHubClientError(f"GitHub GraphQL connection error: {exc.reason}") from exc

        decoded = json.loads(body)
        if decoded.get("errors"):
            messages = ", ".join(err.get("message", "unknown error") for err in decoded["errors"])
            raise GitHubClientError(f"GitHub GraphQL error: {messages}")
        return decoded["data"]

    def _rest(self, method: str, path: str, body: dict[str, Any] | None = None) -> Any:
        payload = None
        if body is not None:
            payload = json.dumps(body).encode("utf-8")

        req = request.Request(
            f"{self.REST_ENDPOINT}{path}",
            data=payload,
            headers={
                "Authorization": f"Bearer {self._config.token}",
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json",
                "User-Agent": "dowagermod-symphony/0.1",
            },
            method=method,
        )
        try:
            with request.urlopen(req, timeout=30) as response:
                raw_body = response.read().decode("utf-8")
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace") if exc.fp is not None else ""
            raise GitHubClientError(f"GitHub REST HTTP error: {exc.code} {detail}".strip()) from exc
        except error.URLError as exc:
            raise GitHubClientError(f"GitHub REST connection error: {exc.reason}") from exc

        if not raw_body:
            return None
        return json.loads(raw_body)


def _parse_datetime(raw_value: str) -> datetime:
    return datetime.fromisoformat(raw_value.replace("Z", "+00:00"))
