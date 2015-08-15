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

import os, sys, base64, ConfigParser, argparse, t411, search_t411, pprint

from deluge_client import DelugeRPCClient



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




class T411ToDeluge(object):
    """
    Main class
    """

    def __init__(self):
        parser = self.buildParser()
        args = parser.parse_args()
        config = self.parseConfig()

        if args.version:
            self.printVersion()

        if not args.title:
            self.printSyntax(parser)

        if args.torrent_id is not None:
            torrent_id = args.torrent_id[0]
            self.downloadAndUploadTorrent(torrent_id, '/home/audric/torrent.torrent')
        else:
            self.t411search = search_t411.search_t411(
                username=self.usernameT411,
                password=self.passwordT411,
                title=args.title,
                season=args.season,
                episode=args.episode,
                seeders_min=args.min_seeders,
                )

            self.t411search.printTorrentList()

    def buildParser(self):
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




    def downloadTorrent(self, torrent_id, filename):
        """
        Download a torrent from t411
        """
        self.t411Instance = t411.T411(self.usernameT411, self.passwordT411)
        self.t411Instance.download(torrent_id, filename)
        # req = requests.get(url, headers={'Authorization': token}, stream=True)
        # content = req.raw

        # with open(filename, 'w') as location:
        # shutil.copyfileobj(content, location)


    def uploadTorrent(self, filename):
        """
        Upload a torrent to the deluge host based on the config file
        """
        print('Uploading torrent %s' % (filename))
        client = DelugeRPCClient(self.hostDeluge, self.portDeluge, self.usernameDeluge, self.passwordDeluge)
        client.connect()
        f = open(filename, 'rb')
        filedump = base64.encodestring(f.read())
        f.close()
        client.call('core.add_torrent_file', filename, filedump, {}, )
        bytes_available = client.call('core.get_free_space')
        gig_available = bytes_available/(1024.*1024*1024)
        print('There is %.1f GB available on the host \'%s\'.' % (gig_available, self.hostDeluge))


    def removeTorrentFile(self, filename):
        print("Deleting torrent file %s" % filename)
        os.remove(filename);


    def downloadAndUploadTorrent(self, torrent_id, filename):
        self.downloadTorrent(torrent_id, filename)
        self.uploadTorrent(filename)
        self.removeTorrentFile(filename)




    def parseConfig(self, filename='config.ini'):
        config = ConfigParser.ConfigParser()
        config.read(filename)
        try:
            self.hostDeluge = config.get('DELUGE','host')
            self.portDeluge = int(config.get('DELUGE', 'port'))
            self.usernameDeluge = config.get('DELUGE', 'username')
            self.passwordDeluge = config.get('DELUGE', 'password')
            self.usernameT411 = config.get('T411', 'username')
            self.passwordT411 = config.get('T411', 'password')
        except:
            print("You have to copy and paste to 'config.ini' the 'config.ini.default' and edit it !")
            sys.exit(1)


if __name__ == '__main__':
    t411ToDeluge = T411ToDeluge()




#end of game
