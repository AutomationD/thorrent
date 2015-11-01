# -*- coding: utf-8 -*-
from thorrent import bencode

__author__ = 'dmitry'

import os
import re

import urllib, urllib.request
import logging
import sys,getopt
import pprint
# from plugins import *
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from socket import timeout
import config
from config import DEBUG
from config import NOARGS

import thorrent.transmission as transmission





import chardet
import unicodedata

from kinopoisk.movie import Movie
import datetime


# IMDB tests:
# movie = Movie(id=521689)
# print(datetime.datetime.now())
# movie.get_content('main_page')
# print(datetime.datetime.now())
# movie.get_content('posters')
# print(movie.posters)
# print(datetime.datetime.now())
# exit()




########### Logging Init: ###########
if DEBUG:
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG, stream=sys.stdout)

    # root = logging.getLogger()
    # root.setLevel(logging.DEBUG)

    # ch = logging.StreamHandler(sys.stdout)
    # ch.setLevel(logging.DEBUG)
    #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # formatter = logging.Formatter('%(message)s')
    # ch.setFormatter(formatter)
    # root.addHandler(ch)
else:
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.WARNING, stream=sys.stdout)
    root = logging.getLogger()
    root.setLevel(logging.WARNING)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.WARNING)
    #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)
########### :Logging Init ###########







#torrent_file_name = TEST_TORRENT_FILE




if NOARGS:
    OPT_MODE = 'dir'
    logging.debug('Default mode: ' + OPT_MODE)
    OPT_PATH = config.TORRENT_DOWNLOADED_DIR


    logging.debug('Default path: ' + OPT_PATH)

video = ["Movies", "TV-Shows", "Music-Videos"]
audio = ["Music", "Audio-Books"]


