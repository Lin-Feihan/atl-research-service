# ATL Research Service

A FastAPI service that exposes two Deep Research agents to Agentic Trading Lab (ATL):

- `shell-company-screening`
- `due-diligence-agent`

The service wraps the existing agent runtimes without changing their core research workflows. It provides authenticated HTTP endpoints, asynchronous run management, SQLite run state, CommonStack integration, and ATL v1.1 usage reporting.

## API

The service exposes four authenticated endpoint patterns:

```text
GET  /manifest?agent_id=...
POST /runs
GET  /runs/{run_id}
GET  /runs/{run_id}/result
```

Every request must include:

```text
X-Service-Token: <service-token>
```

Missing or invalid authentication returns:

```json
{
  "detail": "unauthorized"
}
```

## Supported Agents

### Shell Company Screening Agent

Agent ID:

```text
shell-company-screening
```

This agent identifies, screens, and evaluates listed shell companies as potential candidates for reverse mergers, reverse takeovers, and related M&A transactions.

### Due Diligence Agent

Agent ID:

```text
due-diligence-agent
```

This agent performs structured company due diligence using external research, source collection, evidence synthesis, and report generation.

## Environment Variables

### Required for the current CommonStack deployment

```text
X_SERVICE_TOKEN
OPENAI_API_KEY
OPENAI_BASE_URL
RESEARCH_MODEL
```

Purpose:

```text
X_SERVICE_TOKEN
    Authenticates requests from ATL to this service.

OPENAI_API_KEY
    ATL-supplied CommonStack API key.

OPENAI_BASE_URL
    ATL-supplied CommonStack OpenAI-compatible base URL.

RESEARCH_MODEL
    Research model used by the service.
```

The currently tested model is:

```text
openai/gpt-5.5
```

Do not commit the real values of:

```text
X_SERVICE_TOKEN
OPENAI_API_KEY
OPENAI_BASE_URL
```

`RESEARCH_MODEL` is not secret and may be stored in deployment configuration.

### Optional provider and runtime variables

```text
RESEARCH_PROVIDER
OPENROUTER_API_KEY
GEMINI_API_KEY
PERPLEXITY_API_KEY
SQLITE_PATH
```

The default research provider is:

```text
openai
```

## CommonStack Deep Research

The production deployment uses the OpenAI-compatible CommonStack gateway.

The current Deep Research path is:

```text
ATL
  ↓
FastAPI service
  ↓
OpenAI-compatible provider
  ↓
CommonStack
  ↓
openai/gpt-5.5
  ↓
web_search
  ↓
research report + evidence
```

When `OPENAI_BASE_URL` is configured, requests are routed through CommonStack rather than the default OpenAI endpoint.

For CommonStack:

```text
model = openai/gpt-5.5
tool  = web_search
```

CommonStack `/v1/responses` returns the completed response synchronously, so the provider processes the returned result directly.

For native OpenAI without `OPENAI_BASE_URL`, the existing background execution and polling path remains supported.

Alternative CommonStack research models can be selected by changing `RESEARCH_MODEL`, for example:

```text
openai/gpt-5.4-pro
anthropic/claude-opus-5-5
google/gemini-3.1-pro-preview
```

Only one `RESEARCH_MODEL` value is used at a time.

## Local Setup

Python 3.12 is required.

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Set the service token:

```bash
export X_SERVICE_TOKEN="<service-token>"
```

For CommonStack, configure the ATL-supplied credentials and model:

```bash
export OPENAI_API_KEY="<platform-supplied-commonstack-key>"
export OPENAI_BASE_URL="<platform-supplied-commonstack-base-url>"
export RESEARCH_MODEL="openai/gpt-5.5"
```

Optionally specify the provider:

```bash
export RESEARCH_PROVIDER="openai"
```

Start the service:

```bash
uvicorn service.app:app --host 0.0.0.0 --port 8000
```

The local service is then available at:

```text
http://127.0.0.1:8000
```

## Manifest

Example Shell Company Screening manifest request:

```bash
curl \
  "http://127.0.0.1:8000/manifest?agent_id=shell-company-screening" \
  -H "X-Service-Token: <service-token>"
```

Example Due Diligence manifest request:

```bash
curl \
  "http://127.0.0.1:8000/manifest?agent_id=due-diligence-agent" \
  -H "X-Service-Token: <service-token>"
```

An unknown `agent_id` returns HTTP 404.

## Creating a Run

Example Due Diligence request:

