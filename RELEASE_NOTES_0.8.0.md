# Sustainable Catalyst Workspace v0.8.0
## Cross-Product Handoffs

v0.8.0 turns Workspace into the shared personal context layer across Sustainable Catalyst. Connected-tool launches now create durable handoff records inside the originating project, receive a stable handoff ID, and preserve a return path. A new Handoff Center tracks launches, returned artifacts, and closed handoffs.

Compatible tools can return structured artifacts through a same-origin session return packet or a portable JSON return package. Returned material becomes canonical Workspace Objects with tool provenance. Outbound query strings remain privacy-minimized and carry IDs/intent only; project content is not serialized into URLs. No cloud synchronization or server-side handoff broker is introduced.