class Thorrent(object):

    def get_torrent_html(self, torrent_file_data):
        self.tracker_url = torrent_file_data['comment']


        logging.debug("URL: '%s'" % self.tracker_url)
        try:
            response = urllib.request.urlopen(self.tracker_url)
            html_page = response.read()
        except (urllib.error.HTTPError, urllib.error.URLError) as error:            
            logging.error('Data of %s not retrieved because %s\nURL: %s', urllib.name, error, urllib.url)
            self.errors.append('Data of %s not retrieved because %s\nURL: %s', urllib.name, error, urllib.url)
            return None
        except timeout:
            logging.error('Socket timed out - URL %s', urllib.url)
            self.errors.append('Socket timed out - URL %s', urllib.url)
            return None

        # except:
        #     logging.error("Error, Can't load tracker page '%s'" % self.tracker_url)
        #     return None
        else:
            logging.info('Successful data retreival from ' + self.tracker_url)


        html_page = html_page.decode(self.get_torrent_html_codepage(self, html_page))


        # html_page = html_page.decode(self.get_torrent_html_codepage(self, html_page))
        return html_page

    def __get_torrent_file_data(self,torrent_file_name):
        torrent_file_path = os.path.join(OPT_PATH, torrent_file_name)

        if not os.path.exists(torrent_file_path):
            logging.error('.torrent is not found: "%s' % torrent_file_path)
            self.errors.append('Socket timed out - URL %s', urllib.url)

            return None
        else:
            try:
                torrent_file_data = bencode.decode(open(torrent_file_path, 'rb').read())

                return torrent_file_data
            except:
                logging.error("Error, can't extract tracker url from .torrent file %s" % torrent_file_path)
                self.errors.append("Error, can't extract tracker url from .torrent file %s" % torrent_file_path)
                return None

    def __get_torrent_data(self):

        if self.html:
            soup = BeautifulSoup(self.html)
            if not self.torrent_html_content_is_valid(soup):
                logging.error("Html content is not valid")
                self.errors.append("Html content is not valid")
                # logging.error(pprint.pformat(self.html, indent=1, width=80, depth=None))

            else:
                logging.debug("Html content is valid")

                ## Extracting tracker domain name from the url (to get a plugin name later)
                logging.debug("Extracting tracker domain name from "+self.tracker_url)
                self.tracker_name = urlparse(self.tracker_url).netloc
                logging.debug("Tracker Name: " + self.tracker_name)

                # TODO: Separate tracker into a separate plugin
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

                                37: "Movies",
                                12: "Movies",
                                7: "Movies",
                                38: "Movies",
                                16: "Movies",
                                21: "Movies",
                                22: "Movies",
                                20: "Movies",

                                48: "TV-Shows",
                                49: "TV-Shows",
                                50: "TV-Shows",
                                45: "TV-Shows",
                                46: "TV-Shows",
                                18: "TV-Shows",


                                48: "Music-Videos",
                                1: "Music-Videos",

                                23: "Soft",
                                32: "Soft",
                                40: "Soft",

                                3: "Music",
                                4: "Music",
                                5: "Music",
                                42: "Music",


                                2: "Audio-Books"
                            }
                        }
                    }

                    cat = soup.find(attrs={'class': 'cat_img_r'})
                    cat_id = re.sub(r'[\D]', '', str(cat['onclick']))

                    # logging.debug(pprint.pformat(cat, indent=1, width=80, depth=None))
                    try:
                        cat = categories['kinozal_tv']['categories'][int(cat_id)]
                    except:
                        cat = 'Other'
                        logging.error("Can't find category with id " + cat_id)
                        self.errors.append("Can't find category with id " + cat_id)
                    finally:
                        self.category = cat
                        logging.debug("Category: " + categories['kinozal_tv']['categories'][int(cat_id)])
                    ### :Get Category ###

                    if self.category in audio:
                        #########################
                        ######## Audio ##########
                        #########################
                        self.type = 'audio'
                        logging.debug("Processing as audio")
                        html_title = soup.title.string
                        logging.debug("HTML title: " + html_title)

                        ### Get Audio Format: ###
                        tech_params_div = "".join(soup.find(id="tabs").findAll(text=True)).split("\n")
                        # tp_p1 = tech_params_div.find("Качество: ")
                        # self.format = tech_params_div[tp_p1]
                        # print (self.format)
                        # print (tech_params_div)
                        for tech_param in tech_params_div:
                            param = "Аудио: "
                            tp_p1 = tech_param.find(param)
                            if tp_p1 > -1:
                                self.format = tech_param[tp_p1+len(param):len(tech_param)]
                        ### :Get Audio Format ###

                        ### Get Performer Name: ###
                        sba = soup.find_all("a", {"class": "sba"}) # Getting sba class hrefs
                        for s in sba:
                            if "persons" in s['href']:
                                self.title = s.text

                        ###: Get Performer Name ###

                        ### Get other information from description ###
                        desc = soup.h2.find_all('b')
                        for d in desc:
                            param_name = d.text.strip()
                            param_value = d.next_sibling.strip()
                            if "Альбом" in param_name:
                                self.album = param_value
                                logging.debug("Assigned album: "+self.album)
                            if "Год выпуска" in param_name:
                                self.year = param_value
                            if "Жанр" in param_name:
                                self.genre = param_value

                                # logging.debug(title + " " + original_title + " " + year)
                            if not self.title:
                                self.title = html_title
                        ### :RGet other information from description ###

                        ### Check if discography / collection: ###
                        if "discography" in html_title.lower():
                            self.discography = True
                        ###: Check if discography / collection ###

                    if self.category in video:
                        #########################
                        ######## Video ##########
                        #########################
                        self.type = 'video'
                        logging.debug("Processing as " + self.type)

                        ### Get Video Format: ###
                        tech_params_div = "".join(soup.find(id="tabs").findAll(text=True)).split("\n")
                        # tp_p1 = tech_params_div.find("Качество: ")
                        # self.format = tech_params_div[tp_p1]
                        # print (self.format)
                        # print (tech_params_div)
                        for tech_param in tech_params_div:
                            param = "Качество: "
                            tp_p1 = tech_param.find(param)
                            if tp_p1 > -1:
                                self.format = tech_param[tp_p1+len(param):len(tech_param)]
                        ### :Get Video Format

                        html_title = soup.title.string
                        logging.debug("HTML title: " + html_title)

                        ### Check if series: ###
                        if ("серия" in html_title) or ("серии" in html_title) or ("выпуски" in html_title) or ("сезон:" in html_title) or ("сезоны:" in html_title): # Series Torrent
                            self.series = True
                            logging.debug("Detected Series")

                            if "сезон: " in html_title:  # If season is present in title ###? сезоны
                                se_p1 = html_title.find("сезон: ")
                                se_p2 = html_title[0:se_p1-1].rfind(" (")
                                se_s = html_title[se_p2+2:se_p1-1]  # Temp Season string (could be 1, could be 1-1, etc)
                                # logging.debug("Temp Season string: " + se_s)
                                se_s_min_p = se_s.find("-")  # get dash position
                                # logging.debug("Dash pos: " + str(se_s_min_p))
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
                            else:  # No information about season found
                                self.series_season_min = 1
                                self.series_season_max = 1
                                ### :Check if series ###

                        desc = soup.h2.find_all('b')
                        #print (desc)

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
                            if not self.title:
                                self.title = self.localized_title


                ##### End kinozal.tv ######
                else:
                    logging.error("Tracker " + self.tracker_name + " is not implemented")
                    self.errors.append("Tracker " + self.tracker_name + " is not implemented")
                    return False

            return True
        else:
            logging.error("Can't parse HTML page")
            self.errors.append("Can't parse HTML page")
            return False

    def __get_season_and_episode_file_name(episode_file_name):
        # TODO: transform local 'season, episode, etc' strings to standard S01E01 format
        return episode_file_name

    def __get_torrent_category(self):
        torrent_category = 'other'
        # will need to have a modular function for multiple trackers

        return torrent_category

    def __load_plugins(self):
        # No plugins system yet
        return True

        # plugin_name = self.tracker_name.replace(".", "_")
        # logging.debug("Dynamically Importing " + plugin_name + " plugin")

    def torrent_data_type_is_directory(self):
        if self.torrent_file_data.get('info').get('files'):
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
        result = False

        valid_attrs = {
            'kinozal.tv' : {'class': 'mn_wrap'},
            'rutracker.org' : {'class': 'post_wrap'}
        }
        

        for key, attrs in valid_attrs.items():
            if soup.body.find('div', attrs=attrs):
                logging.debug("Found valid response of " + key)
                result = True

        return result

    def __get_torrent_codepage(self):
        if 'encoding' in self.torrent_file_data:  # If encoding is specified in the torrent file
            torrent_file_encoding = self.torrent_file_data['encoding']
            logging.debug("Torrent encoding found: " + torrent_file_encoding)
        else:
            logging.warn("No encoding information found in the torrent file. Trying to guess encoding.")
            chardet_guess = chardet.detect(self.src_file_name)
            torrent_file_encoding = chardet_guess['encoding']
            logging.debug("Torrent encoding guessed: " + chardet_guess['encoding'] + " with " + str(chardet_guess['confidence']) + " confidence")
        return torrent_file_encoding


    @staticmethod
    def get_safe_file_name(self, torrent_file_name):
        # Stripe Out extra rubbish from the file name


        # #remove repeating spaces
        safe_file_name = torrent_file_name
        safe_file_name = re.sub(r'\s*torrent\s*', '', safe_file_name, 0, re.UNICODE)

        #remove special symbols
        # download_file_name = re.sub(r'[\\/:"\*?<>|]+', '', download_file_name, 0, re.UNICODE)



        # safe_file_name = re.sub(r'\s*[\[\]\s\\/:"\*?"<>\|,]\s*', '.', safe_file_name, 0, re.UNICODE)
        safe_file_name = re.sub(r'[^\(\)\.\'a-zA-ZА-Яа-яЁёё0-9\s_-]', '', safe_file_name, 0, re.UNICODE)


        # Remove accents
        nkfd_form = unicodedata.normalize('NFKD', safe_file_name)
        safe_file_name = u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

        # Remove duplicate dots
        safe_file_name = re.sub(r'[\.]+', '.', safe_file_name, 0, re.UNICODE)

        #\s*[\[\]\s\\/:"\*?"<>\|,]\s*
        #(\.*$|^\.*)


        # Remove trailing spaces
        safe_file_name = safe_file_name.strip()

        # Replace all spaces with dots
        # safe_file_name = re.sub(r'\s', '.', safe_file_name, 0, re.UNICODE)
        if torrent_file_name != safe_file_name:
            logging.debug("Safety filters applied: " + torrent_file_name + " -> " + safe_file_name)
        else:
            logging.debug("No safety filters applied: " + safe_file_name)
        return safe_file_name

    def get_dst_file_name(self):
        ## Get new file / directory name

        # For video torrents (we need to keep year, etc)
        if self.type == 'video':
            if self.series:
                if self.series_season_min == self.series_season_max:  # If Just one season
                    season = "s" + "%02d" % self.series_season_min
                else:
                    season = "s" + "%02d" % self.series_season_min + "-" + "s" + "%02d" % self.series_season_max
            else:
                season = None

            if self.localized_title:
                if season:
                    # dst_file_name = self.title+"."+self.localized_title+"." + season + "."+self.year
                    # dst_file_name = self.localized_title + "-" + self.title + "." +self.year
                    dst_file_name = self.title + " " + "(" + self.year + ")"
                else:
                    # dst_file_name = self.localized_title + "-" + self.title + "." +self.year
                    # dst_file_name = self.title+"." + season + "."+self.year
                    dst_file_name = self.title + " " + "(" + self.year + ")"
            else:
                if season:
                    # dst_file_name = self.title+"."+self.localized_title+"." + season + "."+self.year
                    dst_file_name = self.title + " " + "(" + self.year + ")"
                    # dst_file_name = self.title+"." + season + "." + self.year
                else:
                    dst_file_name = self.title + " " + "(" + self.year + ")"

            # Add media format to the end of a file name. (1080p/720p, etc)
            if self.format:
                dst_file_name += " - " + self.format



            ## If we are processing source as a file target should also have an extension, otherwise not
            if not self.torrent_data_type_is_directory:
                dst_file_name += os.path.splitext(self.src_file_name)[1]


        if self.type == 'audio':
            if self.discography:
                dst_file_name = 'Discography'
            else:
                dst_file_name = self.album

        return self.get_safe_file_name(self, dst_file_name)


    def make_links(self, src_directory, dst_directory):
        # Constructing tartet directory path for videos
        if self.type == 'video':
            if not self.torrent_data_type_is_directory:
                dst_directory = os.path.join(dst_directory, self.category, self.title + " " + "(" + self.year + ")")
            else:
                dst_directory = os.path.join(dst_directory, self.category)

        # Constructing tartet directory path for audios
        elif self.type == 'audio':
            if not self.torrent_data_type_is_directory:
                dst_directory = os.path.join(dst_directory, self.category, self.title, self.album)
            else:
                dst_directory = os.path.join(dst_directory, self.category, self.title)

        try:
            src_full_name = os.path.join(src_directory, self.src_file_name)
            dst_full_name = os.path.join(dst_directory, self.dst_file_name)
            os.environ['THORRENT_DST_FILE_NAME'] = dst_full_name
        except:
            logging.error("Failed joining: " + self.tracker_url + ", skipping")
            self.errors.append("Failed joining: " + self.tracker_url + ", skipping")
            # logging.error(src_directory)
            # logging.error(self.src_file_name)
            return False


        if not os.path.exists(dst_directory):
            logging.debug("Creating " + dst_directory)
            os.makedirs(dst_directory)

        logging.debug("Linking from " + src_full_name + " to " + dst_full_name)
        if os.path.exists(src_full_name):
            if not os.path.exists(dst_full_name):
                if os.symlink(src_full_name, dst_full_name):
                    logging.debug(src_full_name + " -> " + dst_full_name)
        else:
            logging.error(src_full_name + " does not exist (download hasn't finish yet?).")
            self.errors.append(src_full_name + " does not exist (download hasn't finish yet?).")

    def __init__(self, torrent_file_name):
        ## Init empty variables
        self.html = ''
        self.title = ''
        self.localized_title = ''
        self.album = ''
        self.genre = ''
        self.year = ''
        self.src_file_name = ''
        self.dst_file_name = ''
        self.tracker_name = ''
        self.category = ''
        self.format = ''
        self.imdb_id = ''
        self.kinopoisk_id = ''
        self.type = '' # video, audio, soft, game
        self.errors = []


        self.series = False  # Is media a series?
        # self.series_data = {
        #     "s01": [01]
        # }
        self.series_season_min = None  # First season in torrent
        self.series_season_max = None  # Last season in torrent
        self.series_episode_min = None  # First episode
        self.series_episode_max = None

        self.discography = False # Is media a collection of albums?
        self.torrent_file_name = torrent_file_name
        self.torrent_file_data = self.__get_torrent_file_data(self.torrent_file_name)

        # logging.debug(pprint.pformat(self.torrent_file_data, indent=1, width=80, depth=None))
        if self.torrent_file_data:
            ## Get and assign html of the page to parse later
            self.html = self.get_torrent_html(self.torrent_file_data)

            ## Execute parse of html
            if self.__get_torrent_data():

                # Load Plugins (for example tracker-specific parsing logic)
                self.__load_plugins()

                ## Check if data type is directory (vs file)
                self.torrent_data_type_is_directory = self.torrent_data_type_is_directory()


                ## Get original torrent file/directory name
                if 'name.utf-8' in self.torrent_file_data['info']:
                    self.src_file_name = self.torrent_file_data['info']['name.utf-8']
                else:
                    self.src_file_name = self.torrent_file_data['info']['name']

                ## Get destination file/directory name
                self.dst_file_name = self.get_dst_file_name()


                ## Decode src_file_name based on the encoding of torrent file
                ## Get torrent file encoding (torrent_data and src_file_name are involved
                self.src_file_name = self.src_file_name
            else:
                logging.debug("No parse data for " + self.tracker_name + ". Please make sure to get proper plugin")    

        else:
            logging.debug("Skipped " + self.torrent_file_name)


