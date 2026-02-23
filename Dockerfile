FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

ARG MODEL_URL=https://huggingface.co/nomic-ai/nomic-embed-text-v1.5-GGUF/resolve/main/nomic-embed-text-v1.5.Q8_0.gguf
ARG LLAMA_DOWNLOAD=https://github.com/ggml-org/llama.cpp/releases/download/b8123/llama-b8123-bin-ubuntu-x64.tar.gz

RUN apt-get update -y && apt-get upgrade -y && apt-get install nginx vim \
    postgresql-common libpq-dev python3-gdal curl ca-certificates \
    libopenblas-dev libopenblas0 libgomp1 -y
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

COPY nginx.default /etc/nginx/sites-available/default

WORKDIR /models
RUN curl -L ${MODEL_URL} -o model.gguf

WORKDIR /llama-dir
RUN curl -L ${LLAMA_DOWNLOAD} \
    -o llama.tar.gz && \
    tar -xzf llama.tar.gz && \
    rm llama.tar.gz

COPY . /opt/app
WORKDIR /opt/app
RUN mkdir -p /opt/app
RUN uv sync --no-install-project

# start server
EXPOSE 80
STOPSIGNAL SIGTERM
CMD ["/opt/app/start-server.sh"]