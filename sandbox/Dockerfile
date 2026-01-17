FROM ubuntu:24.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install essential tools
RUN apt-get update && apt-get install -y \
    sudo \
    curl \
    wget \
    vim \
    nano \
    git \
    htop \
    tree \
    net-tools \
    iputils-ping \
    dnsutils \
    locales \
    python3 \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Generate locale
RUN locale-gen en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

# Create a non-root user with sudo privileges
RUN useradd -m -s /bin/bash sandbox && \
    echo 'sandbox:sandbox' | chpasswd && \
    usermod -aG sudo sandbox

# Set working directory
WORKDIR /home/sandbox

# Switch to sandbox user
USER sandbox

# Default command
CMD ["/bin/bash"]
