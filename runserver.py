#!env/bin/python
from i2p2www import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
