FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash coreutils procps iproute2 iputils-ping dnsutils curl ca-certificates \
    adduser systemd netcat-openbsd util-linux tar gzip file \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /lab
CMD ["bash"]
