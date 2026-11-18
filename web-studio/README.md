# Trusted AI Adoption Studio — private synthetic deployment

This is the authenticated, hosted companion **within** Dani Monteiro's
[`trustworthy-ai-deployment-lab`](https://github.com/DaniMonteiroDBA/trustworthy-ai-deployment-lab)
monorepo, under `web-studio/`.
It preserves the Studio's synthetic decision workflow and `/api/*` shape. It
**does not run or replace** the original Python FastAPI/SQLite backend.

## Architecture

- **Frontend:** the reference Studio's HTML, CSS and JavaScript under `public/studio/` and `public/assets/`.
- **API:** server route `app/api/[...segments]/route.js` built with Vinext and hosted as a Cloudflare Worker.
- **Authentication:** ChatGPT Sites private access; every API route requires a signed-in user and scopes reads/writes by the platform-provided `oai-authenticated-user-id`.
- **Persistence:** Cloudflare D1, table `studio_snapshots`. Each write appends a new immutable workspace version, recording the authenticated actor, revision, action and timestamp. The unique `(user_id, revision)` index rejects stale concurrent writes.
- **Rules:** `lib/studio-core.js`, a separate JavaScript implementation of the reference synthetic evidence/review/decision workflow. Fixed evaluation fixtures are still deterministic and offline.

All three organizations, people, use cases, documents, permissions and financial assumptions in this application are fictional. **Do not submit customer, employee, research participant or confidential information.** Login proves a visitor's account identity, not a fictional document's validity or a real project's approval.

This app is a reference implementation, not a production-ready multi-tenant consulting platform. Among its limitations are snapshot-based rather than normalized operational storage, no external source verification or real AI evaluation, a bounded history of 1,000 versions per account, and no integration with the Python service.

## Development

```bash
npm run db:generate
node test-hosted-core.mjs
npm run build
```

The generated `drizzle` migration is tracked and must be applied to a **local** D1 preview separately, or through the Sites deployment workflow for the hosted database. Never replay an already-applied migration.

The local managed preview has no ChatGPT sign-in simulation. It can render the interface, but API requests without a valid platform identity return `401`; that is intentional. Hosted private access prompts the owner to sign in. API integration must be tested after authenticated access is established.

The repository-root GitHub Actions workflow is currently paused because of
an account billing restriction. The web Studio does not rely on that workflow;
see [`../docs/HOSTED_STUDIO.md`](../docs/HOSTED_STUDIO.md) for synchronization
and domain activation details.
