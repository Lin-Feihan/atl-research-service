# ATL Research Service

HTTP service for exposing two Deep Research agents to Agentic Trading Lab (ATL):

- `shell-company-screening`
- `due-diligence-agent`

The service uses FastAPI, background research threads, and SQLite for run state. It implements the ATL Research Agent integration contract, including CommonStack support and v1.1 usage reporting.

## API

The service exposes four authenticated endpoint patterns:

- `GET /manifest?agent_id=...`
- `POST /runs`
- `GET /runs/{run_id}`
- `GET /runs/{run_id}/result`

Every request must include:

```text
X-Service-Token: <service-token>
```

## Supported Agents

### Shell Company Screening Agent

Agent ID:

```text
shell-company-screening
```

### Due Diligence Agent

Agent ID:

```text
due-diligence-agent
```

## Environment Variables

Required:

```text
X_SERVICE_TOKEN
OPENAI_API_KEY
OPENAI_BASE_URL
```

`X_SERVICE_TOKEN` authenticates requests from ATL to this service.

`OPENAI_API_KEY` and `OPENAI_BASE_URL` are supplied by the ATL platform for the CommonStack OpenAI-compatible gateway.

Do not commit any of these values to the repository.

Optional provider and runtime variables:

```text
RESEARCH_PROVIDER
RESEARCH_MODEL
OPENROUTER_API_KEY
GEMINI_API_KEY
PERPLEXITY_API_KEY
SQLITE_PATH
```

The default research provider is `openai`.

When `OPENAI_BASE_URL` is configured, the OpenAI-compatible provider sends requests through the configured gateway instead of the default OpenAI endpoint.

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

For a real CommonStack research run, also set the platform-supplied credentials:

```bash
export OPENAI_API_KEY="<platform-supplied-commonstack-key>"
export OPENAI_BASE_URL="<platform-supplied-commonstack-base-url>"
```

Optionally specify the research provider:

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

Example:

```bash
curl -X POST \
  "http://127.0.0.1:8000/runs" \
  -H "X-Service-Token: <service-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "due-diligence-agent",
    "settings": {
      "target_company": "Microsoft",
      "research_cutoff_date": "2026-09-25",
      "additional_context": "Integration test using public information."
    }
  }'
```

A successful request immediately returns a unique `run_id` while the research continues in a background thread.

Example response:

```json
{
  "run_id": "run_abc123",
  "status": "running",
  "created_at": "2026-09-25T00:00:00Z"
}
```

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

A failed run may also include a human-readable `error` field.

## Run Result

After a run reaches `completed`, retrieve the result with:

```bash
curl \
  "http://127.0.0.1:8000/runs/<run_id>/result" \
  -H "X-Service-Token: <service-token>"
```

The v1.1 response includes:

```json
{
  "run_id": "run_abc123",
  "status": "completed",
  "completed_at": "2026-09-25T00:10:00Z",
  "report_markdown": "# Research Report\n\n...",
  "usage": {
    "provider": "commonstack",
    "model": "...",
    "input_tokens": 12345,
    "output_tokens": 678,
    "actual_cost_micro": 850000
  },
  "artifacts": {
    "docx": {
      "filename": "report.docx",
      "content_base64": "..."
    }
  },
  "evidence": {
    "provider": "...",
    "citations": [],
    "sources": [],
    "metadata": {}
  }
}
```

`report_markdown` and `evidence` are required.

DOCX and PDF artifacts are optional.

Result reads are repeatable.

## Usage Reporting

ATL contract v1.1 requires each completed result to include a `usage` object.

The service reports:

```text
provider
model
input_tokens
output_tokens
actual_cost_micro
```

When the OpenAI-compatible provider is routed through `OPENAI_BASE_URL`, the provider is reported as:

```text
commonstack
```

Token usage and model information are taken from the provider response when available.

`actual_cost_micro` represents the real research cost in micro-credits:

```text
$1 = 1 credit = 1,000,000 micro
```

The exact CommonStack cost field is captured from the provider response when available.

## Persistence

Run state and completed results are stored in SQLite.

The default database path is:

```text
data/atl_runs.db
```

The current Render deployment uses the Free web service tier.

Render Free uses an ephemeral local filesystem, so the local SQLite database may be lost if the service spins down, restarts, or is redeployed.

ATL retrieves completed research results from this service and stores them in the platform database.

The platform-side sweeper periodically polls active runs through:

```text
GET /runs/{run_id}
```

When a run reaches `completed`, ATL retrieves the result and stores it in the platform database.

Because ATL stores the completed result after retrieval, long-term persistence of completed reports is handled by the platform rather than by this service.

A small theoretical loss window remains if the Render service is restarted before ATL retrieves a newly completed result.

For stronger persistence in the future, the SQLite storage layer can be migrated to a persistent datastore such as Turso or a Render persistent disk.

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

PDF generation may be unavailable on Linux because the original PDF conversion path depends on Microsoft Word. Failure to generate a PDF must not cause the research run itself to fail.

Binary artifacts returned through the HTTP API are base64 encoded.

Each binary artifact is limited to 5 MB.

## Authentication

All API requests must include:

```text
X-Service-Token
```

The supplied token is compared against:

```text
X_SERVICE_TOKEN
```

Missing or invalid authentication returns:

```json
{
  "detail": "unauthorized"
}
```

Secrets must never be logged, echoed, or committed to GitHub.

The service also redacts configured provider credentials and the CommonStack base URL from captured runtime errors.

## Background Execution

Research jobs run in background threads.

`POST /runs` does not wait for Deep Research to finish.

The lifecycle is:

```text
POST /runs
    ↓
running
    ↓
background research thread
    ↓
run_agent()
    ↓
save_report()
    ↓
completed / failed
    ↓
GET /runs/{run_id}/result
```

Research failures are captured and persisted as:

```text
failed
```

with a human-readable error message.

## Render Deployment

The repository includes:

```text
render.yaml
.python-version
```

`.python-version` pins the service to Python 3.12.

The current Render Blueprint uses the Free web service tier.

Deploy the repository as a Render Blueprint.

During deployment, configure these secret environment variables:

```text
X_SERVICE_TOKEN
OPENAI_API_KEY
OPENAI_BASE_URL
```

Use:

```text
OPENAI_API_KEY = ATL-supplied CommonStack key
OPENAI_BASE_URL = ATL-supplied CommonStack base URL
```

Do not store their real values in:

```text
render.yaml
README.md
Git history
source code
```

The Render service starts with:

```bash
uvicorn service.app:app --host 0.0.0.0 --port $PORT
```

After deployment, Render provides a public HTTPS base URL such as:

```text
https://atl-research-service.onrender.com
```

This base URL, together with the `X-Service-Token`, is delivered to the ATL platform team.

## Verification

Before final delivery, verify all four endpoint patterns for both agent IDs:

```text
GET /manifest
POST /runs
GET /runs/{run_id}
GET /runs/{run_id}/result
```

At least one real end-to-end CommonStack research run should be completed for each agent:

```text
shell-company-screening
due-diligence-agent
```

For each real verification run, retain the produced Markdown report and evidence JSON as test fixtures.

The real CommonStack runs should also be used to verify the v1.1 usage fields, especially:

```text
model
input_tokens
output_tokens
actual_cost_micro
```

## Security

Never commit:

```text
CommonStack API keys
CommonStack base URL
X-Service-Token
other provider API keys
.env files
generated private reports
```

Local runtime outputs and SQLite data should remain excluded through `.gitignore`.