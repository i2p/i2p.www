PROJECT=I2P
VERSION=website

TZ=UTC env/bin/pybabel extract --project=$PROJECT --version=$VERSION -F i2p2www/babel.cfg i2p2www/ > messages.pot
