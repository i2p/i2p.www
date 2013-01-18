source ./translation.vars

TZ=UTC env/bin/pybabel compile -d $TRANSDIR
