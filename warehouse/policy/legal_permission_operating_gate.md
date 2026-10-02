# Anderson House — Legal / Permission Operating Gate

**Version:** 001  
**Date:** 2026-10-01  
**Purpose:** Establish a repeatable legal/permission/compliance gate for Anderson House before production begins, and apply the same gate to every later function, source, service, and external receiver.

> This is an operating compliance design, not a substitute for advice from a qualified lawyer where a material legal question remains uncertain.

---

## 1. PRE-PRODUCTION HOUSE GATE

Before a customer/product job enters production, the Coordinator must be able to answer:

**ARE THE HOUSE, RESOURCES, AND ROUTES WE INTEND TO USE PERMITTED FOR THIS PURPOSE?**

The house is not declared "legal forever." Instead, it maintains a repeatable gate because laws, licenses, provider terms, geography, and uses can change.

### Required categories

1. **Identity / authority**
   - Are these our accounts, devices, repositories, credentials, and resources, or are we otherwise authorized to use them?
   - Are credentials and permissions used only within their granted scope?

2. **Service terms / acceptable use**
   - AWS, Google Cloud, Cloudflare, GitHub, KDP, APIs, AI services, and other providers each have their own agreements and service-specific terms.
   - A service may be lawful generally but prohibit a particular method of use.
   - Current provider terms must be checked when the use is material or has changed.

3. **Copyright / public domain / licenses**
   - Determine whether material is:
     - our own,
     - public domain,
     - licensed,
     - permissioned,
     - or rights-uncertain.
   - Copyright may protect expression such as source code, text, artwork, photographs, and software.
   - Ideas, procedures, systems, methods of operation, and functional concepts are generally not protected by copyright as such, although their particular expression may be protected.
   - Open/public access does not itself mean unrestricted reuse.

4. **Trademark / branding**
   - Do not assume permission to use a provider/project name or trademark merely because underlying content is reusable.
   - Example: Project Gutenberg has separate trademark/license conditions when its name remains associated with redistributed material.

5. **Data / privacy / confidentiality**
   - Do we have a proper basis and permission to collect, store, process, or publish the data involved?
   - Do not expose credentials, private data, or confidential connected-source material.
   - Apply provider-specific data terms when AI/cloud services process content.

6. **Automated access / scraping / robots / rate limits**
   - Automation must respect site/service terms, access controls, rate limits, API rules, and explicit restrictions.
   - Do not bypass authentication, technical controls, paywalls, or access restrictions.
   - Example: Project Gutenberg asks automated/bulk downloaders to use its mirrors rather than automate against the main website.

7. **Security / authorization**
   - No unauthorized access, credential use, disruption, vulnerability testing, evasion, or circumvention unless expressly permitted.
   - Use least privilege, scoped credentials, and logging.

8. **Commercial / publication receiver requirements**
   - External receivers such as KDP may impose contractual/policy requirements in addition to general law.
   - These become functional requirements in the external-receiver adapter layer.

9. **Jurisdiction**
   - Rights can differ by country.
   - Record where the relevant use, distribution, or publication occurs when that can alter the legal result.
   - Do not assume U.S. public-domain status automatically answers every non-U.S. use.

---

## 2. BILL — LEGAL / PERMISSION SURVEY

For every candidate function/resource/source, Bill's survey package must include where relevant:

- SOURCE / OWNER / PROVIDER
- ORIGINAL URL / REPOSITORY / RECORD
- DATE / VERSION
- JURISDICTION NOTES
- COPYRIGHT STATUS
- LICENSE / PERMISSION
- TRADEMARK CONDITIONS
- SERVICE TERMS / AUP / API TERMS
- AUTOMATION / RATE-LIMIT CONDITIONS
- DATA / PRIVACY CONDITIONS
- COMMERCIAL-USE CONDITIONS
- MODIFICATION / DERIVATIVE CONDITIONS
- ATTRIBUTION / NOTICE REQUIREMENTS
- REDISTRIBUTION CONDITIONS
- KNOWN RESTRICTIONS
- EVIDENCE / SOURCE LINKS
- UNCERTAINTIES

Bill must survey widely and must not treat "available on the internet" as "free to reuse."

If rights are unclear, Bill returns **RIGHTS-UNCERTAIN** rather than guessing.

---

## 3. TED — LEGAL BORGARIZATION RULE

Ted may choose among:

- **REUSE** — use as-is where permission permits.
- **ADAPT** — modify where license/permission permits.
- **COMPOSE** — combine compatible components and licenses.
- **CALL AS A SERVICE** — use through the provider's authorized interface and terms.
- **REIMPLEMENT FUNCTIONAL METHOD** — where the functional idea/method is usable but copying protected expression is not appropriate.
- **BUILD NEW** — independently implement the required function.
- **REJECT ROUTE** — where terms/rights make the candidate unsuitable.

Ted must log:

