# -*- coding: utf-8 -*-
__author__ = 'dmitry'
import sys,getopt
import logging
from thorrent import Thorrent

import pprint
# from plugins import *

import config

from config import DEBUG
from config import NOARGS

import thorrent.transmission as transmission





#from kinopoisk.movie import Movie
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
    if opt_mode == 'directory':
        if opt_path:
            torrent_dir = opt_path
        else:
            torrent_dir = config.TORRENT_DIR

        logging.debug("Working in directory mode (processing all .torrent files in " + torrent_dir + ")")
        for torrent_file_name in os.listdir(config.TORRENT_DIR):
            if os.path.splitext(torrent_file_name)[1] == ".torrent":
                torrent_file_name = os.path.join(config.TORRENT_DIR, torrent_file_name)
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

