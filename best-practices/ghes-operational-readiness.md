# GitHub Enterprise Server Operational Readiness

GitHub Enterprise Server is a production platform with application, storage,
network, identity, and operational dependencies. Readiness means more than
having a running appliance: administrators must be able to detect degradation,
restore data, perform upgrades, and execute failover safely.

This article uses only public GitHub documentation. It does not include
customer environments, internal procedures, or private diagnostic signatures.

## 1. Use Documentation for the Exact Release

GitHub Enterprise Server documentation is versioned. Commands, requirements,
features, and upgrade paths can differ between releases.

Before a change:

1. Record the current release and target release.
2. Select the matching version of the documentation.
3. Review release notes and known upgrade issues.
4. Use the Upgrade assistant to determine a supported path.
5. Verify dependent component compatibility.

Do not copy a command from an article for a newer release without confirming
that it applies to the installed version.

## 2. Monitor Capacity Before It Becomes an Incident

Track trends instead of waiting for a threshold to become critical:

- CPU and load
- Memory pressure
- Root and data-disk utilization
- Storage latency and throughput
- Application and authentication response time
- Git and API request volume
- Background-job health
- Replication health
- Backup completion and duration

GitHub Enterprise Server supports built-in monitor dashboards and external
monitoring. Current releases also support OpenTelemetry metrics, while collectd
remains available during the transition.

Alerting should provide time to act. A disk alert that fires only when no safe
cleanup or expansion window remains is not an operational control.

## 3. Treat Backups and High Availability as Different Controls

High availability reduces service disruption by maintaining a replica.
Backups provide recoverable data that can be restored into another environment.
A replica is not a substitute for a backup.

A backup program should define:

- Backup location and access control
- Schedule and retention
- Encryption and key ownership
- Completion monitoring
- Version compatibility
- Restore procedure
- Restore-test frequency
- Recovery point and recovery time objectives

The most important backup signal is a successful restore test. A completed
backup command does not prove that the organization can recover within its
required timeframe.

## 4. Rehearse Restore and Failover

Restore and failover are separate procedures and should be practiced
independently.

For a restore exercise:

1. Select an approved backup.
2. Restore into an isolated test environment.
3. Verify authentication, repositories, Git operations, API requests, and
   critical integrations.
4. Record the actual recovery time.
5. Document gaps and assign corrective actions.

For a high-availability exercise:

1. Confirm replica health and replication status.
2. Define traffic redirection and DNS responsibilities.
3. Document the promotion and rollback decision.
4. Verify service after promotion.
5. Confirm the future replication topology.

Do not perform a first failover during an unplanned outage.

## 5. Prepare Upgrades as Controlled Changes

For feature upgrades, public GitHub guidance includes:

- Use the supported upgrade path.
- Prefer the latest patch release of the target feature version.
- Test the upgrade on a staging instance.
- Complete capacity checks.
- Create a current backup and required virtual-machine snapshot.
- Schedule and communicate a maintenance window.
- Allow background migrations to complete between upgrade steps.

Build a written acceptance checklist before the maintenance window. Include:

- Sign-in
- Repository browsing
- Git clone, fetch, and push over required protocols
- API requests
- Webhook delivery
- Authentication and identity integrations
- GitHub Actions, if enabled
- Code-security features, if enabled
- Monitoring and backup status

Successful installation of the package is not the same as successful service
validation.

## 6. Track External Dependencies

An appliance can be healthy while an external dependency prevents users from
working. Maintain an owner and validation method for:

- DNS
- NTP
- TLS certificates
- Identity provider
- SMTP
- Proxy and firewall rules
- Load balancer
- Object storage used by enabled features
- Monitoring destination
- Backup destination

Time synchronization is especially important for authentication, certificates,
logs, and distributed operations. GitHub recommends configuring preferred NTP
servers and ensuring that the required network path is available.

## 7. Build Version-Aware Runbooks

Each runbook should state:

- Supported GitHub Enterprise Server versions
- Deployment topology
- Required role and access
- Preconditions
- Expected output
- Stop conditions
- Rollback or recovery path
- Verification steps
- Escalation evidence

Avoid runbooks that contain only commands. Explain what each observation means
and what evidence allows the operator to continue.

## 8. Collect Evidence Before Changing the System

During an incident, establish:

- Customer-visible impact
- Start time and scope
- Recent changes
- Capacity and service-health signals
- Replication and backup status
- External dependency health
- Affected and unaffected operations

GitHub Enterprise Server can generate support bundles containing diagnostic
data. Protect bundles according to organizational data-handling requirements
because they can contain sensitive configuration and operational information.

Collect evidence before restarting services or changing configuration whenever
the situation allows. Recovery actions can remove the evidence needed to
identify the mechanism.

## 9. Define Recovery Verification

Verification should test the original affected operation:

- A new Git operation succeeds.
- The API endpoint returns the expected response.
- A webhook is delivered and accepted.
- Authentication succeeds for the affected path.
- A workflow completes on the required runner.
- Replication returns to the expected state.
- Resource trends stabilize after mitigation.

Monitor long enough to distinguish recovery from a brief improvement.

## Operational Checklist

- [ ] Current release and supported upgrade path are documented.
- [ ] Resource, request, service, and replication monitoring is active.
- [ ] Alert thresholds provide actionable lead time.
- [ ] Backups are monitored and restore-tested.
- [ ] HA failover is rehearsed separately from restore.
- [ ] Staging is available for feature-upgrade testing.
- [ ] External dependencies have owners and health checks.
- [ ] Runbooks state version, topology, rollback, and verification.
- [ ] Support-bundle handling follows approved data controls.
- [ ] Post-change validation covers user and integration workflows.

## Public Sources

- Monitoring GitHub Enterprise Server:
  https://docs.github.com/en/enterprise-server@3.21/admin/monitoring-and-managing-your-instance/monitoring-your-instance
- Backing up and restoring:
  https://docs.github.com/en/enterprise-server@3.21/admin/backing-up-and-restoring-your-instance
- Upgrade requirements:
  https://docs.github.com/en/enterprise-server@3.21/admin/upgrading-your-instance/preparing-to-upgrade/upgrade-requirements
- Preparing to upgrade:
  https://docs.github.com/en/enterprise-server@3.21/admin/upgrading-your-instance/preparing-to-upgrade
- High availability and backups:
  https://docs.github.com/en/enterprise-server@3.21/admin/monitoring-and-managing-your-instance/configuring-high-availability/answers-to-common-questions-about-high-availability-replicas
- Configuring time synchronization:
  https://docs.github.com/en/enterprise-server@3.21/admin/configuring-settings/configuring-network-settings/configuring-time-synchronization
- OpenTelemetry metrics:
  https://docs.github.com/en/enterprise-server@3.21/admin/monitoring-and-managing-your-instance/monitoring-your-instance/opentelemetry-metrics/configuring-opentelemetry-for-your-instance
