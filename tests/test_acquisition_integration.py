"""Service checks use simulated research and never contact a model endpoint."""
import importlib
import gc
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from acquisition_runtime.output_handler import save_report
from acquisition_runtime.providers import ResearchResult

ACQUIRER = "acquisition-analysis-acquirer"
TARGET = "acquisition-analysis-target-company"


class FakeProvider:
    def __init__(self, fail=False):
        self.prompts = []
        self.fail = fail

    def run(self, prompt):
        self.prompts.append(prompt)
        if self.fail:
            raise RuntimeError("Simulated research failure")
        return ResearchResult("# Test report\nService transport check only.", "commonstack",
                              metadata={"model": "test-model", "usage": {"input_tokens": 12, "output_tokens": 8}})


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.env = patch.dict(os.environ, {
            "SQLITE_PATH": str(self.directory / "runs.db"),
            "X_SERVICE_TOKEN": "test-service-token",
            "OPENAI_API_KEY": "not-a-real-api-key",
            "OPENAI_BASE_URL": "https://gateway.invalid/v1",
            "RESEARCH_MODEL": "test-model", "RESEARCH_PROVIDER": "openai",
        })
        self.env.start()
        self.app_module = importlib.import_module("service.app")
        self.runner = importlib.import_module("service.runner")
        self.database = importlib.import_module("service.database")
        self.database.init_database()
        self.client = TestClient(self.app_module.app)
        self.headers = {"X-Service-Token": "test-service-token"}
        self.root_patch = patch.object(self.runner, "ROOT_DIR", self.directory)
        self.root_patch.start()

    def tearDown(self):
        self.client.close()
        self.root_patch.stop()
        self.env.stop()
        # The existing sqlite helpers commit via context managers; CPython closes
        # their connections on collection. Release handles before Windows cleanup.
        gc.collect()
        self.temp.cleanup()

    def task(self, agent_id):
        if agent_id == "shell-company-screening":
            return {"client_name": "Test client", "target_market": "Test market"}
        task = {"target_company": "Test target", "research_cutoff_date": "2026-11-08"}
        if agent_id in {ACQUIRER, TARGET}:
            task["acquirer_company" if agent_id == ACQUIRER else "buyer_company"] = "Test buyer"
        return task

    def submit(self, agent_id, task=None):
        with patch.object(self.app_module, "start_run_thread") as start:
            response = self.client.post("/runs", headers=self.headers,
                        json={"agent_id": agent_id, "settings": self.task(agent_id) if task is None else task})
        if response.status_code == 202:
            start.assert_called_once_with(response.json()["run_id"])
        else:
            start.assert_not_called()
        return response

    def test_four_manifests_and_authentication(self):
        for agent_id in ("shell-company-screening", "due-diligence-agent", ACQUIRER, TARGET):
            response = self.client.get("/manifest", params={"agent_id": agent_id}, headers=self.headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["agent_id"], agent_id)
        self.assertEqual(self.client.get("/manifest", params={"agent_id": ACQUIRER}).status_code, 401)
        self.assertEqual(self.client.get("/manifest", params={"agent_id": ACQUIRER}, headers={"X-Service-Token": "wrong"}).status_code, 401)
        self.assertEqual(self.client.get("/manifest", params={"agent_id": "missing"}, headers=self.headers).status_code, 404)

    def test_new_input_validation_before_start(self):
        for agent_id in (ACQUIRER, TARGET):
            for key, value in (("target_company", " "), ("research_cutoff_date", "2026-02-30"), ("unexpected", "text")):
                task = self.task(agent_id)
                task[key] = value
                response = self.submit(agent_id, task)
                self.assertEqual(response.status_code, 422)
                self.assertIn(key, response.json()["field_errors"])
            response = self.submit(agent_id)
            self.assertEqual(response.status_code, 202)
            record = self.database.get_run_record(response.json()["run_id"])
            task = json.loads(record["settings_json"])
            self.assertEqual(task["valuation_date"], "2026-11-08")
            self.assertEqual(task["negotiation_priorities"], "Not specified")

    def test_new_worker_and_result_contract(self):
        prompts = {}
        for agent_id in (ACQUIRER, TARGET):
            response = self.submit(agent_id)
            run_id = response.json()["run_id"]
            self.assertEqual(self.client.get(f"/runs/{run_id}/result", headers=self.headers).status_code, 409)
            fake = FakeProvider()
            with patch.object(self.runner, "get_provider_for_agent", return_value=("commonstack", fake)):
                self.runner.run_research(run_id)
            status = self.client.get(f"/runs/{run_id}", headers=self.headers).json()
            self.assertEqual(status["status"], "completed")
            result = self.client.get(f"/runs/{run_id}/result", headers=self.headers)
            self.assertEqual(result.status_code, 200)
            body = result.json()
            for field in ("report_markdown", "evidence", "usage", "artifacts", "warnings"):
                self.assertIn(field, body)
            self.assertEqual(body["usage"]["input_tokens"], 12)
            self.assertEqual(body["usage"]["output_tokens"], 8)
            self.assertEqual(body["usage"]["provider"], "commonstack")
            self.assertIsNone(body["usage"]["actual_cost_micro"])
            self.assertIn("docx", body["artifacts"])
            self.assertNotIn("pdf", body["artifacts"])
            self.assertTrue(body["warnings"])
            prompts[agent_id] = fake.prompts[0]
        self.assertIn("Stage 6 — Acquisition Returns", prompts[ACQUIRER])
        self.assertIn("Stage 6 — Strategic Alternatives", prompts[TARGET])

    def test_legacy_workers_keep_existing_call_contract(self):
        for agent_id in ("shell-company-screening", "due-diligence-agent"):
            response = self.submit(agent_id)
            self.assertEqual(response.status_code, 202)
            spec = dict(self.runner.AGENTS[agent_id])
            saved_subjects = []
            def save_legacy(result, subject, provider_name=None, output_directory="outputs"):
                saved_subjects.append(subject)
                return save_report(result, output_directory, save_docx=False)
            spec["save_report"] = save_legacy
            with patch.dict(self.runner.AGENTS, {agent_id: spec}), patch.object(self.runner,
                    "get_provider_for_agent", return_value=("openai", FakeProvider())):
                self.runner.run_research(response.json()["run_id"])
            record = self.database.get_run_record(response.json()["run_id"])
            self.assertEqual(record["status"], "completed", record.get("error"))
            self.assertEqual(saved_subjects, [self.task(agent_id)[spec["subject_field"]]])

    def test_failure_and_missing_runs(self):
        response = self.submit(ACQUIRER)
        run_id = response.json()["run_id"]
        with patch.object(self.runner, "get_provider_for_agent", return_value=("commonstack", FakeProvider(fail=True))):
            self.runner.run_research(run_id)
        status = self.client.get(f"/runs/{run_id}", headers=self.headers).json()
        self.assertEqual(status["status"], "failed")
        self.assertIn("Simulated research failure", status["error"])
        self.assertEqual(self.client.get("/runs/missing", headers=self.headers).status_code, 404)
        self.assertEqual(self.client.get("/runs/missing/result", headers=self.headers).status_code, 404)

    def test_gateway_configuration_for_both_agents(self):
        for agent_id in (ACQUIRER, TARGET):
            name, provider = self.runner.get_provider_for_agent(agent_id)
            self.assertEqual(name, "commonstack")
            self.assertEqual(provider.model, "test-model")
            self.assertEqual(provider.base_url, "https://gateway.invalid/v1")
            self.assertIsNone(provider.client)
        with patch.dict(os.environ, {"OPENAI_BASE_URL": "", "RESEARCH_MODEL": ""}):
            name, provider = self.runner.get_provider_for_agent(ACQUIRER)
            self.assertEqual(name, "openai")
            self.assertEqual(provider.model, "o4-mini-deep-research")
        with patch.dict(os.environ, {"RESEARCH_PROVIDER": "gemini"}):
            with self.assertRaises(RuntimeError):
                self.runner.get_provider_for_agent(ACQUIRER)


if __name__ == "__main__":
    unittest.main()
