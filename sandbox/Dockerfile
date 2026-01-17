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
    ca-certificates \
    gnupg \
    lsb-release \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Docker
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-compose-plugin \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Kubernetes tools (kubectl, helm, kind)
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    chmod +x kubectl && \
    mv kubectl /usr/local/bin/ && \
    curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash && \
    curl -Lo ./kind "https://kind.sigs.k8s.io/dl/v0.24.0/kind-linux-amd64" && \
    chmod +x ./kind && \
    mv ./kind /usr/local/bin/

# Install Ollama dependencies
RUN apt-get update && apt-get install -y zstd && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Install Python packages for LLM and AI (using --break-system-packages for Ubuntu 24.04)
RUN pip3 install --break-system-packages --no-cache-dir \
    langgraph \
    langchain \
    langchain-core \
    langchain-community \
    ollama \
    langchain-openai \
    langchain-anthropic \
    redis \
    kubernetes \
    python-dotenv \
    pyyaml

# Generate locale
RUN locale-gen en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

# Create a non-root user with sudo privileges
RUN useradd -m -s /bin/bash sandbox && \
    echo 'sandbox:sandbox' | chpasswd && \
    usermod -aG sudo sandbox && \
    usermod -aG docker sandbox

# Set working directory
WORKDIR /home/sandbox

# Switch to sandbox user
USER sandbox

# Default command
CMD ["/bin/bash"]
