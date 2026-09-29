# Anderson House Function Lane

One tiny function, one source of truth, three cloud adapters.

## Parent function

`core/word_count.mjs` owns the actual transformation:

`text -> word count`

Cloudflare, AWS Lambda, and Google Cloud only contain thin adapters.

## Test locally in GitHub Actions

The workflow first runs:

`node --test function-lane/test/word_count.test.mjs`

The same input must produce the same result everywhere.

## One-time cloud authorization

Do **not** put passwords, MFA codes, card data, or long-lived keys in this repository.

### Cloudflare
Create a narrowly scoped Workers API token and store it in GitHub Actions secrets as:

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

Cloudflare recommends scoping the token to the required account and Workers permissions.

### AWS
Prefer GitHub OIDC. Configure an AWS IAM role that trusts this repository, then add repository variables:

- `AWS_ROLE_TO_ASSUME`
- `AWS_REGION` (for example `us-east-1`)
- `AWS_LAMBDA_FUNCTION` (existing test function can be used)
- optional `AWS_LAMBDA_EXECUTION_ROLE` if GitHub will create a new function

No AWS access key needs to live in GitHub.

### Google Cloud
Prefer Workload Identity Federation. Add repository variables:

- `GCP_PROJECT_ID`
- `GCP_REGION`
- `GCP_FUNCTION_NAME`
- `GCP_WIF_PROVIDER`
- `GCP_SERVICE_ACCOUNT`

No service-account JSON key is required when WIF is used.

## Deployment

The workflow is manual at first so an unconfigured cloud cannot fail on every push.

GitHub -> Actions -> **Function Lane Deploy** -> **Run workflow**

Choose `all` to deploy the same function to all three providers.

After all three authorization joints are proven, change the workflow trigger to deploy automatically on approved changes to `function-lane/**`.
