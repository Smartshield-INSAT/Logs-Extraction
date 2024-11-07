# Stage 1: Build
FROM debian:bookworm-slim AS build

# Set environment variables for non-interactive installation and versions
ENV DEBIAN_FRONTEND=noninteractive \
    ARGUS_VERSION=5.0.0 \
    CLIENTS_VERSION=5.0.0

# Install dependencies
RUN apt-get update && \
    apt-get install -y gcc make flex bison zlib1g-dev libpcap-dev wget

WORKDIR /argus

# Download and extract source code from GitHub releases
RUN wget https://github.com/openargus/clients/archive/refs/tags/v${CLIENTS_VERSION}.tar.gz -O clients-${CLIENTS_VERSION}.tar.gz && \
    tar -xvf clients-${CLIENTS_VERSION}.tar.gz && \
    wget https://github.com/openargus/argus/archive/refs/tags/v${ARGUS_VERSION}.tar.gz -O argus-${ARGUS_VERSION}.tar.gz && \
    tar -xvf argus-${ARGUS_VERSION}.tar.gz

# Build and install argus and clients
RUN cd clients-${CLIENTS_VERSION} && \
    LIBS="-lz" ./configure && \
    make && \
    make install && \
    cd ../argus-${ARGUS_VERSION} && \
    LIBS="-lz" ./configure && \
    make && \
    make install

# Copy CICFlowMeter files to /CICFlowMeter in the build stage
COPY ./CICFlowMeter-4.0 /CICFlowMeter

# Stage 2: Runtime (Switch to Ubuntu)
FROM ubuntu:22.04

# Install runtime dependencies, including Java JDK 8
RUN apt-get update && \
    apt-get install -y zlib1g libpcap0.8 libpcap-dev libtirpc3 openjdk-8-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Verify Java version (optional)
RUN java -version

WORKDIR /CICFlowMeter

# Copy built files from the build stage
COPY --from=build /usr/local /usr/local
COPY --from=build /CICFlowMeter /CICFlowMeter

# Set a default command (optional)
CMD ["bash"]
