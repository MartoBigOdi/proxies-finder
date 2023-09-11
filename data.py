import os


TEMP_FOLDER = 'temp'
WEBS_FOR_SCRAP = ["https://free-proxy-list.net/", "https://proxyscrape.com/free-proxy-list","https://geonode.com/free-proxy-list", "https://hidemyna.me/en/proxy-list/"]

FOLDERS = [TEMP_FOLDER]

for folder in FOLDERS:
    if not os.path.exists(folder):
        os.makedirs(folder)
    