- which candidate(s) were used;
- what was copied versus independently implemented;
- what modifications were made;
- which notices/attribution must travel downstream;
- any continuing license obligations;
- output ownership/rights assumptions;
- provenance hashes/versions where practical.

Ted must not remove a restriction simply because it is inconvenient.

---

## 4. LINDA — LEGAL / PERMISSION VERIFICATION

Linda verifies both functional correctness **and permission fitness**.

Possible statuses:

- **LEGAL/PERMISSION CLEAR**
- **CLEAR WITH CONDITIONS**
- **PUBLIC-DOMAIN / UNRESTRICTED UNDER RECORDED JURISDICTION**
- **LICENSE CONDITIONS MUST TRAVEL**
- **TERMS-OF-SERVICE ROUTE ONLY**
- **RIGHTS UNCERTAIN — HOLD**
- **JURISDICTION CHECK REQUIRED**
- **PRIVACY / DATA HOLD**
- **UNAUTHORIZED ROUTE — REJECT**
- **REBUILD FROM FUNCTIONAL REQUIREMENT**
- **PROFESSIONAL LEGAL REVIEW REQUIRED**

Linda must be able to trace:

**OUTPUT → TED TRANSFORM → BILL CANDIDATE → ORIGINAL SOURCE / LICENSE / TERMS / AUTHORITY**

No material candidate should enter the verified Warehouse without this provenance where rights/terms matter.

---

## 5. COORDINATOR — HOUSE LEGAL GATE

The Coordinator holds the legal/permission gate as a required upstream state.

### Before production
**HOUSE LEGAL/PERMISSION GATE → VERIFIED OR CONDITIONALLY VERIFIED**

### During production
Every branch inherits relevant restrictions and provenance.

### At joins
Linda confirms that obligations are compatible after composition.

### At external receiver
Verify both:
- Anderson House's right to create/deliver the output; and
- the receiver's contractual/policy input requirements.

### If the gate fails
Do not abandon the function goal automatically.

Use:
**BLOCKED ROUTE → BILL RECASTS FOR ALTERNATIVE LEGAL ROUTE → TED BUILDS/ADAPTS → LINDA REVERIFIES**

---

## 6. CURRENT THREE AMIGOS BASELINE

The current use of AWS, Google Cloud, Cloudflare, GitHub, Termux/Android, and ordinary web resources is not inherently unlawful. Each resource must be used within:
- applicable law;
- account authorization;
- provider agreements and acceptable-use/service-specific terms;
- intellectual-property rights;
- privacy/data obligations;
- security/access restrictions.

Current official examples checked on 2026-10-01:

- **AWS:** Customer Agreement requires compliance with applicable law and policies; AWS AUP prohibits illegal/fraudulent activity, rights violations, and attacks on security/integrity/availability.
- **Google Cloud:** current AUP prohibits unlawful/infringing use, unauthorized access, interference/circumvention, and certain reverse engineering/vulnerability testing except where expressly permitted.
- **Cloudflare:** services are governed by applicable subscription/service agreements; Workers AI documentation notes third-party models can carry their own license terms and customers remain responsible for Customer Content.
- **GitHub:** public visibility/forking through GitHub does not mean every public repository grants unrestricted external reuse; additional reuse rights depend on the repository license/rightsholder.
- **Project Gutenberg:** most U.S. public-domain works can be commercially reused, but its trademark/license terms are separate; automated bulk access should follow its designated methods/mirrors.
- **U.S. copyright:** copyright protects original expression but generally not ideas, systems, procedures, or methods of operation themselves.

---

## 7. PERMANENT FUNCTION RECORD FIELDS

Every material Warehouse function should be able to carry:

**FUNCTION ID**  
**PURPOSE**  
**UPSTREAM STATE**  
**TRANSFORM**  
**DOWNSTREAM STATE**  
**SOURCE / PROVENANCE**  
**RIGHTSHOLDER / PROVIDER**  
**LICENSE / PUBLIC-DOMAIN / PERMISSION STATUS**  
**SERVICE / API TERMS**  
**JURISDICTION**  
**ATTRIBUTION / NOTICE**  
**MODIFICATION RIGHTS**  
**COMMERCIAL-USE RIGHTS**  
**DATA / PRIVACY CONDITIONS**  
**AUTOMATION / ACCESS CONDITIONS**  
**TED TRANSFORM HISTORY**  
**LINDA VERIFICATION STATUS**  
**EVIDENCE LINKS / VERSION / DATE**  
**FAILURE / STOP RULE**

---

## 8. STANDING RULE

**AVAILABLE DOES NOT MEAN PERMITTED.**

**SURVEY RIGHTS WITH THE FUNCTION → BUILD ONLY THROUGH PERMITTED ROUTES → CARRY PROVENANCE AND CONDITIONS FORWARD → LINDA VERIFIES BEFORE RELEASE.**

And when one route is not permitted:

**KEEP THE FUNCTION GOAL; CHANGE THE ROUTE.**
