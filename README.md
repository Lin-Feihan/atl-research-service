# ATL Research Service

HTTP service for exposing two Deep Research agents to Agentic Trading Lab (ATL):

- `shell-company-screening`
- `due-diligence-agent`

The service uses FastAPI, background research threads, and SQLite persistence. It implements the ATL Research Agent integration contract, including the v1.1 usage reporting requirements.

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

Requests with a missing or invalid service token return HTTP `401`.

## Supported Agents

### Shell Company Screening Agent

Agent ID:

```text
shell-company-screening
```

The agent identifies, screens, and evaluates listed shell companies as potential candidates for reverse mergers, reverse takeovers, and other M&A transactions.

### Due Diligence Agent

Agent ID:

```text
due-diligence-agent
```

The agent conducts company due diligence, including DD planning, key due diligence workstreams, risk assessment, valuation impact, and report generation.

## Environment Variables

### Required

```text
X_SERVICE_TOKEN
OPENAI_API_KEY
OPENAI_BASE_URL
```

`X_SERVICE_TOKEN` authenticates requests from ATL to this service.

`OPENAI_API_KEY` and `OPENAI_BASE_URL` are supplied by the ATL platform for its CommonStack OpenAI-compatible gateway.

Do not commit any secret values to this repository.

### Optional

```text
SQLITE_PATH
RESEARCH_PROVIDER
RESEARCH_MODEL
OPENROUTER_API_KEY
GEMINI_API_KEY
PERPLEXITY_API_KEY
```

The default research provider is `openai`.

When `OPENAI_BASE_URL` is configured, the OpenAI-compatible provider sends requests through the configured gateway instead of the default OpenAI endpoint.

## Local Setup

Python 3.12 is required.

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Set the service token and platform-supplied CommonStack credentials:

```bash
export X_SERVICE_TOKEN="<service-token>"
export OPENAI_API_KEY="<platform-supplied-commonstack-key>"
export OPENAI_BASE_URL="<platform-supplied-commonstack-base-url>"
```

Start the service:

```bash
uvicorn service.app:app --host 0.0.0.0 --port 8000
```

The local service will be available at:

```text
http://127.0.0.1:8000
```

## Manifest

Example request:

```bash
curl \
  "http://127.0.0.1:8000/manifest?agent_id=shell-company-screening" \
  -H "X-Service-Token: <service-token>"
```

For the Due Diligence Agent:

```bash
curl \
  "http://127.0.0.1:8000/manifest?agent_id=due-diligence-agent" \
  -H "X-Service-Token: <service-token>"
```

## Run Lifecycle

Create a research run with:

```text
POST /runs
```

Example request:

```json
{
  "agent_id": "due-diligence-agent",
  "settings": {
    "target_company": "Example Company",
    "research_cutoff_date": "2026-09-25",
    "additional_context": "Optional transaction context."
  }
}
```

A successful request immediately returns a unique run ID while the research continues in a background thread:

```json
{
  "run_id": "run_example123",
  "status": "running",
  "created_at": "2026-09-25T00:00:00Z"
}
```

Poll the run status with:

```text
GET /runs/{run_id}
```

Possible states are:

```text
queued
running
completed
failed
```

A failed run may also include a human-readable `error` field.

After the run is completed, retrieve the result with:

```text
GET /runs/{run_id}/result
```

## Result Format

A completed result contains:

- Markdown research report
- Usage information
- Evidence data
- DOCX artifact when available
- PDF artifact when available

Example structure:

```json
{
  "run_id": "run_example123",
  "status": "completed",
  "completed_at": "2026-09-25T00:10:00Z",
  "report_markdown": "# Research Report",
  "usage": {
    "provider": "commonstack",
    "model": "example-model",
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
    "provider": "openai",
    "citations": [],
    "sources": [],
    "metadata": {}
  }
}
```

## Usage Reporting

The ATL v1.1 contract requires each completed research result to include a `usage` object.

The service reports:

```text
provider
model
input_tokens
output_tokens
actual_cost_micro
```

When the OpenAI-compatible provider is routed through CommonStack, the reported provider is `commonstack`.

Token usage and model information are taken from the provider response when available.

`actual_cost_micro` represents the real research cost in micro-credits:

```text
$1 = 1 credit = 1,000,000 micro
```

The platform uses this information for user credit settlement.

## Persistence

Run state, settings, status, errors, and completed results are persisted in SQLite.

The default local database path is:

```text
data/atl_runs.db
```

A custom location can be configured through:

```text
SQLITE_PATH
```

For Render deployment, the intended persistent database path is:

```text
/var/data/atl_runs.db
```

## Output Files

Each research run uses its own output directory.

Markdown and evidence JSON are required outputs.

DOCX and PDF are optional.

PDF generation may be unavailable on Linux because the original PDF conversion path depends on Microsoft Word. Failure to generate PDF must not cause the research run itself to fail.

Binary artifacts returned by the API are Base64 encoded and limited to 5 MB each.

## Authentication and Secrets

The service never intentionally logs or returns API keys, service tokens, or the configured CommonStack base URL.

The following values must be kept outside GitHub:

```text
X_SERVICE_TOKEN
OPENAI_API_KEY
OPENAI_BASE_URL
```

They should be configured through environment variables locally and through secret environment variables on Render.

## Render Deployment

The repository includes:

```text
render.yaml
.python-version
```

The service uses Python 3.12.

Render installs dependencies with:

```bash
pip install -r requirements.txt
```

The service starts with:

```bash
uvicorn service.app:app --host 0.0.0.0 --port $PORT
```

Configure the following environment variables in Render:

```text
X_SERVICE_TOKEN
OPENAI_API_KEY
OPENAI_BASE_URL
```

For persistent SQLite storage, the deployment configuration uses:

```text
SQLITE_PATH=/var/data/atl_runs.db
```

with `/var/data` mounted as persistent storage.

Never place real credentials directly in `render.yaml` or any committed source file.

## Verification

The HTTP lifecycle should be verified for both agent IDs:

```text
GET /manifest
POST /runs
GET /runs/{run_id}
GET /runs/{run_id}/result
```

At least one real end-to-end research run should be completed for each agent using the platform-supplied CommonStack credentials.

The final verification should confirm:

- Manifest retrieval succeeds
- Invalid authentication returns `401`
- Required-field validation returns `422`
- Research runs execute in the background
- Run status reaches `completed` or reports a readable failure
- Markdown report is non-empty
- Evidence data is present
- Usage information is present
- Available binary artifacts decode correctly
- Completed results can be retrieved repeatedly
- Persisted runs remain queryable after service restart