def main(argv):
    if NOARGS:
        opt_mode = OPT_MODE
        opt_path = OPT_PATH
        opt_src_dir = config.INPUT_DIR
        opt_dst_dir = config.OUTPUT_DIR


    ### Command Line Options: ###
    try:
        opts, args = getopt.getopt(argv, "hm:p:t:s:d:")
        # if not opts:
        #     logging.error('thorrent.py -fm <mode>')
        #     sys.exit()
    except getopt.GetoptError:
        logging.error('thorrent.py -m <mode>')
        sys.exit(2)


    for opt, arg in opts:
        if opt == '-h':
            print('test.py -m <mode>')
            sys.exit()
        elif opt in ("-m", "--mode"):
            opt_mode = arg
            logging.debug('Mode is ' + opt_mode)
        elif opt in ("-p", "--path"):
            opt_path = arg
            # logging.debug('Path is ' + opt_path.encode('utf-8'))

        elif opt in ("-t", "--torrent_id"):
            opt_torrent_id = arg
            # logging.debug('Path is ' + opt_path.encode('utf-8'))
        elif opt in ("-s", "--source_dir"):
            opt_src_dir = arg
            # logging.debug('Path is ' + opt_path.encode('utf-8'))
        elif opt in ("-d", "--destination_dir"):
            opt_dst_dir = arg
        else:
            logging.error('thorrent.py -m <mode>')
            sys.exit(2)
    ### :Command Line Options ###


    thorrents = []

    ### Create Nesessary Thorrent Objects (and put it in a list): ###

    ## Directory Mode - Processing all .torrent files INPUT_DIR
    if opt_mode == 'directory' or opt_mode == 'dir':
        if opt_path:
            torrent_dir = opt_path
        else:
            torrent_dir = OPT_PATH

        logging.debug("Working in directory mode (processing all .torrent files in " + torrent_dir + ")")
        for torrent_file_name in os.listdir(OPT_PATH):
            if os.path.splitext(torrent_file_name)[1] == ".torrent":
                torrent_file_name = os.path.join(OPT_PATH, torrent_file_name)
                logging.debug("")
                logging.debug("Working on " + torrent_file_name)
                thorrent = Thorrent(torrent_file_name)
                logging.debug("Title: " + thorrent.title)

                thorrents.append(thorrent)

    ## File Mode - Processing a single .torrent file
    elif opt_mode == 'file':
        if NOARGS:  # For debug only - process one single hard coded test .torrent file
            torrent_file_name = config.TORRENT_FILE_NAME
        else:
            if opt_path:
                torrent_file_name = opt_path
            else:
                logging.error("Torrent file not specified")
                sys.exit(2)
        logging.debug("Working in single file mode (processing " + torrent_file_name + ")")
        thorrent = Thorrent(torrent_file_name)
        if thorrent.torrent_file_data:
            logging.debug("Title: " + thorrent.title)
            thorrents.append(thorrent)

    # Transmission mode - Processing a single torrent from transmission client
    elif opt_mode == 'transmission':
        if opt_torrent_id:
            logging.debug("torrent_id received: " + opt_torrent_id)
            torrent_file_name = transmission.get_torrent_file_name(opt_torrent_id)
            logging.debug("torrent_file_name: " + torrent_file_name)
        else:
            if NOARGS:  # For debug only - process one single hard coded test .torrent file
                torrent_file_name = config.TORRENT_FILE_NAME
            else:
                logging.error("Torrent file not specified")
                sys.exit(2)
        logging.debug("Working in single file mode (processing " + torrent_file_name + ")")
        thorrent = Thorrent(torrent_file_name)
        if thorrent.torrent_file_data:
            logging.debug("Title: " + thorrent.title)
            thorrents.append(thorrent)

    else:
        logging.error('thorrent.py -m <mode>')
    ### :Create Nessesary Thorrent Objects (and put it in a list) ###

    logging.debug("Finished collecting information. Number of thorrents aquired: " + str(len(thorrents)))
    if len(thorrents) > 0:
        logging.info("\nCreating symlinks in order to continue seeding")
        for thorrent in thorrents:
            ## Create Links to new structure (and keep seeding old file names as well)
            thorrent.make_links(opt_src_dir, opt_dst_dir)
    
    print("==========================================================================")
    print("========                     Summary                              ========")
    print("==========================================================================")
    print("#######                      Errors                                #######")
    for thorrent in thorrents:
        if thorrent.errors:
            print(thorrent.torrent_file_name)
            for error in thorrent.errors:
                print("---" + error)
