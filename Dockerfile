FROM debian:stable
ENV SERVERNAME=geti2p.net
ENV SERVERMAIL=example@geti2p.net

ADD . /var/www/i2p.www

WORKDIR /var/www/i2p.www

    ## Install the dependencies
RUN apt-get update && \
    apt-get -y install apache2 apache2-utils libapache2-mod-wsgi python2-dev python-pip patch python-virtualenv git && \
    ## Start setting up the site
    rm -rfv env && \
    virtualenv --distribute env                && \  
    . env/bin/activate                          && \
    pip install -r etc/reqs.txt                 && \
    patch -p0 -N -r - <etc/multi-domain.patch   && \
    ./compile-messages.sh                       && \  
    echo "Git revision: $(git log -n 1 | grep commit | sed 's/commit //' | sed 's/ .*$//')" | tee ./i2p2www/pages/include/mtnversion && \
    ## We've now updated the site
    ## Next let's configure WSGI
    ## Set ownership of site to server
    cp etc/docker.wsgi.i2p i2p.wsgi && \
    chown -R www-data /var/www/i2p.www                    && \ 
    ## Make the WSGI script owned by the server 
    chown www-data:www-data /var/www/i2p.www/i2p.wsgi     && \  
    ## Make the WSGI script executable
    chmod 755 /var/www/i2p.www/i2p.wsgi                   && \  
    ## Copy the unmodified vhosts file to the apache2 confdir
    cp etc/apache2.i2p.conf /etc/apache2/sites-available/i2p.conf  && \  
    a2enmod wsgi                                     && \
    a2ensite i2p && \
    ls /etc/apache2 && \
    sed -i 's|IncludeOptional sites-enabled|# IncludeOptional sites-enabled|g' /etc/apache2/apache2.conf && \
    sed -i '1 i\IncludeOptional sites-enabled/i2p.conf' /etc/apache2/apache2.conf

CMD service apache2 restart && tail -f /var/log/apache2/access.log
