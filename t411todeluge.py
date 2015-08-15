#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# t411ToDeluge
# Search and download torrents from t411 and upload them to a deluge daemon
#
# Distributed under the MIT license (MIT)
__appname__ = "t411ToDeluge"
__version__ = "0.1"
__author__ = "Audric Ackermann <audric.bilb@gmail.com>"
__license__ = "MIT"

import urllib2, requests, os, shutil, base64, ConfigParser, argparse, t411, search_t411, pprint

from deluge_client import DelugeRPCClient





def buildParser():
    parser = argparse.ArgumentParser(description='Download t411 torrent through deluge rpc client')
    parser.add_argument('-i', '--torrent_id', nargs='+', help='Torrent\'s id to upload to deluge (once found)')
    parser.add_argument('-t', '--title', help='Torrent\'s title')

    parser.add_argument('-s', '--season', help='Serie\'s season')
    parser.add_argument('-e', '--episode', help='Serie\'s episode')
    parser.add_argument('-l', '--min_seeders', help='Min seeders', action='store_true')
    parser.add_argument('-a', '--all_result', help='Display all results, not just the best one', action='store_true')
    parser.add_argument('--hd', help='Add a filter for hd results', action='store_true')
    parser.add_argument('-v', '--version', help='Print version and exit', action='store_true')
    return parser




def downloadTorrent(torrent_id, filename):
    t411Instance = t411.T411()
    t411Instance.download(torrent_id, filename)
    # req = requests.get(url, headers={'Authorization': token}, stream=True)
    # content = req.raw

    # with open(filename, 'w') as location:
    # shutil.copyfileobj(content, location)


def uploadTorrent(filename, config):
    print('Uploading torrent %s' % (filename))
    host = config.get('DELUGE','host')
    port = int(config.get('DELUGE', 'port'))
    username = config.get('DELUGE', 'username')
    password = config.get('DELUGE', 'password')
    client = DelugeRPCClient(host, port, username, password)
    client.connect()
    f = open(filename, 'rb')
    filedump = base64.encodestring(f.read())
    f.close()
    client.call('core.add_torrent_file', filename, filedump, {}, )
    bytes_available = client.call('core.get_free_space')
    gig_available = bytes_available/(1024.*1024*1024)
    print('There is %.1f GB available on the host \'%s\'.' % (gig_available, host))


def removeTorrentFile(filename):
    print("Deleting torrent file %s" % filename)
    os.remove(filename);


def downloadAndUploadTorrent(torrent_id, filename, config):
    downloadTorrent(torrent_id, filename)
    uploadTorrent(filename, config)
    removeTorrentFile(filename)




def parseConfig(filename='config.ini'):
    config = ConfigParser.ConfigParser()
    config.read(filename)
    return config


def printSyntax(parser):
    """
    Display the syntax of the command line
    """
    print(parser.print_help())


def printVersion():
    """
    Display the current software version
    """
    print(__appname__ + " version " + __version__)



if __name__ == '__main__':
    parser = buildParser()
    args = parser.parse_args()
    config = parseConfig()

    if args.version:
        printVersion()

    if not args.title:
        printSyntax(parser)

    if args.torrent_id is not None:
        torrent_id = args.torrent_id[0]
        downloadAndUploadTorrent(torrent_id, '/home/audric/torrent.torrent', config)
    else:
        t411search = search_t411.search_t411(
            title=args.title,
            season=args.season,
            episode=args.episode,
            seeders_min=args.min_seeders)

        t411search.printTorrentList()



#end of game