```bash
curl -X POST \
  "http://127.0.0.1:8000/runs" \
  -H "X-Service-Token: <service-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "due-diligence-agent",
    "settings": {
      "target_company": "Microsoft Corporation",
      "research_cutoff_date": "2026-09-25",
      "additional_context": "Integration test using public information."
    }
  }'
```

A valid request returns HTTP 202 and immediately provides a run ID while the research continues.

Example:

```json
{
  "run_id": "run_abc123",
  "status": "running",
  "created_at": "2026-09-25T00:00:00Z"
}
```

Invalid settings are rejected before research starts.

For example, missing required fields return HTTP 422.

## Run Status

Poll a run with:

```bash
curl \
  "http://127.0.0.1:8000/runs/<run_id>" \
  -H "X-Service-Token: <service-token>"
```

Possible states are:

```text
queued
running
completed
failed
```

A failed run may include a human-readable `error` field.

Example:

```json
{
  "run_id": "run_abc123",
  "status": "failed",
  "created_at": "2026-09-25T00:00:00Z",
  "error": "Research request failed."
}
```

## Run Result

After a run reaches `completed`, retrieve the result with:

```bash
curl \
  "http://127.0.0.1:8000/runs/<run_id>/result" \
  -H "X-Service-Token: <service-token>"
```

A completed v1.1 result has the following structure:

```json
{
  "run_id": "run_abc123",
  "status": "completed",
  "completed_at": "2026-09-25T00:10:00Z",
  "report_markdown": "# Research Report\n\n...",
  "usage": {
    "provider": "commonstack",
    "model": "openai/gpt-5.5",
    "input_tokens": 12345,
    "output_tokens": 678,
    "actual_cost_micro": null
  },
  "artifacts": {
    "docx": {
      "filename": "report.docx",
      "content_base64": "..."
    }
  },
  "evidence": {
    "provider": "openai",
    "citations": [],
    "sources": [],
    "metadata": {}
  }
}
```

`report_markdown` and `evidence` are required.

DOCX and PDF artifacts are optional.

Result retrieval is repeatable.

Requesting `/result` before completion returns HTTP 409.

## Usage Reporting

ATL contract v1.1 requires completed results to include:

```text
provider
model
input_tokens
output_tokens
actual_cost_micro
```

When requests are routed through `OPENAI_BASE_URL`, the reported provider is:

```text
commonstack
```

Model and token usage are extracted from the provider response when available.

The current verified CommonStack response exposes:

```text
model
input_tokens
output_tokens
```

`actual_cost_micro` represents actual research cost in micro-credits:

```text
$1 = 1 credit = 1,000,000 micro
```

If the gateway exposes a per-request cost field, the service normalizes it into `actual_cost_micro`.

If CommonStack does not expose a recognizable per-request cost field in the response, `actual_cost_micro` may be `null` even when token usage is available.

This does not prevent the research run from completing.

## Evidence

Each research result includes structured evidence derived from the underlying provider result.

The evidence payload may contain:

```text
provider
citations
sources
metadata
research steps
usage metadata
```

The exact evidence available depends on the provider response.

## Output Files

Each research run may generate:

```text
Markdown report
DOCX report
PDF report
Evidence JSON
```

Markdown and evidence JSON are required.

DOCX and PDF are optional.

Binary artifacts returned through the HTTP API are base64 encoded.

Each returned binary artifact is limited to 5 MB.

PDF generation may be unavailable in some Linux environments because the original PDF conversion path can depend on Microsoft Word. PDF generation failure must not cause the research run itself to fail.

## Background Execution

`POST /runs` does not wait for the complete research workflow.

The service lifecycle is:

```text
POST /runs
    ↓
create run
    ↓
running
    ↓
background Python thread
    ↓
run_agent()
    ↓
Deep Research
    ↓
save_report()
    ↓
completed / failed
    ↓
GET /runs/{run_id}/result
```

Research failures are caught and persisted as:

```text
failed
```

with a human-readable error message.

## Persistence

Run state and completed results are stored in SQLite.

The default database path is:

```text
data/atl_runs.db
```

The current Render deployment uses the Free web service tier.

The local filesystem on the Free deployment should not be treated as durable long-term storage. SQLite data may be lost when the service is restarted, redeployed, or otherwise recreated.

ATL therefore acts as the long-term store for completed research results.

The platform-side sweeper periodically checks active runs through:

```text
GET /runs/{run_id}
```

