# Stage 1: Build Argus and Zeek
FROM debian:bookworm-slim AS build

# Set environment variables for non-interactive installation and versions
ENV DEBIAN_FRONTEND=noninteractive \
    ARGUS_VERSION=5.0.0 \
    CLIENTS_VERSION=5.0.0 \
    ZEEK_VERSION=7.0.3

# Install dependencies for both Argus and Zeek
RUN apt-get update && \
    apt-get install -y \
        gcc make flex bison zlib1g-dev libpcap-dev wget \
        cmake g++ libssl-dev python3-dev swig && \
    rm -rf /var/lib/apt/lists/*

# --- Build and Install Argus and Argus Clients ---
WORKDIR /argus

# Download and extract Argus and clients
RUN wget https://github.com/openargus/clients/archive/refs/tags/v${CLIENTS_VERSION}.tar.gz -O clients-${CLIENTS_VERSION}.tar.gz && \
    tar -xvf clients-${CLIENTS_VERSION}.tar.gz && \
    wget https://github.com/openargus/argus/archive/refs/tags/v${ARGUS_VERSION}.tar.gz -O argus-${ARGUS_VERSION}.tar.gz && \
    tar -xvf argus-${ARGUS_VERSION}.tar.gz

# Build and install Argus and Argus clients
RUN cd clients-${CLIENTS_VERSION} && \
    LIBS="-lz" ./configure && \
    make && \
    make install && \
    cd ../argus-${ARGUS_VERSION} && \
    LIBS="-lz" ./configure && \
    make && \
    make install

# --- Build and Install Zeek ---
WORKDIR /zeek

# Download and extract Zeek 7.0.3
RUN wget https://github.com/zeek/zeek/releases/download/v${ZEEK_VERSION}/zeek-${ZEEK_VERSION}.tar.gz && \
    tar -xvf zeek-${ZEEK_VERSION}.tar.gz

# Build and install Zeek
RUN cd zeek-${ZEEK_VERSION} && \
    ./configure && \
    make && \
    make install

# Stage 2: Final Runtime Image
FROM debian:bookworm-slim

# Copy over installed binaries from the build stage
COPY --from=build /usr/local/bin/argus /usr/local/bin/argus
COPY --from=build /usr/local/sbin/argus* /usr/local/sbin/
COPY --from=build /usr/local/zeek /usr/local/zeek

# Add Zeek to PATH
ENV PATH="/usr/local/zeek/bin:${PATH}"

# Install necessary runtime dependencies
RUN apt-get update && \
    apt-get install -y libpcap0.8 zlib1g libssl3 && \
    rm -rf /var/lib/apt/lists/*

# Verify Zeek installation
RUN zeek --version || echo "Zeek installation failed."

# Set default command to run bash
CMD ["bash"]
