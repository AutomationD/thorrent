# -*- coding: utf-8 -*-



from __future__ import unicode_literals
__author__ = 'dmitry'

import os
import re
import bencode
import urllib
import logging
import sys, getopt
import string
from pprint import pprint
from bs4 import BeautifulSoup

DEBUG = True

########### Logging Init > ###########
if DEBUG:
    logging.basicConfig(format='%(asctime)s %(message)s', filename='thorrent.log', level=logging.DEBUG, stream=sys.stdout)
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)
else:
    logging.basicConfig(format='%(asctime)s %(message)s', filename='thorrent.log', level=logging.WARNING, stream=sys.stdout)
    root = logging.getLogger()
    root.setLevel(logging.WARNING)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.WARNING)
    #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)
########### < Logging Init ###########




#TEST_TORRENT_FILE = "[kinozal.tv]id632728.torrent" # Multiple Files
TORRENT_FILE_NAME = "[kinozal.tv]id984957.torrent"
#TEST_TORRENT_FILE = "[kinozal.tv]id1008684.torrent" # Single File


INPUT_DIR = '/Users/dmitry/dev/thorrent/thorrent/test/samples/src'
OUTPUT_DIR = '/Users/dmitry/dev/thorrent/thorrent/test/samples/out'
TORRENT_DIR = '/Users/dmitry/dev/thorrent/thorrent/test/samples/torrents'


#torrent_file_name = TEST_TORRENT_FILE



OPT_MODE = 'directory'
logging.debug('Default mode: ' + OPT_MODE)
OPT_PATH = INPUT_DIR
logging.debug('Default path: ' + OPT_PATH)

class Thorrent(object):
    def get_torrent_html(self, torrent_file_data):
        tracker_url = torrent_file_data['comment']

        logging.debug("URL: '%s'" % tracker_url)
        try:
            response = urllib.urlopen(tracker_url)
            html_page = response.read()
        except:
            logging.error("Error, Can't load tracker page '%s'" % tracker_url)
            return None

        html_page = html_page.decode(self.get_torrent_html_codepage(self,html_page))
        return html_page

    @staticmethod
    def get_torrent_file_data(self, torrent_file_name):
        torrent_file_path = os.path.join(TORRENT_DIR, torrent_file_name)

        if not os.path.exists(torrent_file_path):
            logging.error('Skipped, .torrent is not found: "%s' % torrent_file_path)
            return None
        else:
            try:
                torrent_file_data = bencode.bdecode(open(torrent_file_path, 'rb').read())
                return torrent_file_data
            except:
                logging.error("Error, can't extract tracker url from .torrent file %s" % torrent_file_path)
                return None

    def get_torrent_data(self):
        soup = BeautifulSoup(self.html)
        if not self.torrent_html_content_is_valid(self,soup):
            logging.error("Html content is not valid for " + torrent_file_name)
        else:
            logging.debug("Html content is valid for " + torrent_file_name)

            ##### Begin kinozal.tv ######
            desc = soup.h2.find_all('b')
            #print desc

            for d in desc:
                param_name = d.text.strip()
                param_value = d.next_sibling.strip()
                if "Название" in param_name:
                    self.title = param_value
                if "Оригинальное название" in param_name:
                    self.original_title = param_value
                if "Год выпуска" in param_name:
                    self.year = param_value
                    # logging.debug(title + " " + original_title + " " + year)

                    # TODO: Add category detection ++ Maybe have a list of categories and map each tracker category to that standard list
                    ##### End kinozal.tv ######

    @staticmethod
    def torrent_data_type_is_directory(self, torrent_file_data):
        if torrent_file_data.get('info').get('files'):
            #logging.debug(torrent_file_data['info']['files'])
            return True
        else:
            #logging.debug(torrent_file_data['info']['name'])
            return False

    @staticmethod
    def get_torrent_html_codepage(self, html):
        # TODO: Get codepage from html
        return 'cp1251'

    @staticmethod
    def torrent_html_content_is_valid(self, soup):
        return soup.body.find('a', attrs={'class': 'r0'})

    @staticmethod
    def get_safe_file_name(self, torrent_file_name):
        # Stripe Out extra rubbish from the file name

        #remove special symbols
        # download_file_name = re.sub(r'[\\/:"\*?<>|]+', '', download_file_name, 0, re.UNICODE)
        #
        # #remove repeating spaces
        # download_file_name = re.sub(r'[ ]+', ' ', download_file_name, 0, re.UNICODE)


        # #remove repeating spaces
        safe_file_name = torrent_file_name
        safe_file_name = re.sub(r'\s*torrent\s*', '', safe_file_name, 0, re.UNICODE)

        # safe_file_name = re.sub(r'\s*[\[\]\s\\/:"\*?"<>\|,]\s*', '.', safe_file_name, 0, re.UNICODE)
        safe_file_name = re.sub(r'[^\.\'a-zA-ZА-Яа-яЁёё0-9\s_-]', '', safe_file_name, 0, re.UNICODE)

        # Remove duplicate dots
        safe_file_name = re.sub(r'[\.]+', '.', safe_file_name, 0, re.UNICODE)

        # Remove duplicate dots
        safe_file_name = re.sub(r'[\.]+', '.', safe_file_name, 0, re.UNICODE)
        #\s*[\[\]\s\\/:"\*?"<>\|,]\s*
        #(\.*$|^\.*)


        # Remove trailing spaces
        safe_file_name = safe_file_name.strip()

        # Replace all spaces with dots
        safe_file_name = re.sub(r'\s', '.', safe_file_name, 0, re.UNICODE)
        return safe_file_name


    @staticmethod
    def get_torrent_html_codepage(self, html):
        # TODO: Actually Get codepage from html
        return 'cp1251'

    @staticmethod
    def link_data_file(self, from_file_name, to_file_name):
        logging.debug("Linking from " + from_file_name + " to " + to_file_name)
        return

    def __init__(self, torrent_file_name):
        self.html = ''
        self.title = ''
        self.original_title = ''
        self.year = ''
        self.html = self.get_torrent_html(self.get_torrent_file_data(self, torrent_file_name))

        self.torrent_data_type_is_directory = self.torrent_data_type_is_directory(self.get_torrent_file_data(self, torrent_file_name))

