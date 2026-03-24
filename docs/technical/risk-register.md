# Risk Register — Matrix Competency Matrix Application

**Project:** Matrix — Competency Matrix Web Application for Sber's Dynamic Infrastructure Portal Support Division
**Last Updated:** 2026-03-24
**Review Cadence:** Monthly
**Next Review:** 2026-04-24

---

## 1. Risk Probability x Impact Matrix

|               | **Negligible** | **Low**       | **Medium**      | **High**         | **Critical**      |
|---------------|:--------------:|:-------------:|:---------------:|:----------------:|:-----------------:|
| **Very High** | Medium         | Medium        | High            | Very High        | Very High         |
| **High**      | Low            | Medium        | High            | High             | Very High         |
| **Medium**    | Low            | Low           | Medium          | High             | High              |
| **Low**       | Negligible     | Low           | Low             | Medium           | Medium            |
| **Very Low**  | Negligible     | Negligible    | Low             | Low              | Medium            |

**Legend:**
- Rows = Probability (Very Low to Very High)
- Columns = Impact (Negligible to Critical)
- Cell value = Composite Risk Score

---

## 2. Risk Register

### 2.1 Technical Risks

#### RISK-001: Solo Developer — Bus Factor = 1

| Field | Details |
|---|---|
| **ID** | RISK-001 |
| **Category** | Technical |
| **Title** | Solo Developer — Bus Factor = 1 |
| **Description** | The project has a single developer (supplemented by AI assistance). If the developer becomes unavailable due to illness, departure, or any other reason, all development, maintenance, and operational knowledge is lost. There is no second person who can take over the codebase, deployment pipeline, or operational procedures on short notice. |
| **Probability** | High |
| **Impact** | High |
| **Risk Score** | High |
| **Mitigation Strategy** | Maintain thorough inline documentation and architecture decision records (ADRs). Use AI-assisted code generation to enforce consistent patterns. Keep all infrastructure as code (IaC). Write comprehensive CLAUDE.md and onboarding guides. Ensure CI/CD pipeline is fully automated and self-documenting. Use standard, well-known technology stack to lower onboarding barrier. |
| **Contingency Plan** | If the developer becomes unavailable: (1) the documented codebase and IaC allow a replacement developer to onboard within 1-2 weeks; (2) AI assistants can help a new developer understand the codebase quickly; (3) the application can run in maintenance mode without active development for an extended period due to automated operations. |
| **Owner** | Developer |
| **Status** | Mitigating |

---

#### RISK-002: Technology Choice Mismatch

| Field | Details |
|---|---|
| **ID** | RISK-002 |
| **Category** | Technical |
| **Title** | Technology Choice Mismatch |
| **Description** | Selected technologies (e.g., frontend framework, backend language, database) may prove inadequate for evolving requirements, particularly around real-time assessment workflows, complex reporting, or future multi-tenancy needs. A wrong choice discovered late in development leads to costly rewrites. |
| **Probability** | Low |
| **Impact** | Medium |
| **Risk Score** | Low |
| **Mitigation Strategy** | Conduct technology evaluation against known requirements before committing. Use proven, widely adopted frameworks with strong community support. Design with clean separation of concerns (hexagonal architecture) so individual components can be replaced. Build a prototype/MVP early to validate core technology assumptions. |
| **Contingency Plan** | If a technology proves inadequate: (1) isolate the problematic component behind an interface; (2) incrementally replace it while keeping the rest of the system operational; (3) leverage the modular architecture to swap implementations without full rewrite. |
| **Owner** | Developer |
| **Status** | Accepted |

---

#### RISK-003: Database Schema Changes Breaking Production

| Field | Details |
|---|---|
| **ID** | RISK-003 |
| **Category** | Technical |
| **Title** | Database Schema Changes Breaking Production |
| **Description** | As the data model evolves (competency matrices, assessments, user roles), schema migrations may fail, corrupt data, or introduce incompatibilities with running application code. With a small user base, data loss is especially damaging since each record represents a manually entered assessment. |
| **Probability** | Medium |
| **Impact** | High |
| **Risk Score** | High |
| **Mitigation Strategy** | Use a migration framework (e.g., Alembic) with version-controlled, reversible migrations. Test all migrations against a copy of production data in a staging environment before applying to production. Enforce backward-compatible schema changes (expand-then-contract pattern). Automate pre-migration backups. |
| **Contingency Plan** | If a migration breaks production: (1) immediately roll back using the reversible migration or restore from the pre-migration backup; (2) analyze the failure in staging; (3) fix and re-test the migration before re-applying. Target RTO: under 1 hour. |
| **Owner** | Developer |
| **Status** | Mitigating |

---

#### RISK-004: Performance Degradation with Data Growth

| Field | Details |
|---|---|
| **ID** | RISK-004 |
| **Category** | Technical |
| **Title** | Performance Degradation with Data Growth |
| **Description** | As the number of employees, competency assessments, and historical records grows (especially if commercialized to multiple organizations), query performance may degrade. Complex aggregation queries for 360-degree reviews and competency gap analysis across departments could become slow. |
| **Probability** | Low |
| **Impact** | Medium |
| **Risk Score** | Low |
| **Mitigation Strategy** | Design database schema with proper indexing from the start. Implement pagination for all list views. Use database query analysis (EXPLAIN) during development. Set up performance benchmarks with realistic data volumes (1000+ employees, 10000+ assessments). Consider materialized views or caching for expensive aggregation queries. |
| **Contingency Plan** | If performance degrades: (1) identify slow queries via application performance monitoring; (2) add targeted indexes or query optimizations; (3) implement caching layer (Redis) for frequently accessed aggregated data; (4) consider read replicas if query load justifies it. |
| **Owner** | Developer |
| **Status** | Open |

---

#### RISK-005: Third-Party Dependency Vulnerabilities

| Field | Details |
|---|---|
| **ID** | RISK-005 |
| **Category** | Technical |
| **Title** | Third-Party Dependency Vulnerabilities |
| **Description** | The application relies on third-party libraries and frameworks. Known vulnerabilities (CVEs) in these dependencies can expose the application to exploits. Given that the application handles employee performance data within Sber's infrastructure, this is a compliance concern as well. |
| **Probability** | Medium |
| **Impact** | Medium |
| **Risk Score** | Medium |
| **Mitigation Strategy** | Integrate dependency scanning (e.g., Safety, Dependabot, Snyk) into CI/CD pipeline. Pin dependency versions with lock files. Review and update dependencies on a regular schedule (at least monthly). Minimize the number of direct dependencies. Prefer well-maintained libraries with active security response teams. |
| **Contingency Plan** | If a critical vulnerability is discovered: (1) assess exploitability in our specific context; (2) apply patch or upgrade within 48 hours for critical CVEs; (3) if no patch is available, implement a workaround or temporarily disable the affected feature; (4) notify stakeholders if data exposure is possible. |
| **Owner** | Developer |
| **Status** | Mitigating |

---

#### RISK-006: Complex 360-Degree Assessment Aggregation Logic Errors

| Field | Details |
|---|---|
| **ID** | RISK-006 |
| **Category** | Technical |
| **Title** | Complex 360-Degree Assessment Aggregation Logic Errors |
| **Description** | The 360-degree assessment feature aggregates evaluations from multiple reviewers (self, manager, peers, subordinates) with different weights and normalization. Errors in this logic — incorrect weight application, rounding issues, missing reviewer handling — can produce misleading competency scores, directly impacting personnel decisions. |
| **Probability** | Medium |
| **Impact** | High |
| **Risk Score** | High |
| **Mitigation Strategy** | Develop comprehensive unit and integration tests for all aggregation scenarios, including edge cases (single reviewer, all-same scores, missing categories). Implement audit trails showing how each final score was computed. Provide a "calculation breakdown" view in the UI so managers can verify results. Conduct user acceptance testing with real-world data samples. |
| **Contingency Plan** | If an aggregation error is found in production: (1) flag affected assessments as "under review"; (2) notify affected managers; (3) fix the logic and recompute scores; (4) provide before/after comparison for transparency; (5) document the incident and add regression tests. |
| **Owner** | Developer |
| **Status** | Open |

---

#### RISK-007: Data Migration Complexity from CSV/Excel Imports

