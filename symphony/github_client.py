from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from urllib import error, request

from .config import GitHubConfig
from .models import GitHubIssue, ProjectStatusField


class GitHubClientError(RuntimeError):
    """Raised when Symphony cannot read or write GitHub state."""


class GitHubClient:
    GRAPHQL_ENDPOINT = "https://api.github.com/graphql"

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
        blockers = set(self._config.blocker_labels)
        candidates = []
        for issue in self.list_project_issues():
            if issue.project_status != self._config.ready_state:
                continue
            if issue.state.upper() != "OPEN":
                continue
            if blockers.intersection(issue.labels):
                continue
            if issue_number is not None and issue.number != issue_number:
                continue
            candidates.append(issue)
        candidates.sort(key=lambda issue: issue.created_at)
        return candidates[0] if candidates else None

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


def _parse_datetime(raw_value: str) -> datetime:
    return datetime.fromisoformat(raw_value.replace("Z", "+00:00"))
