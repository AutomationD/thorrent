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
import pprint
from plugins import *
from bs4 import BeautifulSoup
from urlparse import urlparse
import config
import importlib





DEBUG = True

########### Logging Init: ###########
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
########### :Logging Init ###########




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
        self.tracker_url = torrent_file_data['comment']


        logging.debug("URL: '%s'" % self.tracker_url)
        try:
            response = urllib.urlopen(self.tracker_url)
            html_page = response.read()
        except:
            logging.error("Error, Can't load tracker page '%s'" % self.tracker_url)
            return None

        html_page = html_page.decode(self.get_torrent_html_codepage(self, html_page))
        return html_page

    @staticmethod
    def __get_torrent_file_data(torrent_file_name):
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

    def __get_torrent_data(self):
        soup = BeautifulSoup(self.html)
        if not self.torrent_html_content_is_valid(soup):
            logging.error("Html content is not valid")
            logging.error(pprint.pformat(self.html, indent=1, width=80, depth=None))

        else:
            logging.debug("Html content is valid")

            ## Extracting tracker domain name from the url (to get a plugin name later)
            logging.debug("Extracting tracker domain name from "+self.tracker_url)
            self.tracker_name = urlparse(self.tracker_url).netloc
            logging.debug("Tracker Name: " + self.tracker_name)

            ##### Begin kinozal.tv: ######
            if self.tracker_name == 'kinozal.tv':

                ### Get Category: ###
                categories = {
                    "kinozal_tv": {
                        "categories": {
                            8: "Movies",
                            6: "Movies",
                            15: "Movies",
                            17: "Movies",
                            35: "Movies",
                            39: "Movies",
                            13: "Movies",
                            14: "Movies",
                            24: "Movies",
                            11: "Movies",
                            10: "Movies",
                            9: "Movies",
                            47: "Movies",
                            18: "Movies",
                            37: "Movies",
                            12: "Movies",
                            7: "Movies",
                            38: "Movies",
                            16: "Movies",
                            21: "Movies",
                            22: "Movies",
                            20: "Movies",

                            49: "TV-Shows",
                            50: "TV-Shows",
                            45: "TV-Shows",
                            46: "TV-Shows",


                            48: "Music-Videos",
                            1: "Music-Videos",

                            23: "Soft",
                            32: "Soft",
                            40: "Soft",

                            3: "Music"
                        }
                    }
                }

                cat = soup.find(attrs={'class' : 'cat_img_r'})
                cat_id = re.sub(r'[\D]', '', str(cat['onclick']))

                # logging.debug(pprint.pformat(cat, indent=1, width=80, depth=None))
                self.category = categories['kinozal_tv']['categories'][int(cat_id)]
                logging.debug("Category: " + categories['kinozal_tv']['categories'][int(cat_id)])

                ### :Get Category ###

                html_title = soup.title.string
                logging.debug("HTML title: " + html_title)
                ### Check if series: ###
                if ("серия" in html_title) or ("серии" in html_title): # Series Torrent
                    self.series = True
                    logging.debug("Detected Series")

                    if "сезон" in html_title:  # If season is present in title
                        se_p1 = html_title.find("сезон")
                        se_p2 = html_title[0:se_p1-1].rfind(" (")
                        se_s = html_title[se_p2+2:se_p1-1]  # Temp Season string (could be 1, could be 1-1, etc)
                        logging.debug("Temp Season string: " + se_s)
                        se_s_min_p = se_s.find("-")  # get dash position
                        logging.debug("Dash pos: " + str(se_s_min_p))
                        if se_s_min_p < 0:  # If not multiple seasons
                            self.series_season_min = int(se_s)
                            self.series_season_max = int(se_s)
                        else:
                            se_s_min = se_s[0:se_s_min_p]
                            se_s_max = se_s[se_s_min_p+1:len(se_s)]
                            self.series_season_min = int(se_s_min)


                            self.series_season_max = int(se_s_max)

                        logging.debug("First Season: " + str(self.series_season_min))
                        logging.debug("Last Season: " + str(self.series_season_max))
                    ### :Check if series ###

                desc = soup.h2.find_all('b')
                #print desc

                for d in desc:
                    param_name = d.text.strip()
                    param_value = d.next_sibling.strip()
                    if "Название" in param_name:
                        self.localized_title = param_value
                    if "Оригинальное название" in param_name:
                        self.title = param_value
                    if "Год выпуска" in param_name:
                        self.year = param_value
                        # logging.debug(title + " " + original_title + " " + year)

                        # TODO: Add category detection ++ Maybe have a list of categories and map each tracker category to that standard list
            ##### End kinozal.tv ######
            else:
                logging.error("Tracker "+self.tracker_name+" is not implemented")
                exit(1)


    def __get_torrent_category(self):
        torrent_category = 'other'

        return torrent_category

    def __load_plugins(self):
        # No plugins system yet
        return True

        # plugin_name = self.tracker_name.replace(".", "_")
        # logging.debug("Dynamically Importing " + plugin_name + " plugin")


        # return importlib.import_module('plugins.'+plugin_name,)



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
    def torrent_html_content_is_valid(soup):
        return soup.body.find('div', attrs={'class': 'mn_wrap'})

    @staticmethod
    def get_safe_file_name(self, torrent_file_name):
        # Stripe Out extra rubbish from the file name



        # #remove repeating spaces
        safe_file_name = torrent_file_name
        safe_file_name = re.sub(r'\s*torrent\s*', '', safe_file_name, 0, re.UNICODE)

        #remove special symbols
        # download_file_name = re.sub(r'[\\/:"\*?<>|]+', '', download_file_name, 0, re.UNICODE)



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

    def get_dst_file_name(self):


        ## Get new file name
        if self.series:
            if self.series_season_min == self.series_season_max:  # If Just one season
                season = "s" + "%02d" % self.series_season_min
            else:
                season = "s" + "%02d" % self.series_season_min + "-" + "s" + "%02d" % self.series_season_max
        else:
            season = None


        if self.localized_title:
            if season:
                dst_file_name = self.title+"-"+self.localized_title+"." + season + "."+self.year
            else:
                dst_file_name = self.title+"-"+self.localized_title+"."+self.year
        else:
            if season:
                dst_file_name = self.title+"." + season + "." + self.year
            else:
                dst_file_name = self.title+"."+self.year






        ## If are processing source as a file target should also have an extension, otherwise notx`
        if not os.path.isdir(self.src_file_name):
            dst_file_name += os.path.splitext(self.src_file_name)[1]
        return self.get_safe_file_name(self, dst_file_name)

    def make_links(self):
        src_directory = INPUT_DIR
        # if self.series:
        #     if self.series_season_min == self.series_season_max:
        #         dst_directory = os.path.join(OUTPUT_DIR, self.category)
        # else:
        dst_directory = os.path.join(OUTPUT_DIR, self.category)




        src_full_name = os.path.join(src_directory, self.src_file_name)
        dst_full_name = os.path.join(dst_directory, self.dst_file_name)

        if not os.path.exists(dst_directory):
            logging.debug("Creating " + dst_directory)
            os.mkdir(dst_directory)

        logging.debug("Linking from " + src_full_name + " to " + dst_full_name)
        if os.path.exists(src_full_name):
            if not os.path.exists(dst_full_name):
                if os.symlink(src_full_name, dst_full_name):
                    logging.debug(src_full_name + "->" + dst_full_name)
        else:
            logging.error(src_full_name + " does not exits.")

    def __init__(self, torrent_file_name):
        ## Init empty variables
        self.html = ''
        self.title = ''
        self.localized_title = ''
        self.year = ''
        self.src_file_name = ''
        self.dst_file_name = ''
        self.tracker_name = ''
        self.category = ''
        self.series = False # Is media a series?
        self.series_data = {
            "s01": [01]
        }
        self.series_season_min = None  # First season in torrent
        self.series_season_max = None  # Last season in torrent
        self.series_episode_min = None  # First episode
        self.series_episode_max = None

        self.torrent_file_name = torrent_file_name
        self.torrent_file_data = self.__get_torrent_file_data(self.torrent_file_name)

        # logging.debug(pprint.pformat(self.torrent_file_data, indent=1, width=80, depth=None))

        ## Get and assign html of the page to parse later
        self.html = self.get_torrent_html(self.torrent_file_data)

        ## Execute parse of html
        self.__get_torrent_data()

        # Load Plugins (for example tracker-specific parsing logic)
        self.__load_plugins()

        ## Check if data type is directory (vs file)
        self.torrent_data_type_is_directory = self.torrent_data_type_is_directory(self, self.torrent_file_data)

        ## Get original torrent file/directory name
        self.src_file_name = self.torrent_file_data['info']['name']

        ## Get destination file/directory name
        self.dst_file_name = self.get_dst_file_name()


