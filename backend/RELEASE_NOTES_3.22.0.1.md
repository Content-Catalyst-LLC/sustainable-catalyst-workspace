# Sustainable Catalyst Workspace v3.22.0.1

## Neural Training Runtime Production Repair

This patch repairs the production-only PyTorch optimizer initialization failure discovered during the v3.22.0 Contabo deployment smoke test.

### Root cause

The hardened PyTorch 2.10.0 neural runtime successfully started and reported healthy, but the first `torch.optim.Adam` construction lazily imported `torch._dynamo` from a FastAPI/AnyIO worker thread. In the production image this hit duplicate `precompile` registration in PyTorch's mega-cache artifact factory and returned HTTP 500.

The same runtime also emitted a startup warning that NumPy was not installed.

### Repair

- preload `torch._dynamo` on the service main import thread;
- warm the Adam optimizer integration before request threads begin executing jobs;
- serialize optimizer construction with a narrow lock while leaving the training loop unlocked;
- pin NumPy 2.2.6 in the neural runtime image;
- expose production-repair readiness fields in `/health`;
- add a worker-thread optimizer construction regression test;
- keep the existing read-only, non-root, dropped-capability container hardening unchanged.

No database migration is required. Checkpoint persistence, training resume, and accelerator execution remain disabled.
