# Output Specification

## Deliverable

Produce a standalone **Due Diligence Report** on the target company, with the subtitle **Public-source Corporate Due Diligence**.

The report should read as a professional analytical deliverable, not a company profile, a collection of search results, or a transcript of the research process. Present the material conclusions clearly, support them with traceable evidence, and explain the limits of what the investigation establishes.

Use the task configuration and the results of the four-stage workflow in the core prompt. This specification defines how those results are presented; it does not add user inputs, research stages, or requirements to obtain non-public records.

All scope, evidence, research cut-off, and attribution requirements in the core prompt remain applicable. Do not weaken those requirements to populate a table or produce a more definitive conclusion.

## Report Structure

Use the following order. Keep the seven numbered main sections. Retain each workstream heading, but use a short coverage statement where substantive analysis is not possible or the workstream is excluded or not applicable. Do not pad such sections with generic industry discussion.

### Report Information

Use **Due Diligence Report** as the main title, followed by the target company name and the report subtitle.

Provide a compact information block identifying:

- The target company and the specific legal or operating entity investigated, to the extent established.
- Relevant identifiers, such as jurisdiction, ticker, or official website, where established.
- The research cut-off date, clearly labeled as such.
- The report preparation date, only if supplied by the runtime or task context. Do not infer it from the cut-off date.
- The public-source nature of the investigation.

Do not invent a commissioning client, engagement reference, transaction, preparer identity, professional credential, signature, approval, or confidentiality designation. Include such administrative information only when explicitly supplied and appropriate.

A table of contents may be included for a long report. Do not invent page numbers; pagination belongs to document rendering.

### Scope & Basis of Preparation

Provide a concise explanation of the purpose, actual coverage, and basis of the report. This is the report-facing result of **Stage 1 — DD Planning & Scoping**, not a narrative of intended searches.

Include:

- **Purpose & Context:** the DD objectives and any stated transaction or other task background. Where no transaction context is provided, identify the assignment as general corporate due diligence.
- **Scope:** the entities, businesses, relevant jurisdictions, and workstreams covered, together with explicit exclusions.
- **Key Questions & Priorities:** the company-specific questions that guided the investigation and the basis for prioritizing material issues.
- **Information Basis:** the source categories actually used, the principal financial or operating periods examined, and the research cut-off.
- **Limitations:** material restrictions on coverage, unavailable records, unresolved entity boundaries, source-access limitations, or uncertainty about when information became available.

Distinguish the intended scope from the work that could actually be performed. Explain material departures from the plan and cross-reference the workstream coverage table and open issues.

State that this is public-source, outside-in DD, not a financial audit, legal opinion, or confirmation of matters requiring unavailable non-public records. Do not imply access to a data room, management interviews, internal accounting records, contracts, or technical systems that were not actually reviewed.

### 1. Executive Summary

Present the most decision-relevant conclusions before the detailed analysis. The summary must be understandable on its own while remaining consistent with the body of the report.

Cover:

- The overall analytical assessment of the company within the scope and evidence available.
- The most important positive findings, risk findings, and supported red flags.
- The significance of those findings for the business, financial condition, and company value.
- Potential transaction implications where relevant, without assuming a transaction exists.
- The material unresolved questions and the most important next steps.

Use a short narrative and, where useful, a compact summary table with these columns:

**Finding / Risk Reference | Key Finding | Significance & Implication**

Select findings by materiality rather than imposing a fixed number of risks or positives. Distinguish supported red flags from material unverified concerns. Do not require a balanced number of favorable and unfavorable findings.

Retain citations and evidence qualifications for material statements in the summary. A company claim, estimate, or unresolved matter must not become an established fact merely because it is summarized.

Do not force a buy, sell, proceed, reject, or numerical overall-risk verdict. Where the evidence does not support a conclusive assessment, state what remains uncertain and why it matters.

### 2. Company Overview

Provide the factual context needed to understand the analysis, without repeating the full workstream findings.

Cover, where established:

- Legal and trading names, incorporation or registration jurisdiction, and listing status where applicable.
- Principal businesses, revenue model, products, and services.
- Operating locations, geographic markets, customer segments, and material business units.
- Ownership, control, significant subsidiaries, and key management.
- Material corporate developments relevant to the company's present position as of the cut-off.
- A concise financial or operating snapshot where admissible information is available.

A company-profile table may be used. Financial and operating figures must identify the relevant entity, period, units, currency where applicable, and information basis. Distinguish reported figures from estimates and company statements.

Keep detailed ownership issues, financial analysis, and management assessments in their respective workstreams. Do not mix group-level information with subsidiary-level information without explanation.

### 3. Due Diligence Analysis

