FROM python:3.13-bookworm

CMD ["/bin/bash"]

WORKDIR /app

# install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# install
RUN pip install --no-input uv reflex reflex-chakra

# Copy application files
COPY . /app

# Create virtual environment and install dependencies
RUN uv venv && \
    # source .venv/bin/activate && \
    uv sync

# Make start.sh executable and validate script
RUN chmod +x start.sh && \
    [ -f start.sh ] || (echo "Error: start.sh missing" && exit 1)

EXPOSE 3000

ENTRYPOINT ["/app/start.sh"]
