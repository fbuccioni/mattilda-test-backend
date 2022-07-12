ARG FROM_TAG=latest
FROM python:3.8-alpine


# Package installation

# Base
RUN apk --no-cache add supervisor libuv

# Binary needed
#RUN apk --no-cache add mariadb-connector-c-dev py3-gdal gdal-dev geos-dev binutils \
#    libpng libjpeg-turbo

# Development dependencies
RUN apk add --no-cache --virtual .build-deps g++ gcc musl-dev libuv-dev make
#    libjpeg-turbo-dev zlib-dev

# Build ENV
ENV DATABASE_DEFAULT_URL="sqlite+aiosqlite:///:memory:"

# Add application
RUN mkdir -p /app
WORKDIR /app

# copy app into container
COPY app/ ./app
COPY main.py requirements.txt ./

# Upgrade pip
RUN pip install --upgrade pip

# Install requirements 
RUN pip install -r requirements.txt

# Remove development packages
RUN apk del .build-deps

# copy configs
COPY automation/docker/conf/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

HEALTHCHECK --interval=5s --timeout=3s CMD curl --fail http://localhost:80 || exit 1
EXPOSE 80
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