| Field | Details |
|---|---|
| **ID** | RISK-007 |
| **Category** | Technical |
| **Title** | Data Migration Complexity from CSV/Excel Imports |
| **Description** | Initial data population and ongoing imports from CSV/Excel files (employee lists, existing competency data, organizational structure) are error-prone. Inconsistent formats, encoding issues (Cyrillic text), duplicate entries, and missing required fields can lead to corrupted or incomplete data in the system. |
| **Probability** | Medium |
| **Impact** | Medium |
| **Risk Score** | Medium |
| **Mitigation Strategy** | Build a robust import pipeline with strict validation, clear error reporting, and a dry-run mode that shows what will be imported before committing. Provide downloadable template files with correct formatting. Handle encoding detection automatically (UTF-8, Windows-1251). Implement duplicate detection and merge strategies. Log all import operations for audit. |
| **Contingency Plan** | If a bad import corrupts data: (1) use the import audit log to identify affected records; (2) roll back using pre-import database snapshot; (3) fix the import file and re-run with dry-run validation first; (4) if rollback is not possible, manually correct affected records using the audit trail. |
| **Owner** | Developer |
| **Status** | Open |

---

### 2.2 Organizational Risks

#### RISK-008: Low User Adoption

| Field | Details |
|---|---|
| **ID** | RISK-008 |
| **Category** | Organizational |
| **Title** | Low User Adoption — Users Resist Switching to a Formalized Process |
| **Description** | Currently there is no structured competency tracking process in the division. While this means there is no competing tool to displace, introducing a formalized system requires users (managers and engineers) to adopt new habits: regularly updating competencies, conducting assessments, and using the tool for development planning. Resistance to formalization and perceived bureaucracy overhead can lead to the tool being underutilized or abandoned. |
| **Probability** | Medium |
| **Impact** | High |
| **Risk Score** | High |
| **Mitigation Strategy** | Involve key users (team leads) in the design process from the start. Keep the UI minimal and workflows fast — filling in an assessment should take under 5 minutes. Demonstrate clear value: show competency gaps, suggest training, enable fair promotions. Provide onboarding sessions and quick-start guides. Start with a pilot group before rolling out to the full division. Integrate with existing workflows (Telegram notifications, calendar reminders). |
| **Contingency Plan** | If adoption is low after launch: (1) conduct user interviews to identify friction points; (2) simplify workflows further based on feedback; (3) get management buy-in to make competency reviews a quarterly process; (4) gamify the experience (progress indicators, achievements); (5) if adoption remains critically low, pivot to a simpler "assessment-only" mode and expand features later. |
| **Owner** | Developer / Division Management |
| **Status** | Open |

---

#### RISK-009: Stakeholder Priorities Change

| Field | Details |
|---|---|
| **ID** | RISK-009 |
| **Category** | Organizational |
| **Title** | Stakeholder Priorities Change |
| **Description** | The project's sponsor or key stakeholders within Sber may shift priorities due to organizational restructuring, budget reallocation, or strategic pivots. Without a strict deadline and as an internal tool, the project is vulnerable to deprioritization in favor of more urgent business needs. |
| **Probability** | Low |
| **Impact** | High |
| **Risk Score** | Medium |
| **Mitigation Strategy** | Deliver incremental value through regular MVP releases — ensure the tool is useful even in its earliest form. Align project goals with broader organizational KPIs (employee retention, skill development metrics). Maintain regular communication with stakeholders through demo sessions. Document and communicate ROI and time savings at each milestone. |
| **Contingency Plan** | If priorities shift: (1) ensure the current version is stable and deployable as-is; (2) document the roadmap and backlog for future resumption; (3) propose a minimal maintenance mode requiring negligible resources; (4) identify alternative sponsors within the organization who benefit from the tool. |
| **Owner** | Developer / Project Sponsor |
| **Status** | Open |

---

#### RISK-010: Scope Creep — Too Many Features Requested for MVP

