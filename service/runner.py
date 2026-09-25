import base64
import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path

import yaml

from agents.shell_company_screening.runtime.agent_runner import (
    run_agent as run_shell_agent,
)
from agents.shell_company_screening.runtime.output_handler import (
    save_report as save_shell_report,
)
from agents.shell_company_screening.runtime.providers import (
    get_provider as get_shell_provider,
)

from agents.due_diligence.runtime.agent_runner import (
    run_agent as run_due_diligence_agent,
)
from agents.due_diligence.runtime.output_handler import (
    save_report as save_due_diligence_report,
)
from agents.due_diligence.runtime.providers import (
    get_provider as get_due_diligence_provider,
)

from .database import (
    get_run_record,
    save_run_result,
    update_run_status,
)


ROOT_DIR = Path(__file__).resolve().parents[1]

MAX_ARTIFACT_BYTES = 5 * 1024 * 1024


PROVIDER_KEY_ENVS = {
    "openai": "OPENAI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "perplexity": "PERPLEXITY_API_KEY",
}


AGENTS = {
    "shell-company-screening": {
        "root": (
            ROOT_DIR
            / "agents"
            / "shell_company_screening"
        ),
        "run_agent": run_shell_agent,
        "save_report": save_shell_report,
        "get_provider": get_shell_provider,
        "subject_field": "client_name",
    },
    "due-diligence-agent": {
        "root": (
            ROOT_DIR
            / "agents"
            / "due_diligence"
        ),
        "run_agent": run_due_diligence_agent,
        "save_report": save_due_diligence_report,
        "get_provider": get_due_diligence_provider,
        "subject_field": "target_company",
    },
}


