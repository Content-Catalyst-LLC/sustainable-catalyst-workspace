FROM julia:1.11-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-venv ca-certificates && rm -rf /var/lib/apt/lists/*
ENV JULIA_DEPOT_PATH=/opt/julia-depot
RUN mkdir -p /opt/julia-depot && julia --startup-file=no -e 'using Pkg; Pkg.add(PackageSpec(name="JSON3", version="1.14.3")); Pkg.precompile()'
WORKDIR /app
COPY requirements.txt ./
RUN python3 -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt
COPY service.py runner.jl ./
ENV PATH="/opt/venv/bin:/usr/local/bin:/usr/bin:/bin"
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "8091"]