| Field | Details |
|---|---|
| **ID** | RISK-010 |
| **Category** | Organizational |
| **Title** | Scope Creep — Too Many Features Requested for MVP |
| **Description** | As stakeholders and early users see the potential of the system, feature requests will accumulate: advanced analytics, integration with HR systems, gamification, mobile app, AI-powered recommendations, etc. For a solo developer, accepting too many features delays MVP delivery and risks building a bloated product that never ships. |
| **Probability** | High |
| **Impact** | Medium |
| **Risk Score** | High |
| **Mitigation Strategy** | Define a clear MVP scope document with explicit in/out boundaries. Use MoSCoW prioritization (Must/Should/Could/Won't). Maintain a public backlog where stakeholders can see their requests are tracked but not necessarily in the current iteration. Set firm iteration deadlines (2-week sprints). Learn to say "yes, but in a future release." |
| **Contingency Plan** | If scope creep has already delayed the MVP: (1) perform a scope audit and ruthlessly cut features to the minimum viable set; (2) release what is ready as "v0.1" to get early feedback; (3) communicate a revised timeline with the reduced scope; (4) use early user feedback to prioritize the backlog for the next iteration. |
| **Owner** | Developer |
| **Status** | Mitigating |

---

#### RISK-011: Insufficient User Feedback During Development

| Field | Details |
|---|---|
| **ID** | RISK-011 |
| **Category** | Organizational |
| **Title** | Insufficient User Feedback During Development |
| **Description** | Building a tool without regular user feedback risks creating features that don't match actual workflows, using terminology that confuses users, or missing critical requirements. With a solo developer, there is no product manager or UX researcher to bridge the gap between development and user needs. |
| **Probability** | Medium |
| **Impact** | Medium |
| **Risk Score** | Medium |
| **Mitigation Strategy** | Schedule bi-weekly demo sessions with 2-3 representative users (a team lead, a senior engineer, and a junior engineer). Deploy a staging environment accessible to pilot users for hands-on testing. Create a dedicated Telegram channel for feedback. Implement analytics to track feature usage. Conduct brief (15-min) user interviews after each sprint. |
| **Contingency Plan** | If the product is built without adequate feedback and users reject it: (1) conduct rapid user research (interviews + observation sessions); (2) identify the top 3 pain points; (3) redesign the affected workflows in a focused sprint; (4) re-engage users with the improved version. |
| **Owner** | Developer |
| **Status** | Open |

---

#### RISK-012: Loss of Project Champion / Sponsor

| Field | Details |
|---|---|
| **ID** | RISK-012 |
| **Category** | Organizational |
| **Title** | Loss of Project Champion / Sponsor |
| **Description** | If the key sponsor or champion who initiated and supports the project leaves the organization or changes role, the project may lose its organizational backing, budget, and political support. This is particularly dangerous for an internal tool that is not yet fully established. |
| **Probability** | Low |
| **Impact** | Critical |
| **Risk Score** | Medium |
| **Mitigation Strategy** | Build support across multiple stakeholders rather than relying on a single champion. Demonstrate value to multiple department heads. Ensure the project is documented in official department plans and roadmaps. Create "champions" at the team-lead level who directly benefit from the tool and can advocate for it. |
| **Contingency Plan** | If the champion is lost: (1) immediately identify and engage a replacement sponsor; (2) prepare a concise value proposition document for the new sponsor; (3) leverage existing user adoption data and testimonials to demonstrate value; (4) if no new sponsor emerges, shift to a community-maintained model where the tool continues as a grassroots effort. |
| **Owner** | Developer / Project Sponsor |
| **Status** | Open |

---

### 2.3 Business Risks

#### RISK-013: Commercialization Fails — No Market Demand

| Field | Details |
|---|---|
| **ID** | RISK-013 |
| **Category** | Business |
| **Title** | Commercialization Fails — No Market Demand |
| **Description** | If the tool is eventually offered as a commercial product, there may be insufficient market demand. The competency matrix space is niche, and potential customers may prefer all-in-one HR platforms or consider the problem not worth a dedicated tool. The effort to prepare for commercialization (multi-tenancy, billing, marketing) could be wasted. |
| **Probability** | Medium |
| **Impact** | Medium |
| **Risk Score** | Medium |
| **Mitigation Strategy** | Validate market demand before investing in commercialization: conduct customer discovery interviews with 10+ potential buyers from other companies. Analyze competitors and identify underserved segments. Start with a freemium model or open-core approach to lower the barrier to adoption. Focus on a specific niche (IT support divisions) where the tool's specificity is an advantage. |
| **Contingency Plan** | If commercialization proves unviable: (1) the tool continues as a successful internal product, justifying the development investment; (2) consider open-sourcing the tool to build community and reputation; (3) pivot the commercial offering to consulting/implementation services rather than SaaS; (4) license the technology to HR platform vendors as an embedded module. |
| **Owner** | Developer / Business Stakeholder |
| **Status** | Open |

---

#### RISK-014: Competition from Established HR Platforms

| Field | Details |
|---|---|
| **ID** | RISK-014 |
| **Category** | Business |
| **Title** | Competition from Established HR Platforms Adding Competency Features |
| **Description** | Major HR platforms (SAP SuccessFactors, Workday, 1C:HRM, etc.) may add or improve competency matrix features, making a standalone tool less attractive. These platforms have larger development teams, established customer bases, and integration ecosystems that a solo-developed tool cannot match. |
| **Probability** | Medium |
| **Impact** | Medium |
| **Risk Score** | Medium |
| **Mitigation Strategy** | Differentiate through specialization: focus on IT/engineering competency models, technical skill assessment, and integration with developer tools (Git, Jira, CI/CD). Maintain agility — deliver features faster than enterprise platforms can. Build deep domain expertise in technical competency assessment. Offer superior UX for the specific use case rather than competing on breadth. |
| **Contingency Plan** | If a competing platform captures the market: (1) position Matrix as a best-of-breed complement that integrates with HR platforms via APIs; (2) focus on the specific niche where large platforms underperform; (3) consider pivoting to a different aspect of engineering team management (on-call scheduling, knowledge management); (4) offer migration tools to ease transition if users choose to switch. |
| **Owner** | Developer |
| **Status** | Accepted |

---

#### RISK-015: Regulatory/Compliance Changes Affecting Data Handling

| Field | Details |
|---|---|
| **ID** | RISK-015 |
| **Category** | Business |
| **Title** | Regulatory/Compliance Changes Affecting Data Handling |
| **Description** | Changes in Russian data protection law (Federal Law 152-FZ on Personal Data), Sber's internal data governance policies, or industry regulations could impose new requirements on how employee competency and assessment data is stored, processed, and retained. Non-compliance could force feature removal, data deletion, or project suspension. |
| **Probability** | Low |
| **Impact** | High |
| **Risk Score** | Medium |
| **Mitigation Strategy** | Design the system with privacy-by-design principles from the start: data minimization, purpose limitation, consent tracking, and data retention policies. Implement data export and deletion capabilities (right to be forgotten). Store all personal data within Russia-located infrastructure. Consult with Sber's legal/compliance team during the design phase. Maintain an up-to-date data processing agreement. |
| **Contingency Plan** | If new regulations require changes: (1) assess the gap between current implementation and new requirements; (2) prioritize compliance changes above all feature work; (3) implement required changes within the regulatory grace period; (4) if fundamental architectural changes are needed, prepare a compliance roadmap and communicate timeline to stakeholders. |
| **Owner** | Developer / Legal/Compliance Team |
| **Status** | Open |

---

#### RISK-016: Inability to Scale Architecture for Multi-Tenant Use

| Field | Details |
|---|---|
| **ID** | RISK-016 |
| **Category** | Business |
| **Title** | Inability to Scale Architecture for Multi-Tenant Use |
| **Description** | If commercialization is pursued, the application must support multiple independent organizations (tenants) with data isolation, separate configurations, and potentially different competency models. An architecture originally designed for a single organization may be fundamentally incompatible with multi-tenancy, requiring an expensive rewrite. |
| **Probability** | Medium |
| **Impact** | High |
| **Risk Score** | High |
| **Mitigation Strategy** | Design the data model with tenant awareness from the start, even if only one tenant exists initially. Use tenant ID as a partition key in all major tables. Abstract organization-specific configuration into a settings layer. Document architectural decisions that affect multi-tenancy. Evaluate multi-tenancy patterns (shared database with tenant column vs. schema-per-tenant vs. database-per-tenant) early and choose one that fits the expected scale. |
| **Contingency Plan** | If the architecture cannot support multi-tenancy: (1) deploy separate instances per tenant as a short-term solution (increases ops cost but provides full isolation); (2) gradually refactor the data layer to add tenant awareness; (3) if a full rewrite is needed, scope it as a "v2" with multi-tenancy as a core requirement, while maintaining v1 for the existing internal deployment. |
| **Owner** | Developer |
| **Status** | Open |

---

### 2.4 Security Risks

#### RISK-017: Data Breach — Employee Data Exposure

| Field | Details |
|---|---|
| **ID** | RISK-017 |
| **Category** | Security |
| **Title** | Data Breach — Employee Competency and Assessment Data Exposure |
| **Description** | The application stores sensitive employee data: personal information, competency assessments, performance scores, peer reviews, and development plans. A data breach could expose this information, causing reputational damage to Sber, legal liability under data protection laws, and personal harm to employees whose assessment data is leaked. |
| **Probability** | Low |
| **Impact** | Critical |
| **Risk Score** | Medium |
| **Mitigation Strategy** | Encrypt all data at rest and in transit (TLS 1.3, AES-256). Implement defense-in-depth: network segmentation, WAF, rate limiting. Follow OWASP Top 10 guidelines. Conduct security review before production deployment. Use parameterized queries to prevent SQL injection. Implement comprehensive audit logging. Apply principle of least privilege for all service accounts. Store no unnecessary personal data. |
| **Contingency Plan** | If a breach occurs: (1) immediately isolate the affected system; (2) assess the scope of the breach (what data, how many records, what timeframe); (3) notify Sber's security team within 1 hour; (4) follow Sber's incident response procedure; (5) notify affected employees as required by law; (6) conduct a post-incident review and implement additional safeguards; (7) engage external security auditors if needed. |
| **Owner** | Developer / Security Team |
| **Status** | Mitigating |

---

#### RISK-018: Insufficient Access Control

| Field | Details |
|---|---|
| **ID** | RISK-018 |
| **Category** | Security |
| **Title** | Insufficient Access Control — Users See Unauthorized Data |
| **Description** | The application has multiple user roles (admin, manager, employee) with different data visibility requirements. A manager should see their team's assessments but not other teams'. An employee should see their own data but not peers' assessment details. Broken access control (IDOR, privilege escalation, missing authorization checks) is among the most common web application vulnerabilities. |
| **Probability** | Medium |
| **Impact** | High |
| **Risk Score** | High |
| **Mitigation Strategy** | Implement role-based access control (RBAC) with clearly defined permission matrices. Enforce authorization checks at the API/service layer, not just the UI. Write authorization integration tests for every endpoint. Use a centralized authorization middleware. Implement row-level security where supported by the database. Conduct access control testing as part of each feature's QA. Deny by default — require explicit grants. |
| **Contingency Plan** | If an access control flaw is discovered: (1) immediately patch the vulnerability; (2) audit access logs to determine if unauthorized access actually occurred; (3) if unauthorized access is confirmed, notify affected users and management; (4) conduct a comprehensive access control audit across all endpoints; (5) add regression tests to prevent recurrence. |
| **Owner** | Developer |
| **Status** | Open |

---

#### RISK-019: JWT Token Theft or Misuse

| Field | Details |
|---|---|
| **ID** | RISK-019 |
| **Category** | Security |
| **Title** | JWT Token Theft or Misuse |
| **Description** | The application uses JWT tokens for authentication. If tokens are stolen (via XSS, network interception, or compromised client), an attacker can impersonate a legitimate user. Long-lived tokens or tokens without proper validation increase the window of exploitation. |
| **Probability** | Low |
| **Impact** | High |
| **Risk Score** | Medium |
| **Mitigation Strategy** | Use short-lived access tokens (15-30 minutes) with refresh token rotation. Store tokens in HTTP-only, Secure, SameSite cookies — never in localStorage. Implement Content Security Policy (CSP) headers to mitigate XSS. Validate token signature, expiration, issuer, and audience on every request. Support token revocation for user logout and password changes. Implement rate limiting on token refresh endpoints. |
| **Contingency Plan** | If token theft is suspected: (1) revoke all active tokens for the affected user(s); (2) force re-authentication; (3) analyze access logs for the compromised token's activity; (4) if significant unauthorized actions were performed, follow the data breach contingency (RISK-017); (5) rotate the JWT signing key if key compromise is suspected. |
| **Owner** | Developer |
| **Status** | Open |

---

### 2.5 Operational Risks

#### RISK-020: Cloud Provider Outage

| Field | Details |
|---|---|
| **ID** | RISK-020 |
| **Category** | Operational |
| **Title** | Cloud Provider Outage |
| **Description** | The application is deployed on a cloud platform. Cloud provider outages, while infrequent, can render the application completely unavailable. For 10-50 users in a support division, even a few hours of downtime is tolerable, but prolonged outages during critical assessment periods (quarterly reviews) could be disruptive. |
| **Probability** | Low |
| **Impact** | Medium |
| **Risk Score** | Low |
| **Mitigation Strategy** | Choose a reputable cloud provider with a strong SLA (99.9%+). Deploy across multiple availability zones if cost-effective. Implement health checks and automated restart policies. Design the application to handle graceful degradation (read-only mode if database is unavailable). Maintain infrastructure-as-code for rapid redeployment to an alternative provider if needed. |
| **Contingency Plan** | If the cloud provider experiences a prolonged outage: (1) communicate expected downtime to users via Telegram; (2) if outage exceeds 4 hours during a critical period, consider deploying to an alternative environment; (3) once service is restored, verify data integrity; (4) if the outage reveals single-point-of-failure issues, evaluate multi-region deployment for critical periods. |
| **Owner** | Developer |
| **Status** | Accepted |

---

#### RISK-021: Backup Failure Leading to Data Loss

| Field | Details |
|---|---|
| **ID** | RISK-021 |
| **Category** | Operational |
| **Title** | Backup Failure Leading to Data Loss |
| **Description** | If automated backups silently fail (misconfigured cron, full disk, permission errors) and a data loss event occurs (accidental deletion, corruption, ransomware), there may be no viable backup to restore from. For a system containing months or years of competency assessments, this data is irreplaceable. |
| **Probability** | Low |
| **Impact** | Critical |
| **Risk Score** | Medium |
| **Mitigation Strategy** | Implement automated daily backups with verification (restore test). Use the 3-2-1 backup rule: 3 copies, 2 different media, 1 offsite. Set up monitoring and alerting for backup job success/failure. Test backup restoration quarterly. Maintain point-in-time recovery capability (e.g., PostgreSQL WAL archiving). Document and automate the full restoration procedure. |
| **Contingency Plan** | If backup failure is discovered after a data loss event: (1) check all possible backup locations (cloud snapshots, WAL archives, local copies); (2) attempt recovery from the most recent available backup, even if outdated; (3) cross-reference with any data exports (CSV/Excel) that users may have downloaded; (4) for partially recovered data, engage users to manually verify and supplement missing records; (5) implement immediate backup monitoring improvements. |
| **Owner** | Developer |
| **Status** | Open |

---

#### RISK-022: Telegram API Changes Breaking Notifications

| Field | Details |
|---|---|
| **ID** | RISK-022 |
| **Category** | Operational |
| **Title** | Telegram API Changes Breaking Notifications |
| **Description** | The application uses Telegram Bot API for sending notifications (assessment reminders, review deadlines, system alerts). Telegram may deprecate API endpoints, change rate limits, or modify bot policies, breaking the notification system. |
| **Probability** | Low |
| **Impact** | Low |
| **Risk Score** | Low |
| **Mitigation Strategy** | Abstract the notification system behind an interface so the transport layer (Telegram, email, etc.) can be swapped. Use the official Telegram Bot API with stable, well-documented endpoints. Pin the Telegram library version and monitor changelogs. Implement a fallback notification channel (email). Monitor notification delivery success rates. |
| **Contingency Plan** | If Telegram notifications break: (1) activate the fallback email notification channel; (2) notify users about the temporary change via the application's UI; (3) update the Telegram integration to comply with API changes; (4) if Telegram becomes permanently unsuitable, migrate fully to an alternative channel. |
| **Owner** | Developer |
| **Status** | Accepted |

---

#### RISK-023: Developer Burnout Due to Solo Work

| Field | Details |
|---|---|
| **ID** | RISK-023 |
| **Category** | Operational |
| **Title** | Developer Burnout Due to Solo Work |
| **Description** | As the sole developer handling all aspects of the project (design, development, testing, deployment, operations, user support, and stakeholder management), the workload and cognitive overhead can lead to burnout. This directly impacts code quality, delivery speed, and the developer's long-term commitment to the project. Burnout is especially likely during intense periods (pre-launch, post-launch support, critical bugs). |
| **Probability** | Medium |
| **Impact** | High |
| **Risk Score** | High |
| **Mitigation Strategy** | Leverage AI assistants extensively to reduce repetitive work (code generation, testing, documentation). Automate everything possible (CI/CD, monitoring, backups). Set realistic sprint goals — consistently delivering small increments rather than heroic pushes. Maintain strict work-life boundaries. Take regular breaks between sprints. Celebrate milestones. Seek peer interaction through code reviews with AI or community participation. |
| **Contingency Plan** | If burnout occurs: (1) reduce scope to maintenance-only mode temporarily; (2) communicate reduced capacity to stakeholders with a recovery timeline; (3) identify and delegate any tasks that can be handled by others (e.g., user support to a team lead); (4) seek management support for temporary additional resources or reduced expectations; (5) consider bringing in a contract developer for specific tasks. |
| **Owner** | Developer / Management |
| **Status** | Open |

---

## 3. Risk Response Strategies Summary

| Strategy | Description | Applied To |
|---|---|---|
| **Avoid** | Eliminate the risk by removing its cause or changing the plan. | Not currently applied to any identified risk. |
| **Mitigate** | Reduce the probability or impact of the risk through proactive measures. | RISK-001 (documentation), RISK-003 (migrations), RISK-005 (dependency scanning), RISK-010 (scope management), RISK-017 (security measures) |
| **Transfer** | Shift the risk impact to a third party (insurance, outsourcing, SLA). | RISK-020 (cloud provider SLA), RISK-015 (legal/compliance team involvement) |
| **Accept** | Acknowledge the risk and prepare a contingency plan without proactive mitigation. | RISK-002 (technology choice), RISK-014 (competition), RISK-020 (cloud outage), RISK-022 (Telegram API) |
| **Escalate** | Raise the risk to a higher authority because it is outside the project's control. | RISK-009 (stakeholder priorities), RISK-012 (loss of sponsor), RISK-015 (regulatory changes) |

### Risk Distribution by Category

| Category | Count | High/Critical Risks |
|---|---|---|
| Technical | 7 | RISK-001, RISK-003, RISK-006 |
| Organizational | 5 | RISK-008, RISK-010, RISK-012 |
| Business | 4 | RISK-016 |
| Security | 3 | RISK-017, RISK-018 |
| Operational | 4 | RISK-021, RISK-023 |
| **Total** | **23** | **10** |

### Top 5 Risks Requiring Immediate Attention

| Rank | ID | Title | Risk Score | Rationale |
|---|---|---|---|---|
| 1 | RISK-001 | Solo Developer — Bus Factor = 1 | High | Foundational risk that amplifies all other risks. |
| 2 | RISK-017 | Data Breach — Employee Data Exposure | Medium (but Critical impact) | Reputational and legal consequences for Sber are severe. |
| 3 | RISK-018 | Insufficient Access Control | High | Most common web vulnerability; directly affects data privacy. |
| 4 | RISK-006 | 360-Degree Assessment Logic Errors | High | Core feature; errors undermine trust in the entire system. |
| 5 | RISK-008 | Low User Adoption | High | If users don't adopt the tool, all other efforts are wasted. |

---

## 4. Review Schedule

| Activity | Frequency | Responsible | Notes |
|---|---|---|---|
| Full risk register review | Monthly | Developer | Review all risks, update statuses, adjust scores. |
| New risk identification | Ongoing | Developer / Stakeholders | Add risks as they are discovered during development. |
| Top-5 risk deep dive | Bi-weekly | Developer | Focus on the highest-priority risks, verify mitigation progress. |
| Post-incident risk update | After any incident | Developer | Update affected risks, add new risks if applicable. |
| Stakeholder risk review | Quarterly | Developer / Sponsor | Present risk status to stakeholders, get feedback on priorities. |
| Pre-release risk assessment | Before each release | Developer | Evaluate risks introduced by the release, verify mitigations. |

**Review Log:**

| Date | Reviewer | Changes Made |
|---|---|---|
| 2026-03-24 | Developer | Initial risk register created with 23 risks across 5 categories. |

---

*This document is a living artifact. Update it whenever risks change, new risks are identified, or existing risks are resolved.*