def utc_now():
    return (
        datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def get_provider_for_agent(
    agent_id,
):
    spec = AGENTS[agent_id]

    provider_name = (
        os.getenv(
            "RESEARCH_PROVIDER",
            "openai",
        )
        .strip()
        .lower()
    )

    key_env = PROVIDER_KEY_ENVS.get(
        provider_name
    )

    if key_env is None:
        raise RuntimeError(
            f"Unsupported provider: "
            f"{provider_name}"
        )

    api_key = os.getenv(key_env)

    if not api_key:
        raise RuntimeError(
            f"{key_env} is not configured"
        )

    config_path = (
        spec["root"]
        / "runtime"
        / "config.yaml"
    )

    with config_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        config = yaml.safe_load(file) or {}

    provider_config = (
        config
        .get("providers", {})
        .get(provider_name)
    )

    if not provider_config:
        raise RuntimeError(
            f"Provider configuration missing: "
            f"{provider_name}"
        )

    provider_config = dict(
        provider_config
    )

    if not provider_config.get(
        "enabled",
        True,
    ):
        raise RuntimeError(
            f"Provider is disabled: "
            f"{provider_name}"
        )

    model_override = os.getenv(
        "RESEARCH_MODEL"
    )

    if model_override:
        if provider_name in {
            "openai",
            "openrouter",
        }:
            provider_config[
                "model"
            ] = model_override

        elif provider_name == "gemini":
            provider_config[
                "agent"
            ] = model_override

        elif provider_name == "perplexity":
            provider_config[
                "preset"
            ] = model_override

    provider = spec[
        "get_provider"
    ](
        provider_name=provider_name,
        api_key=api_key,
        config=provider_config,
    )

    return (
        provider_name,
        provider,
    )


def encode_artifact(path):
    if path is None:
        return None

    path = Path(path)

    if not path.exists():
        return None

    if (
        path.stat().st_size
        > MAX_ARTIFACT_BYTES
    ):
        return None

    encoded = base64.b64encode(
        path.read_bytes()
    ).decode("ascii")

    return {
        "filename": path.name,
        "content_base64": encoded,
    }


def build_usage_payload(
    research_result,
    provider_name,
):
    metadata = (
        getattr(
            research_result,
            "metadata",
            {},
        )
        or {}
    )

    raw_usage = (
        metadata.get("usage")
        or {}
    )

    if not isinstance(
        raw_usage,
        dict,
    ):
        raw_usage = {}

    input_tokens = (
        raw_usage.get(
            "input_tokens"
        )
        or raw_usage.get(
            "prompt_tokens"
        )
        or 0
    )

    output_tokens = (
        raw_usage.get(
            "output_tokens"
        )
        or raw_usage.get(
            "completion_tokens"
        )
        or 0
    )

    actual_cost_micro = (
        raw_usage.get(
            "actual_cost_micro"
        )
    )

    if actual_cost_micro is None:
        actual_cost_micro = (
            metadata.get(
                "actual_cost_micro"
            )
        )

    if actual_cost_micro is None:
        cost_usd = (
            raw_usage.get(
                "cost_usd"
            )
            or metadata.get(
                "cost_usd"
            )
        )

        if cost_usd is not None:
            actual_cost_micro = round(
                float(cost_usd)
                * 1_000_000
            )

    reported_provider = (
        "commonstack"
        if (
            provider_name == "openai"
            and os.getenv(
                "OPENAI_BASE_URL"
            )
        )
        else provider_name
    )

    return {
        "provider":
            reported_provider,
        "model":
            metadata.get("model"),
        "input_tokens":
            int(input_tokens),
        "output_tokens":
            int(output_tokens),
        "actual_cost_micro":
            (
                int(actual_cost_micro)
                if actual_cost_micro
                is not None
                else None
            ),
    }


def build_result_payload(
    report_paths,
    research_result,
    provider_name,
):
    markdown_path = (
        report_paths.get("markdown")
    )

    evidence_path = (
        report_paths.get("evidence")
    )

    if (
        markdown_path is None
        or not Path(markdown_path).exists()
    ):
        raise RuntimeError(
            "Required Markdown report "
            "was not produced"
        )

    if (
        evidence_path is None
        or not Path(evidence_path).exists()
    ):
        raise RuntimeError(
            "Required evidence JSON "
            "was not produced"
        )

    report_markdown = (
        Path(markdown_path)
        .read_text(
            encoding="utf-8"
        )
    )

    if not report_markdown.strip():
        raise RuntimeError(
            "Markdown report is empty"
        )

    evidence = json.loads(
        Path(evidence_path)
        .read_text(
            encoding="utf-8"
        )
    )

    artifacts = {}

    for artifact_type in (
        "docx",
        "pdf",
    ):
        artifact = encode_artifact(
            report_paths.get(
                artifact_type
            )
        )

        if artifact is not None:
            artifacts[
                artifact_type
            ] = artifact

    return {
        "report_markdown":
            report_markdown,
        "usage":
            build_usage_payload(
                research_result,
                provider_name,
            ),
        "artifacts":
            artifacts,
        "evidence":
            evidence,
    }


def safe_error_message(exc):
    message = str(exc)

    secret_envs = list(
        PROVIDER_KEY_ENVS.values()
    ) + [
        "X_SERVICE_TOKEN",
        "OPENAI_BASE_URL",
    ]

    for env_name in secret_envs:
        secret = os.getenv(env_name)

        if secret:
            message = message.replace(
                secret,
                "[redacted]",
            )

    if not message.strip():
        message = (
            exc.__class__.__name__
        )

    return message[:1000]


def run_research(run_id):
    run = get_run_record(run_id)

    if run is None:
        return

    try:
        agent_id = run["agent_id"]

        spec = AGENTS.get(agent_id)

        if spec is None:
            raise RuntimeError(
                f"Unknown agent: {agent_id}"
            )

        settings = json.loads(
            run["settings_json"]
        )

        provider_name, provider = (
            get_provider_for_agent(
                agent_id
            )
        )

        result = spec[
            "run_agent"
        ](
            settings=settings,
            provider=provider,
        )

        output_directory = (
            ROOT_DIR
            / "outputs"
            / run_id
        )

        report_paths = spec[
            "save_report"
        ](
            result,
            settings[
                spec["subject_field"]
            ],
            provider_name=provider_name,
            output_directory=str(
                output_directory
            ),
        )

        result_payload = (
            build_result_payload(
                report_paths,
                result,
                provider_name,
            )
        )

        save_run_result(
            run_id=run_id,
            result=result_payload,
            completed_at=utc_now(),
        )

    except Exception as exc:
        update_run_status(
            run_id=run_id,
            status="failed",
            error=safe_error_message(
                exc
            ),
            completed_at=utc_now(),
        )


def start_run_thread(run_id):
    thread = threading.Thread(
        target=run_research,
        args=(run_id,),
        name=f"research-{run_id}",
        daemon=True,
    )

    thread.start()
