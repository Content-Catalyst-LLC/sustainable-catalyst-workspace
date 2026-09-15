# Polyglot Scientific Runtime Fabric — v2.12.0

Workspace treats language as an execution property rather than a product boundary. The v2.12 fabric provides one job/provenance/policy contract across Python, SQL, R, Julia, and WebAssembly.

Python and bounded SQL execute in-process. R, Julia, and WebAssembly are registered but require server-configured runtime services. An unavailable adapter is reported as unconfigured; Workspace never accepts a client-provided URL as a fallback.

The Arrow-compatible descriptor captures column names, logical types, nullability, and row count without requiring every runtime to share a Python object model. Records JSON is the v1 transport representation; a future build can add Arrow IPC without changing the runtime envelope.
