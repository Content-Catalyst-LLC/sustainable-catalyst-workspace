FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HOME=/tmp
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       r-base-core \
       r-cran-jsonlite \
       r-cran-ggplot2 \
       r-cran-rlang \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY vendor/catalystanalyticsr /opt/catalystanalyticsr
RUN R CMD INSTALL --preclean /opt/catalystanalyticsr \
    && Rscript --vanilla -e 'library(catalystanalyticsr); p <- catalyst_core_provider_manifest(); stopifnot(as.character(packageVersion("catalystanalyticsr")) == "2.2.0", p$provider_key == "catalystanalyticsr", p$core_contract == "sc.core.analytical-runtime-provider.v1", p$runtime == "r", p$execution_host == "workspace", p$diagnostics_contract == "sc.analytics-r.statistical-diagnostics-validation.v1"); cat("Catalyst Analytics R v2.2.0 image contract PASS\n")' \
    && rm -rf /opt/catalystanalyticsr
COPY service.py runner.R provider_runner.R ./
RUN useradd --system --uid 10001 --home-dir /tmp --shell /usr/sbin/nologin sc_r_runtime
USER 10001
EXPOSE 8090
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "8090", "--workers", "1"]
