# ClawCrew Docker Image
# Multi-agent AI team framework for OpenClaw

FROM python:3.11-slim

LABEL maintainer="ClawCrew Team"
LABEL description="Multi-agent AI team framework for OpenClaw"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install -y gh \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY pyproject.toml .
COPY src/ src/
COPY workspace-*/ ./
COPY bin/ bin/

# Install ClawCrew
RUN pip install --no-cache-dir -e .

# Copy entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create directories
RUN mkdir -p /root/.openclaw /root/.clawcrew /app/artifacts

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV CLAWCREW_DOCKER=1

# Expose ports for dashboard
EXPOSE 6000 6001

# Entrypoint
ENTRYPOINT ["/entrypoint.sh"]
