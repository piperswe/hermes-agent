# Unmodified v0.23.1 baseline and ownership handoff

## Pin and boundaries

Application source is NousResearch/hermes-agent tag v0.23.1, annotated tag object
`b65acf3fdc1d43bd889211ea8e37032974b395a5`, peeled commit
`3b421578588243f920886e6fe79a6faa87ea026e`.
The application build context is `git archive` of that exact commit, NOT the fork
working tree. The only generated addition to that context is upstream's canonical
install stamp. The official Dockerfile and dependency locks are unchanged. Its
frontend stages build dashboard, TUI and browser webapp; the image smoke gate
checks all three products, source stamp, SQLite and CLI version.

The fork changes only workflows, operations and deployment packaging. No callback,
plugin or core changes are included. Inherited upstream workflow entrypoints are
removed on the packaging branch (preserved in upstream/history), not enabled.
The default branch is `baseline-v0.23.1`, initially the exact release; merging the
packaging PR activates only the Piper workflows. Never use `gh repo sync` on the
deployment branch. `main` remains upstream history, not the deploy/build branch.

The running image's install stamp already names this exact commit and version;
this baseline is not a source downgrade. `/etc/hermes/image-provenance.json`
reports the upstream packaging placeholder version `0.0.0`; the install stamp and
CLI report `0.23.1`. Do not infer compatibility from that placeholder alone.
Dependency rebuilds and boot-time PM generation refresh can still change runtime
environments. Existing Honcho plugin ref and persisted configuration are unchanged.
No real-data compatibility or restore exercise has been performed by this work.

## Build, review and promotion

`piper-baseline.yml` is independently executable in GitHub Actions. It runs upstream
state/persistence and stamp regression tests in a temporary home, packaging unit
tests, verifies the exact upstream tag object and commit, builds the official full
image, and tests it with no network, no provider credentials and no production
mount. It pushes that tested local image (not a second build) only on trusted push
or manual dispatch. Images have unique version/packaging-commit/run tags, OCI source
and revision labels, and a receipt containing source SHA, packaging SHA, registry
digest and run URL. The current cluster is amd64, so only linux/amd64 is built.
Publication is NOT deployment. No Kubernetes credentials or cross-repository write
secrets are installed in the fork.

Download `baseline-<run_id>` from a successful run. `receipt.json`, `app.yaml`,
`image-inspect.json`, `registry-inspect.txt`, `push.txt` and `version.txt` are the
promotion evidence. Re-rendering with `operations/baseline.py` accepts only a full
sha256 digest and requires exactly two application image substitutions (gateway
and configure-honcho); sidecar/init images are untouched. Review the resulting diff
and open a kube-manifests PR. A build never pushes to kube-manifests main.
The staged kube-manifests PR has a suspended Flux Kustomization, prune disabled and
Orphan deletion policy. Merging it alone must NOT start application reconciliation.
A later explicit activation PR unsuspends it only after the ownership transfer.

`piper-upstream.yml` detects final SemVer releases (not prereleases, drafts or old
calendar tags), fetches the exact tag and opens a draft merge PR with tag object
and peeled commit. It restores only the already-reviewed Piper workflows, so
upstream publishing code is not enabled. Non-workflow merge conflicts fail closed
for manual resolution. It never changes the v0.23.1 pin, merges its PR, or promotes
an image. The baseline source guard intentionally blocks newer application source
until a separate upgrade plan changes the pin and verifies state/plugin compatibility.
GITHUB_TOKEN-created PRs may require manually dispatched CI. The repository setting
allowing Actions to create PRs must permit it; no broader PAT is provisioned here.
The schedule begins only after the packaging PR reaches the default branch.
Current repository readback: `can_approve_pull_request_reviews=false` in both fork
and kube-manifests. GitHub uses this setting for Actions-created PRs as well as
approving reviews. Automated PR creation is therefore an activation blocker; this
work does NOT widen that permission. Until the user separately approves changing
that setting (or supplies an appropriately scoped already-authorized app), the
external operator creates PRs with its existing `gh` login. Builds and artifact
recovery do not need this permission.

## Exact ownership split

Flux eventually owns these seven existing objects in namespace `hermes`:
Deployment/hermes, ConfigMap/hermes-config, Service/hermes,
NetworkPolicy/hermes-ingress, BackendTLSPolicy/hermes-backend-tls,
HTTPRoute/hermes-http, HTTPRoute/hermes-https.

Pulumi continues owning Namespace/hermes, PVC/hermes-data, generated health API
Secret, Hermes Certificate, DNS, shared trust, all Honcho resources and its external
PostgreSQL database/credentials. Flux must not declare or prune any of these.
The PVC is the existing Bound 40Gi RWO `vultr-block-storage-retain` claim, PV
`pvc-c273f2aaa0334396`, reclaim policy Retain. It is NOT recreated or copied.
The service's allocated clusterIP and Kubernetes defaulted networking fields are
omitted from desired manifests, not intentionally replaced.

All runtime mounts and connectivity are preserved: `/opt/data`, Docker socket,
Docker CLI/buildx/compose volumes, `/etc/honcho-trust` via outbound-trust,
nginx config, service TLS and internal-trust, bootstrap config and Honcho credential
references. `/opt/data` includes state.db/WAL, profiles, auth, .env, skills, plugins,
cron, scripts, home/toolchain, workspaces and runtime dependency generations.
The deployment retains names/selectors, one replica, Recreate strategy, UID/GID
10000, root s6 bootstrap, DinD privilege, disabled SA token mount, node selector,
probes/resources, TLS, routes and ingress policy. No new ingress or credentials.
Keep `hermes.piperswe.me` and its existing authentication callbacks unchanged.

