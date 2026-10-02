# Anderson House — External Resource Agreement Register 001

**Checked:** 2026-10-01
**Purpose:** Track the agreements, free-plan/trial windows, usage limits, renewal/upgrade decisions, and legal account-continuity rules for Anderson House / The 3 Amigos resources.

> Dates below use the best-supported Anderson House activation records. Provider consoles remain authoritative for exact account-specific expiry timestamps and credit balances.

## AWS

**Relationship:** AWS Customer Agreement + AWS Free Tier / Free account plan + service-specific terms/AUP.

**Anderson House activation evidence:** Free account setup began 2026-09-28.

**Current free-plan rule:** Free account plan ends at the earlier of:
1. six months after AWS account creation, or
2. Free Tier credits being exhausted.

**Best-supported calendar checkpoint:** approximately 2027-03-28 if the account creation date was 2026-09-28. The AWS console should be used to confirm the exact date and remaining credits.

**At expiry:** AWS states the Free account closes/suspends automatically; data/resources are retained for 90 days, during which the account can be upgraded to Paid to restore access. Free-plan eligibility cannot be extended beyond six months.

**Human intervention:** Required before expiry if Anderson House needs to preserve running AWS workloads/resources beyond the Free plan. Options:
- upgrade to Paid and use pay-as-you-go carefully;
- migrate/stop workloads before expiry;
- continue only services legitimately available under continuing free usage where applicable.

**Do not:** open replacement AWS accounts merely to obtain repeated new-customer Free Plans. AWS states Free Plan/credits are only for new customers and people who previously had an AWS account are ineligible.

---

## Google Cloud

**Relationship:** Google Cloud Terms/Agreement + Free Trial terms + service-specific terms/AUP.

**Anderson House activation evidence:** Free Trial active by 2026-09-28.

**Current trial rule:** $300 Welcome credit / 90-day Free Trial; trial ends when either the credit is spent or 90 days pass.

**Best-supported calendar checkpoint:** approximately 2026-12-27 from a 2026-09-28 start. Google Cloud Billing Overview is authoritative for exact days/credit remaining.

**At expiry:** If not manually upgraded, workloads are shut down. Google states there is a 30-day period to upgrade/recover before stored workloads/data are deleted.

**Human intervention:** Required before expiry if Anderson House wants those workloads to continue. Upgrade is manual; Google does not automatically bill after the Free Trial unless the account is upgraded to paid.

**After upgrade:** eligible Free Tier products can still be used within their monthly limits; usage beyond free allowances is billable.

**Do not:** create another personal trial simply to reset the trial. Google says Free Trial eligibility applies to users who have not previously signed up for the Free Trial and have not been a paying customer of Google Cloud/Maps/Firebase. Separate genuinely eligible users in an organization may independently qualify under Google's stated eligibility rules.

---

## Cloudflare

**Relationship:** Cloudflare self-serve terms/service-specific terms + Workers Free plan and applicable product terms.

**Anderson House activation evidence:** Workers Free plan active by 2026-09-28.

**Current plan rule:** Workers Free is an ongoing plan with monthly usage limits; the current pricing documentation does not describe a fixed trial expiry requiring renewal.

**Human intervention:** No periodic renewal is presently required just to remain on Workers Free. Monitor limits and terms. Paid Workers currently has a minimum monthly charge if deliberately upgraded.

**Additional accounts:** Cloudflare currently explicitly allows eligible users to create up to five additional Free accounts after seven days of user tenure, but Cloudflare terms prohibit using services in ways intended to circumvent service-specific limits/quotas. Additional accounts therefore need a legitimate account/organizational purpose, not quota evasion.

---

## GitHub

**Relationship:** GitHub Terms of Service + GitHub Free plan + product-specific usage/billing rules.

**Current plan rule:** GitHub Free itself has no fixed trial expiry requiring annual renewal. Usage-based allowances such as Actions reset on their billing cycle.

**Current relevant included allowance:** GitHub Free currently includes 2,000 Actions minutes/month for private-repository Actions usage, with separate included storage allowances. Public-repository Actions may have different billing treatment under GitHub rules.

**Human intervention:** No periodic plan renewal is required to keep GitHub Free. Monitor Actions/storage usage and budgets/alerts if billable products are enabled.

**Multiple accounts:** GitHub's current Terms state one person/legal entity may maintain no more than one free personal Account, with one additional free machine account allowed for automation. Do not create extra personal free accounts to multiply allowances.

---

# Anderson House Continuity Rule

For every external resource maintain:

**PROVIDER → AGREEMENT → ACCOUNT/PLAN → START DATE → FREE/TRIAL LIMIT → EXPIRY/RESET → HUMAN DECISION DATE → CONTINUITY ROUTE → LEGAL ACCOUNT RULE → EVIDENCE DATE**

## Coordinator check

- **Expiry-based resource?** Create a human decision alert before expiry.
- **Credit-based resource?** Also check for early exhaustion.
- **Ongoing free plan?** No fake renewal date; monitor quota/terms instead.
- **Provider changes terms?** Bill resurvey → Ted adapts route → Linda verifies.
- **Free period ending?** Never assume opening another account is permissible. Check provider eligibility/anti-circumvention terms first.
- **No-cost continuity preferred:** first survey legitimate Always Free/Free Tier routes, workload migration, lower-resource alternatives, and permitted account structures before any paid upgrade.

## Current decision dates

- **Google Cloud:** review about one week before ~2026-12-27 → target reminder ~2026-12-20.
- **AWS:** review about one week before ~2027-03-28 → target reminder ~2027-03-21.
- **Cloudflare:** no fixed free-plan expiry currently identified.
- **GitHub Free:** no fixed free-plan expiry currently identified.