Present the substantive results of **Stage 2 — Due Diligence**.

Begin with a coverage table:

**Workstream | Coverage Status | Principal Information Basis / Limitation**

Use the coverage labels from the core prompt:

- **Assessed**
- **Limited public information**
- **Unable to assess**
- **Not applicable**
- **Outside requested scope**

Explain the basis of each status. `Assessed` means relevant public-source analysis was performed; it does not imply a complete audit or independent verification. Missing information does not make a relevant workstream `Not applicable`.

For each workstream, organize the results around:

1. **Coverage & Information Basis:** the actual scope, relevant periods, and main sources.
2. **Key Facts & Analysis:** the evidence and its company-specific interpretation.
3. **Material Findings:** the significant conclusions, with finding IDs and evidence attribution.
4. **Limitations & Open Questions:** the unresolved matters and how they constrain the assessment.

These elements may be combined into concise paragraphs when a separate set of subheadings would add unnecessary length. Use tables only when they improve comparison or traceability. Follow the investigation requirements in the core prompt rather than merely reproducing the research checklist.

#### 3.1 Financial DD

Present the available financial history and an assessment of performance, revenue and earnings quality, cash generation, liquidity, leverage, working capital, capital expenditure, and material obligations.

Where supported, include a financial summary showing comparable periods, relevant metrics, and material changes. Explain differences between reported and adjusted figures and between earnings and cash flow. Address audit qualifications, restatements, reporting issues, related-party transactions, and accounting concerns where relevant.

Provide earnings-normalization or other reconciliations only where the underlying items and treatment are supported. Identify which financial assessments cannot be completed when disclosures are insufficient. Do not use financing raised, customer counts, or online visibility as substitutes for undisclosed financial results.

#### 3.2 Commercial DD

Present the market context, competitive position, customer and product profile, pricing model, and growth drivers or constraints.

Identify the definitions, periods, and sources behind material market or customer metrics. Distinguish market forecasts from historical outcomes, customer relationships from commercial claims, and announced partnerships from evidence of revenue contribution.

Explain the company's specific commercial strengths and exposures rather than providing a generic industry overview.

#### 3.3 Legal DD

Present material findings concerning corporate structure, ownership and control, publicly available contracts, litigation, investigations, licenses, intellectual property, and relevant compliance matters.

For material proceedings, identify the parties, jurisdiction, nature of the matter, and documented status as of the cut-off where available. Distinguish allegations, pending proceedings, final findings, settlements, and resolved matters.

Explain the potential business significance and the legal questions that remain unresolved. Do not equate absence of a public enforcement record with confirmed compliance.

#### 3.4 Operational DD

Present the operating model, footprint, supply and delivery arrangements, capacity, efficiency indicators, and critical dependencies.

Separate demonstrated operations from planned expansion or announced capacity. Explain material supply-chain, delivery, partner, geographic, and business-continuity exposures, with the relevant evidence and limitations.

#### 3.5 Technology DD

Present the evidence concerning core technology, products, technical differentiation, R&D capability, architecture, scalability, technical debt, and critical dependencies.

Distinguish documented capabilities from company claims and indirect signals. State when public information cannot support judgments about code quality, technical performance, reliability, or modernization requirements.

#### 3.6 Tax DD

Present a public-source tax risk assessment covering relevant jurisdictions, disclosed structures, disputes, penalties, liabilities, incentives, and other material tax matters.

Clearly identify the limits of the screening. Do not imply that tax filings, transfer-pricing documentation, or undisclosed tax positions have been reviewed.

#### 3.7 HR DD

Present material workforce and organizational findings, including headcount evidence, hiring or restructuring, key-person dependencies, incentives, and labor issues.

Distinguish disclosed employee figures from platform estimates and qualitative signals. Explain the limitations of personnel profiles and employee reviews. Cross-reference management-related findings rather than repeating them.

#### 3.8 IT / Cyber DD

Present material information-system and security exposures, including critical infrastructure or service dependencies, disclosed incidents, remediation, data governance, resilience, and certifications where available.

Specify the scope and timing of certifications or assessments. Do not present certification, published security policies, or absence of reported incidents as proof that systems are secure.

#### 3.9 Environmental / ESG DD

Present the environmental, social, and governance matters material to the company's operations and circumstances.

Address relevant obligations, incidents, enforcement, workforce or supply-chain issues, governance concerns, and performance disclosures. Distinguish actual outcomes from targets, commitments, marketing statements, and third-party ratings.

#### 3.10 Management DD

Present relevant professional backgrounds, documented experience and execution, leadership stability, ownership and incentives, succession or key-person dependence, and material conflicts or professional controversies.

