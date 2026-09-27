# Deploy Workspace backend v3.22.0.1

The production baseline remains v3.21.0 because v3.22.0 failed its neural training smoke test and was automatically rolled back.

Copy the v3.22.0.1 backend ZIP and deployer to `/tmp` on Contabo and run the deployer there. No database migration is required. Promotion is blocked unless the repaired neural health contract and a real Adam training job both pass.
