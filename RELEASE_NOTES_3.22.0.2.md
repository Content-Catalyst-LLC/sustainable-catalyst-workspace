# Sustainable Catalyst Workspace v3.22.0.2

## Hardened Neural Runtime Identity & Cache Repair

Repairs the production-only PyTorch 2.10 Dynamo/Inductor cache initialization failure observed during the v3.22.0.1 pre-switch certification. The neural container continues to run as numeric UID `65532:65532` with a read-only root filesystem, dropped Linux capabilities, and `no-new-privileges`. The runtime now pins identity and compiler/cache environment paths to the writable `/tmp` tmpfs before importing `torch._dynamo`.

No database migration. Rollback baseline remains Workspace backend v3.21.0 because v3.22.0 and v3.22.0.1 were never promoted successfully.
