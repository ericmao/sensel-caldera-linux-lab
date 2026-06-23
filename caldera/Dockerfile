# SenseL Caldera server image — clones upstream at build time
ARG CALDERA_REF=5.3.0

FROM node:23 AS ui-build
ARG CALDERA_REF
WORKDIR /src
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates && rm -rf /var/lib/apt/lists/*
RUN git clone --recursive --depth 1 --branch "${CALDERA_REF}" https://github.com/mitre/caldera.git .
RUN cd plugins/magma && npm install && npm run build

FROM debian:bookworm-slim AS runtime
ARG CALDERA_REF
ARG VARIANT=slim
ENV VARIANT=${VARIANT}
ENV CALDERA_REF=${CALDERA_REF}

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl unzip python3-dev python3-pip mingw-w64 zlib1g gcc ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://go.dev/dl/go1.25.0.linux-amd64.tar.gz -o go.tar.gz \
    && tar -C /usr/local -xzf go.tar.gz && rm go.tar.gz
ENV PATH="$PATH:/usr/local/go/bin"

RUN git clone --recursive --depth 1 --branch "${CALDERA_REF}" https://github.com/mitre/caldera.git /usr/src/app

COPY --from=ui-build /src/plugins/magma/dist /usr/src/app/plugins/magma/dist

RUN cd /usr/src/app/plugins/sandcat \
    && cp ./update-agents.sh ./update-agents_orig.sh \
    && tr -d '\15\32' < ./update-agents_orig.sh > ./update-agents.sh

RUN pip3 install --no-cache-dir --break-system-packages -r /usr/src/app/requirements.txt

RUN if [ "$VARIANT" = "full" ]; then \
      git clone --depth 1 https://github.com/redcanaryco/atomic-red-team.git \
        /usr/src/app/plugins/atomic/data/atomic-red-team && \
      git clone --depth 1 --recursive https://github.com/center-for-threat-informed-defense/adversary_emulation_library.git \
        /usr/src/app/plugins/emu/data/adv_eql; \
    fi

COPY caldera-plugin-sensel /opt/sensel-plugin-baked
COPY caldera/conf/local.yml.template /usr/src/app/conf/local.yml.template
COPY caldera/entrypoint.sh /usr/local/bin/caldera-entrypoint.sh
RUN chmod +x /usr/local/bin/caldera-entrypoint.sh

EXPOSE 8888
ENTRYPOINT ["/usr/local/bin/caldera-entrypoint.sh"]
