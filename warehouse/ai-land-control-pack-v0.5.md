# AI LAND Control Pack v0.5

Status: GREEN

Validated live controls:
- Cloudflare health probe
- Google health probe via OIDC
- healthy-route selection
- fallback routing replay
- free-only stop gate

Live run:
- workflow: .github/workflows/ai-land-control-pack-v0.5.yml
- run id: 38250279880
- Cloudflare health: success
- Google health: success
- router: success

Routing rule:
IF Cloudflare healthy -> Cloudflare
ELSE IF Google healthy -> Google
ELSE -> BLOCK

Replay proofs:
- Cloudflare fail + Google success -> Google
- Google fail + Cloudflare success -> Cloudflare
- both fail -> BLOCK

House rule retained:
No silent paid fallback.
