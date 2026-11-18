# Hosted AI Value & Adoption Studio

## Current hosting and scope

- **Production Site project:** `appgprj_6afbc085af5881918f7ea2549447d9f0`.
- **Working private URL:** <https://dani-trusted-intelligence-lab-demo.danimonteirodba.chatgpt.site/studio/>.
- **Preferred custom URL:** <https://lab.danimonteiro.tech/studio/>; **not considered operational until DNS and TLS status are verified**.
- **Code:** [`web-studio/`](../web-studio/), with its own `package.json`, lockfile, UI, Worker API, D1 migration and tests.
- **Persistence:** D1 snapshots, isolated per authenticated platform user; not the local Python SQLite database.

The current Site is owner-private. Do not change its audience to public or
accept real client data based solely on this demonstration. All cases are
synthetic and its auth guarantees do not establish enterprise authorization.

## Local verification

Run the Python tests from the repository root:

```bash
python -m unittest discover -s tests -v
```

Run the hosted Studio checks from `web-studio/`:

```bash
cd web-studio
npm ci
npm test
npm run build
```

The hosted API requires a platform-authenticated user. A development preview
without that context should return `401` to protected endpoints.

## Publishing and source synchronization

**GitHub is the public canonical source repository**, but the Sites host keeps
its own internal deployment repository. The Site is not automatically built
from GitHub and the private D1 database is not stored in either Git repository.

After making and testing a change in `web-studio/`, synchronize its *contents*
to the existing Site source repository root, retaining that Site's
`.openai/hosting.json` project identity, and then publish a new version using
the Sites workflow. Conversely, verify and bring production hotfixes back
into `web-studio/` before declaring GitHub up to date. Do not copy the
repository-root Python application into the hosted Worker project.

The intentionally paused root GitHub Actions workflow must remain paused
until the owner explicitly resolves the account billing restriction.

## Domain setup — DNS provider must be verified

On 17 November 2026, the connected Namecheap dashboard showed
`danimonteiro.tech` as **registered with another registrar**. Searching its
Namecheap **Domain List** returned no matching editable domain, so we could
not safely create the records there. Domain registration and authoritative DNS
hosting are separate; this observation does not establish which nameservers
currently serve the zone.

First identify the authoritative DNS service for `danimonteiro.tech`. Add the
Site-provided CNAME and verification TXT records **there**. If the zone is
hosted in Namecheap FreeDNS or a Namecheap hosting DNS editor, use that
specific DNS interface; otherwise use the provider currently serving its
nameservers. Do not transfer the domain or change nameservers just to add
these records. Keep all existing mail, website and unrelated DNS entries.

In a DNS editor whose **Host** fields are relative to the
`danimonteiro.tech` zone, use `lab`, not the full FQDN, for the CNAME.

The Site currently provides:

| Record | Host | Value |
| --- | --- | --- |
| CNAME | `lab` | `custom-domains.chatgpt.site` |
| TXT | `_openai-site-verification.lab` | Obtain from the Site's current custom-domain settings |
| TXT | `_cf-custom-hostname.lab` | Obtain from the Site's current custom-domain settings |

Values should be copied from the current hosting control panel rather than
relying on stale instructions. After DNS propagation, refresh the custom-domain
status and confirm both domain verification and an active TLS certificate
before advertising the URL. DNS activation may take time.
