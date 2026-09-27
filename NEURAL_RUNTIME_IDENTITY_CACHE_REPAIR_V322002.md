# Neural Runtime Identity & Cache Repair — v3.22.0.2

Root cause: `torch._dynamo`/Inductor cache initialization called `getpass.getuser()` and ultimately `pwd.getpwuid(65532)`, but the hardened numeric runtime UID has no passwd entry. v3.22.0.2 sets `HOME=/tmp`, `USER=LOGNAME=scworkspace`, `XDG_CACHE_HOME=/tmp/.cache`, and `TORCHINDUCTOR_CACHE_DIR=/tmp/torchinductor` before Dynamo import and at the Docker/Compose layer. Security hardening is unchanged.
