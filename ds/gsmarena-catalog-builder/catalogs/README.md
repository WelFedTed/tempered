# Full Catalog Snapshot

`gsmarena-full-catalog.gscatalog` is a ready-to-restore public catalog snapshot generated on 2026-07-28.

- File size: 41.14 MiB
- SHA-256: `204E5F89197F886B84AEB109B0EBF4FA9BE78763CBA3D369A08949A9AF52D26D`

It contains:

- 14,710 discovered devices
- 14,710 full-spec device records
- A thumbnail URL for every device
- Saved image, 3D/360, and review data available at the time of the snapshot
- Completed discovery and device identities needed for accurate counters

Local application logs, observed crawler IP addresses, server instance IDs, and recovery incidents have been removed from the public copy.

The project license covers the builder code. Product names and source-site data in the snapshot remain the property of their respective owners.

## Import

1. Start the catalog builder locally or open a deployed instance.
2. Pause the scanner if it is running.
3. Select **Restore catalog & queues**.
4. Choose `catalogs/gsmarena-full-catalog.gscatalog`.
5. Confirm that the browser's current catalog may be replaced.

The browser reads the selected file into IndexedDB. Importing it does not upload the catalog to a shared project database.

## Regenerate

Maintainers can create a publishable copy from a private resumable backup:

```powershell
node .\scripts\prepare-public-catalog.mjs `
  "C:\path\to\private-session.gscatalog" `
  ".\catalogs\gsmarena-full-catalog.gscatalog"
```

Run `npm run release:check` afterward to verify the public artifact.