def main(argv, opt_mode=OPT_MODE, opt_path=OPT_PATH):


    ### Command Line Options: ###
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
    ### :Command Line Options ###


    thorrents = []

    ### Create Nesessary Thorrent Objects (and put it in a list): ###

    ## Directory Mode - Processing all .torrent files INPUT_DIR
    if opt_mode == 'directory':
        if opt_path:
            torrent_dir = opt_path
        else:
            torrent_dir = TORRENT_DIR

        logging.debug("Working in directory mode (processing all .torrent files in " + torrent_dir + ")")
        for torrent_file_name in os.listdir(TORRENT_DIR):
            if os.path.splitext(torrent_file_name)[1] == ".torrent":
                torrent_file_name = os.path.join(TORRENT_DIR, torrent_file_name)
                logging.debug("")
                logging.debug("Working on " + torrent_file_name)
                thorrent = Thorrent(torrent_file_name)

                logging.debug("Title: " + thorrent.title)

                thorrents.append(thorrent)

    ## File Mode - Processing a single .torrent file
    elif opt_mode == 'file':
        if opt_path:
            torrent_file_name = opt_path
        else:
            if DEBUG:  # For debug only - process one single hard coded test .torrent file
                torrent_file_name = TORRENT_FILE_NAME
            else:
                logging.error("Torrent file not specified")
                sys.exit(2)
        logging.debug("Working in single file mode (processing " + torrent_file_name + ")")
    else:
        logging.error('thorrent.py -m <mode>')
    ### :Create Nessesary Thorrent Objects (and put it in a list) ###

    logging.info("\nCreating symlinks in order to continue seeding")
    for thorrent in thorrents:

        ## Create Links to new structure (and keep seeding old file names as well)
        thorrent.make_links()



if __name__ == "__main__":
    main(sys.argv[1:])







