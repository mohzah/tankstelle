import os


SECRET_KEY = 'secret-key'
# Key fur den Zugriff auf die freie Tankerkoenig-Spritpreis-API
# Fur eigenen Key bitte hier https://creativecommons.tankerkoenig.de
# registrieren.
API_KEY = 'tankerkoenig api key'
GOOGLEMAP_KEY = 'google map api key'

try:
    MONGO_URI = os.environ['OPENSHIFT_MONGODB_DB_URL'] + 'myflaskapp'
except:
    # uses default mongo configs
    pass

try:
    LOG_DIR = os.environ['OPENSHIFT_LOG_DIR']
except:
    LOG_DIR = '.'