When a run becomes `completed`, ATL retrieves:

```text
GET /runs/{run_id}/result
```

and stores the completed result in the ATL platform database.

A small loss window may still exist if the Render service is restarted after a run completes but before ATL retrieves the result.

A persistent database such as Turso or a persistent Render disk can be introduced later if stronger durability is required.

## Authentication

All API requests must include:

```text
X-Service-Token
```

The supplied value is compared against:

```text
X_SERVICE_TOKEN
```

Secrets must never be logged, echoed, or committed.

The service also attempts to redact configured provider credentials and the CommonStack base URL from captured runtime errors.

## Render Deployment

The repository includes:

```text
render.yaml
.python-version
```

`.python-version` pins Python 3.12.

The current `render.yaml` uses:

```yaml
services:
  - type: web
    name: atl-research-service
    runtime: python
    plan: free

    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn service.app:app --host 0.0.0.0 --port $PORT

    envVars:
      - key: X_SERVICE_TOKEN
        sync: false

      - key: OPENAI_API_KEY
        sync: false

      - key: OPENAI_BASE_URL
        sync: false

      - key: RESEARCH_MODEL
        value: openai/gpt-5.5
```

The following values must be configured securely in Render:

```text
X_SERVICE_TOKEN
OPENAI_API_KEY
OPENAI_BASE_URL
```

For the ATL CommonStack deployment:

```text
OPENAI_API_KEY  = ATL-supplied CommonStack key
OPENAI_BASE_URL = ATL-supplied CommonStack base URL
RESEARCH_MODEL  = openai/gpt-5.5
```

Do not store secret values in:

```text
render.yaml
README.md
Git history
source code
.env files committed to Git
```

The Render service starts with:

```bash
uvicorn service.app:app --host 0.0.0.0 --port $PORT
```

Current deployed service:

```text
https://atl-research-service.onrender.com
```

The ATL platform requires the service base URL together with the matching `X-Service-Token`.

## Verification

Before delivery, verify the four endpoint patterns for both agent IDs:

```text
GET /manifest
POST /runs
GET /runs/{run_id}
GET /runs/{run_id}/result
```

Authentication verification should include:

```text
correct token → HTTP 200 / 202
incorrect token → HTTP 401
unknown agent → HTTP 404
invalid run settings → HTTP 422
```

A real CommonStack end-to-end research run must also be completed for each agent:

```text
shell-company-screening
due-diligence-agent
```

Both agents have been successfully verified against:

```text
provider: commonstack
model:    openai/gpt-5.5
tool:     web_search
```

The verified workflow is:

```text
POST /runs
→ running
→ CommonStack Deep Research
→ completed
→ GET /result
```

The current CommonStack responses successfully expose token usage.

Per-request `actual_cost_micro` is currently left null when no recognizable cost field is present in the gateway response.

## E2E Test Fixtures

Real end-to-end Markdown reports and evidence JSON files are retained under:

```text
tests/fixtures/e2e/
├── due_diligence/
│   ├── due-diligence-report.md
│   └── due-diligence-evidence.json
└── shell_company_screening/
    ├── shell-company-screening-report.md
    └── shell-company-screening-evidence.json
```

These fixtures were produced by real CommonStack Deep Research runs and are retained as integration evidence.

They must not contain API keys, service tokens, or other deployment secrets.

## Security

Never commit:

```text
CommonStack API keys
CommonStack base URL
X-Service-Token
other provider API keys
.env files containing secrets
```

Runtime-generated SQLite databases and temporary output directories should remain excluded through `.gitignore`.

Before committing generated reports or evidence fixtures, verify that they contain no private credentials or sensitive deployment information.

## Current Integration Status

The following integration steps have been completed:

```text
✓ Both manifests exposed
✓ X-Service-Token authentication
✓ POST /runs validation
✓ SQLite run persistence
✓ Background execution
✓ Run status endpoint
✓ Result endpoint
✓ CommonStack OPENAI_BASE_URL support
✓ openai/gpt-5.5 model override
✓ CommonStack web_search support
✓ Synchronous /v1/responses compatibility
✓ v1.1 provider/model/token usage reporting
✓ Render Free deployment
✓ Due Diligence real E2E completed
✓ Shell Company Screening real E2E completed
✓ Markdown and evidence fixtures retained
```

Known caveat:

```text
actual_cost_micro may be null because the current CommonStack
response does not expose a recognized per-request cost field.
```

This does not block research execution or result delivery.