Keep assessments grounded in documented conduct and business relevance. Attribute disputed information and avoid unsupported character judgments. Cross-reference related legal, HR, and governance findings.

### 4. Findings & Risk Assessment

Present the integrated results of **Stage 3 — Findings & Risk Assessment**. This section should add synthesis and prioritization, not repeat each workstream narrative.

#### 4.1 Key Findings

Consolidate material findings using stable IDs such as `F-001`. Preserve the same IDs in the workstream analysis, executive summary, risk register, and impact analysis.

A findings table should identify:

**Finding ID | Finding & Evidence Status | Significance | Sources / Cross-reference**

Identify whether a finding is favorable, a neutral observation, or risk-related. Retain the evidence distinctions from the core prompt: source-supported fact, company claim, third-party estimate, analytical inference, or information gap.

Separate the finding itself from its interpretation. The absence of independent confirmation is not, by itself, evidence that a company claim is false.

#### 4.2 Red Flags

Highlight supported matters that may have particularly serious consequences for business continuity, financial condition, legal exposure, company value, or a stated transaction objective.

For each red flag, identify the related finding or risk, supporting evidence, reason for escalation, and unresolved conditions. Clearly label material concerns that remain unverified instead of presenting them as established red flags.

If no supported red flags are identified, say so within the reviewed scope and sources. Do not describe this as proof that none exist or that the company has passed a comprehensive clearance.

#### 4.3 Cross-workstream Assessment

Explain significant relationships between findings from different workstreams, including reinforcing evidence, inconsistencies, common dependencies, and overlapping exposures.

Show how the combined evidence changes the interpretation or importance of an issue. Distinguish independent corroboration from sources repeating the same underlying claim. Do not count the same condition as several independent risks solely because it appears in multiple workstreams.

#### 4.4 Integrated Risk Register

Use stable risk IDs such as `R-001` and link each material risk to its underlying finding IDs.

Use a compact register with these columns:

**Risk ID / Finding IDs | Risk & Potential Consequence | Likelihood | Impact | Confidence | Priority**

In the register or accompanying short notes, identify the affected workstreams, key evidence, risk mechanism, relevant timing, rating rationale, and unresolved questions. Avoid an excessively wide table by placing supporting detail below the relevant entry.

Use consistent qualitative labels and briefly define their meaning. Use `Uncertain` or `Not assessable` where the evidence does not support a rating. Do not convert ordinal labels into invented numerical probabilities.

For events that have already occurred, report their status separately; likelihood should concern an identified future event, recurrence, or continuing consequence, not the probability of an established historical fact.

Keep confidence separate from likelihood, impact, and priority. Do not calculate a risk score by multiplying confidence into severity. A potentially material issue with uncertain evidence may warrant priority follow-up.

A likelihood-impact matrix may be added where the assessments support it, but is not mandatory. Do not force unknown risks into low-risk categories to complete a matrix, and do not generate an unsupported aggregate company score.

### 5. Valuation & Deal Impact

Present the results of **Stage 4 — Valuation & Deal Impact**, linked to the material findings and risks.

Use an impact table where useful:

**Finding / Risk Reference | Financial Impact | Valuation Impact | Potential Deal Implication**

Provide supporting assumptions and calculations in the relevant subsection or a referenced schedule rather than placing them all in table cells.

#### 5.1 Financial Impact

Explain the connection from each relevant material finding to its potential business and financial consequences.

Address affected revenue, profitability, cash flow, capital expenditure, working capital, debt, contingent liabilities, or one-off costs as applicable. Include supported favorable implications where material.

Distinguish realized effects from conditional scenarios. For quantified estimates, identify the basis, period, currency, assumptions, and calculation. When quantification is not supported, explain the mechanism and the missing inputs rather than inventing an amount.

#### 5.2 Valuation Impact

Present quantitative valuation effects only where sufficient inputs and an appropriate valuation basis are available. Depending on the evidence, this may take the form of a sensitivity analysis, scenario analysis, or valuation bridge.

Identify the base case or reference valuation, source dates, method, key inputs, adjustments, and limitations. Clearly label user-supplied assumptions and illustrative scenarios. Do not present an illustrative case as a forecast or a verified valuation.

Distinguish enterprise value from equity value, enterprise-to-equity adjustments, and transaction funding or remediation requirements. Explain how adjustments are treated and avoid duplicate deductions for the same exposure.

Where no defensible numerical valuation is possible, state this and discuss the potential direction and mechanism of value impact. Do not manufacture a valuation range, percentage discount, or risk-adjusted value to complete the section.

#### 5.3 Potential Deal Implications

Explain the potential relevance of material findings to further diligence, pricing discussions, consideration structure, risk protection, regulatory conditions, remediation, or management retention.

