__author__ = 'dmitry'
import os
import bencode
from pprint import pprint

TEST_TORRENT_FILE = "[kinozal.tv]id1184343.torrent"

INPUT_DIR = '/Userqs/dmitry/dev/thorrent/thorrent/test/samples/src'
OUTPUT_DIR = '/Users/dmitry/dev/thorrent/thorrent/test/samples/out'
TORRENT_DIR = '/Users/dmitry/dev/thorrent/thorrent/test/samples/torrents'
torrent_file_name = TEST_TORRENT_FILE


def get_torrent_data(torrent_file_name):
    torrent_file_path = os.path.join(TORRENT_DIR, torrent_file_name)

    if not os.path.exists(torrent_file_path):
        print('Skipped, .torrent is not found: "%s' % torrent_file_path)
        return None
    else:
        try:
            torrent_data = bencode.bdecode(open(torrent_file_path, 'rb').read())
            return torrent_data
        except:
            print("Error, can't extract tracker url from .torrent file %s" % torrent_file_path)
            return None

torrent_data = get_torrent_data(torrent_file_name)

print(torrent_data['comment'])
