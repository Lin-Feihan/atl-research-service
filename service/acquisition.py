"""Adapters for the two independent acquisition analysis agents."""
import json
import os
from pathlib import Path

from acquisition_runtime.output_handler import save_report
from acquisition_runtime.providers import get_provider
from agents.acquisition_analysis_acquirer.runtime.agent_runner import run_agent as run_acquirer
from agents.acquisition_analysis_target_company.runtime.agent_runner import run_agent as run_target

ROOT_DIR = Path(__file__).resolve().parents[1]
ACQUISITION_ROOTS = {
    "acquisition-analysis-acquirer": ROOT_DIR / "agents/acquisition_analysis_acquirer",
    "acquisition-analysis-target-company": ROOT_DIR / "agents/acquisition_analysis_target_company",
}


def get_acquisition_provider(agent_id):
    configured = os.getenv("RESEARCH_PROVIDER", "openai").strip().lower()
    if configured not in {"openai", "commonstack"}:
        raise RuntimeError("Acquisition analysis supports openai or commonstack.")
    gateway = bool(os.getenv("OPENAI_BASE_URL", "").strip())
    provider_name = "commonstack" if gateway else configured
    path = ACQUISITION_ROOTS[agent_id] / "runtime/config.yaml"
    config = json.loads(path.read_text(encoding="utf-8"))["providers"][provider_name]
    provider = get_provider(provider_name=provider_name, config=config)
    return provider_name, provider


def save_acquisition_report(result, target_company, provider_name=None, output_directory="outputs"):
    """Accept the existing worker signature; the service scopes files by run ID."""
    return save_report(result, output_directory, save_docx=True, save_pdf=False)


ACQUISITION_AGENTS = {
    "acquisition-analysis-acquirer": {
        "root": ACQUISITION_ROOTS["acquisition-analysis-acquirer"],
        "run_agent": run_acquirer,
        "save_report": save_acquisition_report,
        "subject_field": "target_company",
    },
    "acquisition-analysis-target-company": {
        "root": ACQUISITION_ROOTS["acquisition-analysis-target-company"],
        "run_agent": run_target,
        "save_report": save_acquisition_report,
        "subject_field": "target_company",
    },
}
