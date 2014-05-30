# -*- encoding: utf-8 -*-
import os
import re
import urllib.request
import shutil
#import sys
import ctypes

INPUT_DIR = 'f:/testpy/downloads'
OUTPUT_DIR = 'f:/testpy/movies'
TORRENT_DIR = 'f:/testpy/torrents'
MOVE_ALGORITHM = 'link'


def get_move_algorithms():
    return {'move': move_file(),
            'copy': copy_file(),
            'link': create_hard_link()}

# def print(msg):
#     msg = msg.encode('cp866', 'replace')
#     msg = msg.decode('cp866')
#     print(msg)


def get_torrent_file_path(file_name):
    file_path = os.path.join(TORRENT_DIR, file_name + '.torrent')
    if not os.path.exists(file_path):
        print('Skipped, .torrent is not found: "%s' % file_path)
        return None
    return file_path


def get_tracker_url(torrent_file_path):
    try:
        torrent_file = open(torrent_file_path, 'r', encoding='ascii', errors='replace')
        file_data = torrent_file.read()
        tracker_url_len, tracker_url = re.search(r'comment([0-9]{2}):(.+)', file_data).groups()
        tracker_url = re.search(r'(.{' + tracker_url_len + '})', tracker_url).groups()[0]
        return tracker_url
    except:
        print("Error, can't extract tracker url from .torrent file %s" % torrent_file_path)
        return None


def load_tracker_page(tracker_url):
    #print ("URL: '%s'" % tracker_url)
    try:
        response = urllib.request.urlopen(tracker_url)
        html_page = response.read()
    except:
        print("Error, Can't load tracker page '%s'" % tracker_url)
        return None
    html_page = html_page.decode('cp1251')
    return html_page


def prepare_file_name(file_name):
    try:
        #remove special symbols
        file_name = re.sub(r'[\\/:"\*?<>|]+', '', file_name, 0, re.UNICODE)
        #remove repeating spaces
        file_name = re.sub(r'[ ]+', ' ', file_name, 0, re.UNICODE)
        file_name = file_name.strip()
    except:
        print("Error, can't prepare file name '%s'" % file_name)
        return None
    return file_name


class FileInfo:
    pass


def parse_tracker_page(html_page):
    try:
        page_title = re.search(r'<title>(.+?) :: .+?</title>', html_page, re.UNICODE).groups()[0]
    except:
        print("Error, Can't parse <title>")
        return None
    file_info = FileInfo()
    file_info.name = ""
    file_info.year = ""
    file_info.descr = ""
    try:
        file_info.name, file_info.year, file_info.descr = re.search(r'(.+?) \[([0-9]{4}).*?, (.+?)\]', page_title, re.UNICODE).groups()
    except:
        print("Warning, Can't parse page title: %s" % page_title)
        try:
            file_info.name, file_info.year, file_info.descr = re.search(r'(.+?)([0-9]{4}).*?, (.+?)$', page_title, re.UNICODE).groups()
        except:
            print("Warning, Can't parse page title: %s" % page_title)
            file_info.name = page_title
    return file_info


def get_data_from_torrent(file_name):
    torrent_file_path = get_torrent_file_path(file_name)
    if not torrent_file_path:
        return None
    tracker_url = get_tracker_url(torrent_file_path)
    if not tracker_url:
        return None
    html_page = load_tracker_page(tracker_url)
    if not html_page:
        return None
    return parse_tracker_page(html_page)

def prepare_new_file_name(file_name, file_info):
    tmp, ext = os.path.splitext(file_name)
    to_prepare = file_info.name + ' (' + file_info.year + ') ' + file_info.descr
    clean_name = prepare_file_name(to_prepare)
    new_file_name = clean_name + ext
    return new_file_name


def move_file(src, dst):
    shutil.move(src, dst)


def copy_file(src, dst):
    if os.path.isdir(src):
        for file_name in os.listdir(src):
            if not os.path.exists(dst):
                os.mkdir(dst)
            sub_src = os.path.join(src, file_name)
            sub_dst = os.path.join(dst, file_name)
            CopyFile(src, dst)
    else:
        if not os.path.exists(dst):
            shutil.copy2(src, dst)


def create_hard_link(src, dst):
    create_hard_link_w = ctypes.windll.kernel32.CreateHardLinkW
    create_hard_link_w.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_void_p)
    create_hard_link_w.restype = ctypes.c_int
    if os.path.isdir(src):
        for fileName in os.listdir(src):
            if not os.path.exists(dst):
                os.mkdir(dst)
            sub_src = os.path.join(src, fileName)
            sub_dst = os.path.join(dst, fileName)
            create_hard_link(sub_src, sub_dst)
    else:
        if not os.path.exists(dst):
            if create_hard_link_w(dst, src, 0) == 0:
                raise IOError


def main():
    print('Hello, Find downloads in "%s" :' % INPUT_DIR)
    total_count = 0
    processed_count = 0
    for file_name in os.listdir(INPUT_DIR):
        total_count = total_count + 1
        print('Process a file: "%s"' % file_name)
        file_info = get_data_from_torrent(file_name)
        if file_info is None:
            continue
        s_new_file_name = prepare_file_name(file_name, file_info)
        if s_new_file_name:
            old_file_path = os.path.join(INPUT_DIR, file_name)
            new_file_path = os.path.join(OUTPUT_DIR, s_new_file_name)
            try:
                get_move_algorithms()[MOVE_ALGORITHM](old_file_path, new_file_path)
                processed_count = processed_count + 1
            except:
                print("Error, Can't move file from %s to %s" % (old_file_path, new_file_path))
    print("%d friles were moved from %d total found files" % (processed_count, total_count))

if __name__ == "__main__":
    main()