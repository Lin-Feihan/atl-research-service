# Default Settings

This document defines the input settings for a public-source corporate due diligence task.

## Settings

| Field ID | Setting | Type | Required Input | Description |
|---|---|---|---|---|
| `target_company` | Target Company | Text | Yes | Name of the company to be investigated. The input may include a ticker, website, jurisdiction, or other identifying information when needed to distinguish the target company. |
| `research_cutoff_date` | Research Cut-off Date | Date | Yes | Latest date up to which information may be considered in the due diligence research. |
| `additional_context` | Additional Context | Long text | No | Optional background, transaction context, specific concerns, focus areas, or other information that may help the agent interpret the due diligence task. |
