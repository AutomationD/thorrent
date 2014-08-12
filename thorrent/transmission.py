# -*- coding: utf-8 -*-
__author__ = 'dmitry'
import transmissionrpc

def get_torrent_file_name(torrent_id):
    tc = transmissionrpc.Client('127.0.0.1', port=9091)
    if tc:
        if torrent_id:
            tb = tc.get_torrent(torrent_id)
            return tb.torrentFile
        else:
            return None
    else:
        print("Can't create tc")
