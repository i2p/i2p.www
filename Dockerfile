FROM debian:oldoldstable as builder
ENV SERVERNAME=geti2p.net \
    SERVERMAIL=example@geti2p.net

# Install only build dependencies first
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python2-dev \
        python-pip \
        patch \
        python-virtualenv \
        git \
        python-polib && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy dependency files first for better layer caching
COPY etc/reqs.txt etc/
COPY etc/multi-domain.patch etc/

# Setup virtual environment and install dependencies
RUN virtualenv --distribute env && \
    . env/bin/activate && \
    pip install -r etc/reqs.txt

# Now copy the rest of the application
COPY . .

# Build steps in a single layer
RUN . env/bin/activate && \
    patch -p0 -N -r - < etc/multi-domain.patch && \
    ./compile-messages.sh && \
    echo "Git revision: $(git log -n 1 | grep commit | sed 's/commit //' | sed 's/ .*$//')" > ./i2p2www/pages/include/mtnversion

# Start second stage with same old base image
FROM debian:oldoldstable

# Install only runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        apache2 \
        apache2-utils \
        libapache2-mod-wsgi \
        python2-minimal && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /var/www/i2p.www

# Copy built artifacts
COPY --from=builder /build /var/www/i2p.www
COPY --from=builder /build/env /var/www/env

# Configure Apache and WSGI in a single layer
RUN cp etc/docker.wsgi.i2p i2p.wsgi && \
    chown -R www-data:www-data /var/www/i2p.www && \
    chmod 755 i2p.wsgi && \
    cp etc/apache2.i2p.conf /etc/apache2/sites-available/i2p.conf && \
    a2enmod wsgi && \
    a2ensite i2p && \
    sed -i 's|IncludeOptional sites-enabled|# IncludeOptional sites-enabled|g' /etc/apache2/apache2.conf && \
    sed -i '1 i\IncludeOptional sites-enabled/i2p.conf' /etc/apache2/apache2.conf

CMD service apache2 restart && tail -f /var/log/apache2/access.log /var/log/apache2/error.log