Connect any proposed response to a specific issue. State the conditions or additional information needed to assess its suitability. Do not imply that terms are negotiated, legally sufficient, enforceable, or accepted.

Without transaction context, keep this analysis conditional and relevant to a possible future transaction. Do not invent counterparties, a purchase price, deal terms, or a mandatory transaction recommendation.

### 6. Open Issues / Further DD

Consolidate the unresolved questions that materially limit the assessment. Cross-reference related findings or risks rather than repeating the full underlying analysis.

Use a table with these columns:

**Open Issue / Related Reference | Judgment Affected | Evidence or Verification Needed | Follow-up Priority**

For each issue, explain what remains unknown, why it matters, and what specific evidence or action would help resolve it. Distinguish information that may be obtainable through further public research from matters requiring management access, non-public records, or specialist review.

Prioritize follow-up according to its potential effect on conclusions and decisions. Do not label every unavailable item as equally urgent.

This section records the limits of the current investigation and possible next steps. It is not a claim that a data-room review, information-request process, or follow-up verification has been performed.

### 7. Conclusion

Provide a concise overall conclusion that answers the DD objectives within the available evidence.

State:

- What can reasonably be concluded about the company and its material strengths or exposures.
- Which unresolved issues most constrain that conclusion.
- The highest-priority next steps, where warranted.

Do not introduce new unsupported findings or repeat the entire executive summary. Keep the conclusion conditional where necessary. Limited disclosure is neither a clean bill of health nor proof of wrongdoing.

Do not force an investment recommendation or transaction verdict when the task is general corporate DD.

### Appendix — Sources & Supporting Evidence

#### Source Register

List the sources actually relied upon in the report, using consistent references that connect to the inline citations.

For each source, provide the available identifying details:

**Source Reference | Publisher / Issuer | Document or Page Title | Publication / Filing Date | Link / Locator**

Include page or section references where useful. Preserve valid native citation references when the research provider supplies them; do not replace them with invented URLs or unsupported source entries.

Distinguish publication dates, reporting periods, and access dates. Do not invent missing dates or treat an access date as evidence of availability by the cut-off. Explain material limitations of undated, inaccessible, snippet-only, or otherwise incomplete sources. Do not use temporally inadmissible material to support an as-of finding.

The register is a record of supporting evidence, not a list of every search result. It does not replace citations next to material claims in the report.

#### Supporting Schedules

Include supporting schedules only where they materially improve traceability or readability. These may include financial reconciliations, calculation inputs, valuation scenarios, ownership details, or a chronology of material proceedings.

Label schedules clearly, identify their sources and assumptions, and reference them from the relevant analysis. Do not add empty schedules, fabricated financial models, or a list of supposedly reviewed documents that were not obtained.

## Presentation Requirements

### Professional Form and Language

Use clear, formal business language, informative headings, concise paragraphs, and readable tables. Use English unless the task explicitly requests another report language.

Use a single report title, second-level headings for the front matter, numbered main sections, and appendix, and third-level headings for workstreams and subsections. Use additional levels only where needed. Avoid decorative icons, promotional claims, exaggerated certainty, and unnecessary technical discussion of the agent.

Do not impose a fixed page count, number of findings, or equal length across workstreams. Detail should follow materiality, complexity, and the available evidence.

### Consistency and Traceability

Keep company names, entity boundaries, dates, metric definitions, finding IDs, risk IDs, and source references consistent throughout.

Locate the detailed facts in the workstream analysis, the integrated judgment in Section 4, the financial and transaction implications in Section 5, and the unresolved follow-up in Section 6. Use cross-references to avoid duplicating the same narrative.

Preserve evidence qualifications in summaries, tables, and conclusions. Cite material claims close to their use; a reference elsewhere in the report or only in the appendix is not a substitute for clear attribution.

### Data and Missing Information

Identify the entity, period, currency, units, and basis of financial or operating data. Distinguish reported, adjusted, estimated, calculated, and illustrative figures. Use precision proportionate to the underlying evidence.

Do not represent missing information as zero. Use specific descriptions such as `Not publicly disclosed`, `Not independently corroborated`, `Unable to assess`, or `Not applicable`, according to the actual reason. Avoid unexplained dashes or `N/A` where they could conceal a material distinction.

Do not omit a required section solely because evidence is limited. Provide the appropriate coverage statement, the resulting limitation, and any material implication for the overall assessment.

### Final Delivery

Return only the completed report, without a conversational preface, the output instructions, unresolved template placeholders, or an internal reasoning transcript.

Do not fabricate administrative details or request additional inputs merely to fill optional report fields. A professional report may reach qualified or inconclusive judgments; apparent completeness must not take precedence over evidentiary accuracy.
