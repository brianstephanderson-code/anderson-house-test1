# The 3 Amigos Recovery Kit

Purpose: restore one broken cloud doorway without rebuilding the whole system.

## Recovery rule

CHECK -> identify broken doorway -> restore only that doorway -> run runtime test -> DONE

Do not rebuild healthy providers.

## AWS doorway

Known components:
- Deploy role: AndersonHouseGitHubDeploy
- Lambda: Ahhello
- GitHub OIDC authentication
- Region is supplied by GitHub variable AWS_REGION

GitHub variables used:
- AWS_ROLE_TO_ASSUME
- AWS_REGION
- AWS_LAMBDA_FUNCTION
- AWS_LAMBDA_EXECUTION_ROLE

Recovery:
1. Confirm the GitHub variables still exist.
2. Confirm the deploy role still trusts GitHub OIDC for this repository and main branch.
3. Confirm Lambda Ahhello exists in the configured region.
4. Re-run The 3 Amigos Deploy targeting AWS.
5. Run The 3 Amigos Runtime Feed and require AWS runtime success.

Known non-blocking gap:
- CloudWatch metric-read permission is optional telemetry, not required for Lambda runtime.

## Google doorway

Known components:
- Project is supplied by GCP_PROJECT_ID
- Region by GCP_REGION
- Function: ahhello
- Runtime: Node.js 22 / Gen2
- Service account by GCP_SERVICE_ACCOUNT
- Workload Identity Provider by GCP_WIF_PROVIDER

GitHub variables used:
- GCP_PROJECT_ID
- GCP_REGION
- GCP_FUNCTION_NAME
- GCP_WIF_PROVIDER
- GCP_SERVICE_ACCOUNT

Recovery:
1. Confirm the GitHub variables still exist.
2. Confirm the Workload Identity Provider exists.
3. Confirm the service account still exists and accepts the GitHub identity path used by the workflow.
4. Confirm Gen2 function ahhello exists in the configured region.
5. Re-run The 3 Amigos Deploy targeting Google.
6. Run Google Runtime Feed or The 3 Amigos Runtime Feed and require authenticated runtime success.

Important:
- Google deployment normally takes about 45-50 seconds even when runtime code is tiny.
- Treat this as deployment overhead, not runtime slowness.
- Preferred operating rule: deploy rarely, feed heavily.

## Cloudflare doorway

Known components:
- Worker: ah-word-count
- Runtime endpoint is defined in the The 3 Amigos workflows.

GitHub secrets used:
- CLOUDFLARE_API_TOKEN
- CLOUDFLARE_ACCOUNT_ID

Recovery:
1. Confirm both GitHub secrets still exist.
2. Confirm worker ah-word-count still exists.
3. Re-run The 3 Amigos Deploy targeting Cloudflare.
4. Run The 3 Amigos Runtime Feed and require Cloudflare runtime success.

## GitHub control layer

Repository:
- brianstephanderson-code/anderson-house-test1
- Branch: main

Core workflows:
- .github/workflows/function-lane-deploy.yml
- .github/workflows/google-runtime-feed.yml
- .github/workflows/function-land-runtime-feed.yml
- .github/workflows/function-land-dispatcher.yml

Operating rule:
- Deploy only when function code or provider packaging changes.
- Normal work should go through runtime feeds or dispatcher without redeploying providers.

## Quick fault isolation

If one provider fails:
- Check only that provider first.
- Do not touch the other two if they are green.

If all three fail:
- Check GitHub permissions, variables, secrets, and workflow authentication first.

If deployment fails but runtime still works:
- Keep using the existing deployed function while repairing the deploy path.

If runtime fails but deployment is green:
- Check authentication, endpoint, provider health, then function response validation.

## Verified recovery baseline

- Google runtime-only feed: 10 -> 50 -> 100 requests, success.
- The 3 Amigos Runtime Feed: AWS + Google + Cloudflare all successfully processed 160 runtime jobs each without redeployment.
- The 3 Amigos Dispatcher: 30 parcels, 10 per provider, all returned, one joined DONE.

## Senior rule

BUILD FUNCTION ONCE -> DEPLOY ACROSS THE LAND -> FEED REPEATEDLY -> REDEPLOY ONLY WHEN THE FUNCTION CHANGES