def main(argv, opt_mode=OPT_MODE, opt_path=OPT_PATH ):

    #  opt_path = os.path.join(TORRENT_DIR,torrent_file_name)
    # torrent_file_data = get_torrent_file_data(torrent_file_name)
    # thorrent = Thorrent(torrent_file_name)
    # print thorrent.title
    # print thorrent.original_title


    ### Command Line Options > ###
    try:
        opts, args = getopt.getopt(argv, "hmp:", ["mode="])
        # if not opts:
        #     logging.error('thorrent.py -m <mode>')
        #     sys.exit()
    except getopt.GetoptError:
        logging.error('thorrent.py -m <mode>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -m <mode>'
            sys.exit()
        elif opt in ("-m", "--mode"):
            opt_mode = arg
            logging.debug('Mode is ', opt_mode)
        elif opt in ("-p", "--path"):
            opt_path = arg
            logging.debug('Path is ', opt_path)
        else:
            logging.error('thorrent.py -m <mode>')
            sys.exit(2)
    ### < Command Line Options ###

    if opt_mode == 'directory':
        if opt_path:
            torrent_dir = opt_path
        else:
            torrent_dir = TORRENT_DIR

        logging.debug("Working in directory mode (processing all .torrent files in " + torrent_dir + ")")
        for torrent_file_name in os.listdir(TORRENT_DIR):
            if os.path.splitext(torrent_file_name)[1] == ".torrent":
                torrent_file_name = os.path.join(TORRENT_DIR, torrent_file_name)
                # Start .torrent Files Processing
                logging.debug("Got #{torrent_file_name}")


    elif opt_mode == 'file':
        if opt_path:
            torrent_file_name = opt_path
        else:
            if DEBUG:
                torrent_file_name = TORRENT_FILE_NAME
            else:
                logging.error("Torrent file not specified")
                sys.exit(2)
        logging.debug("Working in single file mode (processing " + torrent_file_name + ")")
        # Start .torrent File Processing
        print(torrent_file_name)

    else:
        logging.error('thorrent.py -m <mode>')

        # print thorrent.torrent_data_type_is_directory


        # html = get_torrent_html(torrent_file_data)
        # thorrent = get_torrent_data(thorrent)

        # print thorrent.title + thorrent.original_title + thorrent.year
        # if torrent_data_type_is_directory(torrent_file_data):
        #     logging.debug(torrent_file_data['info']['name'])
        #     # for file in torrent_data['info']['files']:
        #     #     print file['path'][0]
        # else:
        #     logging.debug(torrent_file_data['info']['name'])



        #pprint(torrent_file_data)

        # Testing torrent_data type (directory / file)



        # link_data_file("testfom","testto")
def move_file(src_file, target_file):
    return True

if __name__ == "__main__":
    main(sys.argv[1:])