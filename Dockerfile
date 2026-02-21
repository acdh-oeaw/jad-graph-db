FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# install nginx posgtes and gdal
RUN apt-get update -y && apt-get upgrade -y && apt-get install nginx vim \
    postgresql-common libpq-dev python3-gdal curl zstd -y
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

# install ollama
RUN curl -fsSL https://ollama.com/install.sh | sh
RUN ollama serve & \
    OLLAMA_PID=$! && \
    sleep 5 && \
    ollama pull nomic-embed-text && \
    kill $OLLAMA_PID

COPY nginx.default /etc/nginx/sites-available/default

COPY . /opt/app
WORKDIR /opt/app
RUN mkdir -p /opt/app
RUN uv sync --no-install-project

# start server
EXPOSE 80
STOPSIGNAL SIGTERM
CMD ["/opt/app/start-server.sh"]