from __future__ import annotations

from pathlib import Path
from typing import Any

import jinja2
import yaml

from .models import WorkflowDefinition


class WorkflowError(RuntimeError):
    """Raised when the machine-readable Symphony workflow is invalid."""


def load_workflow(path: str | Path) -> WorkflowDefinition:
    workflow_path = Path(path)
    if not workflow_path.is_file():
        raise WorkflowError(f"missing_workflow_file: {workflow_path}")

    raw_text = workflow_path.read_text(encoding="utf-8")
    config: dict[str, Any] = {}
    body = raw_text

    if raw_text.startswith("---"):
        try:
            _, front_matter, remainder = raw_text.split("---", 2)
        except ValueError as exc:
            raise WorkflowError("workflow_parse_error: front matter is not closed") from exc
        parsed = yaml.safe_load(front_matter) or {}
        if not isinstance(parsed, dict):
            raise WorkflowError("workflow_front_matter_not_a_map")
        config = parsed
        body = remainder

    return WorkflowDefinition(
        path=workflow_path,
        config=config,
        prompt_template=body.strip(),
    )


def render_prompt(workflow: WorkflowDefinition, context: dict[str, Any]) -> str:
    environment = jinja2.Environment(
        loader=jinja2.BaseLoader(),
        undefined=jinja2.StrictUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    try:
        template = environment.from_string(workflow.prompt_template)
        return template.render(**context).strip()
    except jinja2.TemplateError as exc:
        raise WorkflowError(f"template_render_error: {exc}") from exc
