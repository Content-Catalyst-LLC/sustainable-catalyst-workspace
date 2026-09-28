# Deploy Workspace backend v3.24.0

Production baseline: **v3.23.0**. No database migration is required.

The Contabo deployer builds v3.24.0, certifies checkpoint/resume plus evaluation/calibration/uncertainty inside the hardened neural image before switching production, then performs end-to-end Workspace jobs and artifact/receipt verification after promotion. Any post-switch failure restores v3.23.0.
