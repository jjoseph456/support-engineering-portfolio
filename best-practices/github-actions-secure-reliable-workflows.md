# Secure and Reliable GitHub Actions Workflows

Reliable CI/CD starts with small permissions, repeatable dependencies, bounded
concurrency, and enough evidence to explain a failure.

This article uses public GitHub documentation and synthetic examples. It is not
an official GitHub guide.

## 1. Start with Least Privilege

Set the default `GITHUB_TOKEN` permission to read-only and grant write access
only to the job that requires it.

```yaml
permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
```

Avoid broad repository-level write permissions when only one deployment or
commenting job needs them. Review the effective permission of reusable
workflows as well as the top-level caller.

## 2. Pin Third-Party Actions

A version tag can move. A full commit SHA identifies immutable Git content.
Pin external actions to a verified full-length commit SHA and keep the release
version in a comment for maintainability.

```yaml
- uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
  with:
    python-version: "3.12"
```

Use dependency automation or a scheduled review process to identify newer
trusted SHAs. Verify that the commit belongs to the expected action repository.

## 3. Treat Pull Request Content as Untrusted

Branch names, issue text, pull request titles, and changed files can contain
attacker-controlled values. Do not insert an expression directly into a shell
script.

Risky:

```yaml
- run: echo "${{ github.event.pull_request.title }}"
```

Safer:

```yaml
- name: Print pull request title
  env:
    PR_TITLE: ${{ github.event.pull_request.title }}
  run: printf '%s\n' "$PR_TITLE"
```

Do not execute code from an untrusted pull request with a token that can write
to the repository. If a workflow must analyze pull request content and later
post a privileged result, separate the unprivileged analysis from the
privileged reporting step.

## 4. Prefer Short-Lived Cloud Credentials

OpenID Connect lets a workflow request a short-lived cloud token instead of
storing a long-lived cloud credential as a repository secret.

```yaml
jobs:
  deploy:
    permissions:
      contents: read
      id-token: write
    environment: production
    runs-on: ubuntu-latest
    steps:
      - name: Authenticate to cloud provider
        run: echo "Use the provider's official OIDC action here."
```

The cloud trust policy must restrict which repository, branch, tag, or
environment can request the credential. An unrestricted trust relationship
removes much of OIDC's security benefit.

## 5. Protect Deployment Environments

Use environments to separate test, staging, and production. Depending on plan
and repository visibility, environments can provide:

- Required reviewers
- Deployment branch or tag restrictions
- Environment-specific secrets and variables
- Custom deployment protection rules

The deployment job cannot access environment secrets until the configured
protection rules pass.

## 6. Control Concurrency Intentionally

Repeated pushes can create duplicate work or overlapping deployments.
Concurrency groups define which runs compete with one another.

For CI, cancel superseded work:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

For production deployments, serialize changes rather than allowing two
deployments to modify the same environment at once. Choose cancellation or
queueing based on whether an interrupted deployment is safe.

Use the workflow name in the concurrency key so unrelated workflows do not
cancel one another accidentally.

## 7. Make Failures Reproducible

A supportable workflow makes the failure visible without exposing secrets.
Capture:

- Workflow and job identifiers
- Commit SHA and triggering event
- Runner type, image, and relevant tool versions
- Exact failed step
- Exit code and sanitized error
- Correlation or request identifiers
- Whether a rerun used the same commit and configuration

Add `timeout-minutes` to jobs that can hang. Use explicit shell error handling
so a failed command cannot be hidden by a later successful command.

```yaml
- name: Validate configuration
  shell: bash
  run: |
    set -euo pipefail
    python -m json.tool config.json > /dev/null
```

## 8. Use Caches as an Optimization

A cache should improve runtime, not become a required source of truth.

- Build successfully after a cache miss.
- Use a key that changes when relevant dependencies change.
- Avoid storing secrets or generated credentials.
- Separate trusted and untrusted workflow contexts.
- Record whether a failure occurs with a clean cache.

When diagnosing an inconsistent build, compare a clean run with a cached run
before concluding that the runner or platform is at fault.

## 9. Keep Workflows Small and Composable

Use reusable workflows for organization-wide policy and repeated job
sequences. Use composite actions for repeated step-level behavior.

Document:

- Required inputs
- Optional inputs and defaults
- Required secrets
- Required token permissions
- Outputs
- Supported runner environments
- Versioning and compatibility policy

A reusable workflow should fail early with a clear validation message when a
required input or permission is missing.

## 10. Verify Recovery

A green rerun is useful evidence only when it tests the original failure
condition.

After a change:

1. Trigger the same workflow path.
2. Use the same relevant inputs and permissions.
3. Confirm the previously failing step succeeds.
4. Confirm downstream artifacts or deployments are valid.
5. Run a second time if the original failure was intermittent.

State what proved recovery. Do not present a configuration change as the root
cause unless the evidence supports that conclusion.

## Review Checklist

- [ ] Default token permissions are read-only.
- [ ] Write permissions exist only where required.
- [ ] External actions use verified full commit SHAs.
- [ ] Untrusted values are passed through environment variables.
- [ ] Pull request code does not run with unnecessary write access.
- [ ] Cloud authentication uses constrained OIDC where supported.
- [ ] Production uses an environment and appropriate protection rules.
- [ ] Concurrency behavior is explicit.
- [ ] Jobs have useful timeouts and deterministic shell behavior.
- [ ] Cache misses do not break the build.
- [ ] Logs provide enough sanitized evidence to reproduce a failure.
- [ ] Recovery is tested against the original symptom.

## Public Sources

- GitHub Actions secure use reference:
  https://docs.github.com/en/actions/reference/security/secure-use
- Workflow syntax:
  https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
- OpenID Connect for cloud providers:
  https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-cloud-providers
- Controlling deployments:
  https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/control-deployments
- Controlling workflow concurrency:
  https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency
- Managing Actions settings:
  https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository
