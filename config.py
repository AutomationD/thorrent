# -*- coding: utf-8 -*-
SYSTEM_ENCODING = 'utf-8'

import os
# PLUGINS = ['kinozal_tv',]
APPDIR = os.path.dirname(os.path.realpath(__file__))

LOG_FILE = '/var/log/thorrent.log'
DEBUG = True
NOARGS = True  # Don't use cli argument (for development)


INPUT_DIR = os.path.join(APPDIR, '/data/downloads')
OUTPUT_DIR = os.path.join(APPDIR, '/data/media')
TORRENT_DIR = os.path.join(APPDIR, '/data/to-download')
TORRENT_DOWNLOADED_DIR = os.path.join(APPDIR, '/var/lib/transmission/torrents')

#TEST_TORRENT_FILE = "[kinozal.tv]id632728.torrent" # Multiple Files
# TORRENT_FILE_NAME = "[kinozal.tv]id984957.torrent"
# TORRENT_FILE_NAME = "[kinozal.tv]id1016418.torrent"

# Music (test):
TORRENT_FILE_NAME = "[kinozal.tv]id567386.torrent"
#TEST_TORRENT_FILE = "[kinozal.tv]id1008684.torrent" # Single File




# INPUT_DIR = '/data/downloads'
# OUTPUT_DIR = '/data/test-media'
# TORRENT_DIR = '/data/torrents-downloaded'
#
