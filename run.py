import os
from app import app

if __name__ == '__main__':
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    port = int(os.getenv('PORT', '5002'))
    app.run(host='0.0.0.0', debug=debug, port=port)