## Named approvals and ordering (none executed here)

1. APPROVAL RETENTION PREVIEW/APPLY: review and merge the mycloud retention PR.
   From the external operator's normal checkout/stack `piper/mycloud/dev`, export
   an encrypted state checkpoint to secure storage and take a fresh full preview.
   Verify the change is retention metadata only: no pod-template diff, replacement,
   deletion, PVC/namespace mutation or unrelated provider update. Apply only the
   reviewed scope. Read back the exported state to prove `retainOnDelete: true`
   is persisted for each of the seven exact URNs BEFORE unregistering anything.
   This PR leaves every resource registration in place; it does not transfer ownership.
2. APPROVAL SAFE DRAIN/BACKUP: coordinator enumerates active foreground/background
   agents, scheduled work and Docker workloads. Wait for or explicitly stop them;
   do not cut the gateway out from under an active agent. The 60-second grace period
   is not a guarantee a long agent completes. Block new work and stop the sole
   gateway from an external control surface. Never start a second replica with the
   same state or Telegram bot token. Pause Honcho ingestion/derivation as needed
   for a coordinated logical cut; preserve its queue and PostgreSQL backup/WAL
   recovery point. Record both sides' restore point and any external side effects.
   Take an encrypted off-PVC full `/opt/data` backup after writers stop, including
   SQLite WAL/SHM or a verified SQLite backup/checkpoint; a live file copy or Retain
   PV policy is not a consistency guarantee. Verify checksums and restore into an
   isolated scratch volume with no production credentials/network. Do not reuse
   real state for CI. A tested restore and secure backup destination are prerequisites,
   not claims made by this baseline work. DinD emptyDir images/cache are disposable;
   its active jobs are not preserved on pod replacement.
3. APPROVAL OWNERSHIP RELEASE: keep Flux suspended. Prepare a separate mycloud PR
   unregistering ONLY the seven listed resources, preserving namespace/PVC/secrets,
   Certificate, Honcho and DNS. Preview against the retained checkpoint; verify
   removals are retain/orphan operations, not Kubernetes DELETEs. Apply only after
   explicit approval; export state and read back the live objects to prove the
   exact seven disappeared from Pulumi state but still exist with unchanged UIDs.
   Do not use unreviewed `pulumi state delete` or remove protected storage.
   Keep an external operator holding the maintenance/recovery procedure throughout.
4. APPROVAL PRODUCTION PROMOTION/FLUX ADOPTION: verify published digest provenance,
   registry pull access for existing `hermes/default` SA `ghcr-pull`, desired/live
   rendered diff, complete backups and seven-resource ownership release. Approve a
   kube-manifests activation PR changing `suspend: true` to false; no force replace.
   Flux server-side apply may need explicit ownership-conflict review after Pulumi
   release; do not set force or delete/adopt live resources as a shortcut. Coordinate
   a single Recreate rollout so no simultaneous gateway writers ever run. Do not
   combine unreviewed config/plugin migrations with the baseline image change.
5. Verify exact digest and install stamp, mounts/PVC UID, single gateway, health,
   mTLS/route/auth behavior, allowed Telegram round trip, provider/Honcho connectivity,
   cron/profile/session retention and one explicitly authorized scheduled job. Report
   real execution results, not only Flux Ready. Only then close the maintenance gate.

## Recovery outside Hermes

The operator can use GitHub web/gh, Flux and kubectl from its own machine while
Hermes is down. No callback or running Hermes process is needed. After merging the
packaging PR, rebuild with:

    gh workflow run piper-baseline.yml -R piperswe/hermes-agent --ref baseline-v0.23.1
    gh run list -R piperswe/hermes-agent --workflow piper-baseline.yml
    gh run download RUN_ID -R piperswe/hermes-agent -n baseline-RUN_ID

Review receipt and app.yaml, clone kube-manifests separately, create a feature
branch, copy app.yaml to `apps/hermes/app/app.yaml`, render/validate, and open a PR.
After activation, a reviewed revert PR to the previous known-good digest is the
normal rollback; Flux reconciles without Hermes. Before activation, Pulumi remains
the sole manager and its existing digest is the recovery source of truth:
`nousresearch/hermes-agent@sha256:276d44685c65c0cb2a25f190b63c65c8906f9dc76486fb1c05ae71b5826bda08`.
Do not blindly run `kubectl rollout undo` against an active GitOps reconciler.

If a boot or upgrade migrated state/dependency generations, image-only downgrade
is not assumed safe: stop the sole writer, restore the paired pre-change full
Hermes/Honcho recovery points into verified storage, then start the known-good
image with compatible config/plugins. Review any lost/new external actions first.
Never perform a destructive SQLite or Honcho schema downgrade as part of rollback.
Keep the old digest and backups until post-cutover validation is accepted.

## Sources checked

Official docs (live):
https://hermes-agent.nousresearch.com/docs/llms.txt
https://hermes-agent.nousresearch.com/docs/user-guide/docker
https://hermes-agent.nousresearch.com/docs/getting-started/updating
https://hermes-agent.nousresearch.com/docs/user-guide/features/plugins
https://fluxcd.io/flux/components/kustomize/kustomizations/
https://www.pulumi.com/docs/iac/concepts/resources/options/retainondelete/

Version-specific authority is the exact upstream tag source, especially Dockerfile,
docker/build_agent.py, scripts/write_install_stamp.py, scripts/run_tests.sh,
.github/actions/setup-pm and tests/docker. Current docs are not permission to
silently substitute newer code or use existing production state in a test.
