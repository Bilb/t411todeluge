#! /usr/bin/env python3
# -*- coding: UTF-8 -*-
import logging


import t411, re


from termcolor import colored, cprint

class search_t411(object):
    """
    Main class: search torrents from t411 server
    """

    def __init__(self,
            username, password, title="", season=None, episode=None, seeders_min=0):

        self.username = username
        self.password = password
        self.title = title

        self.season = season
        self.episode = episode
        self.seeders_min = seeders_min

        self.source = self.__readsource__()
        self.regexp = self.search_regexp()
        logging.debug("Search regexp: %s" % self.regexp)

        #get the list of torrent from t411 source
        self.list = self.buildlist()

        #sort list of torrents
        self.list.sort(key=lambda torrent: int(torrent['seeders']), reverse=True)
        logging.info("%s torrent(s) found" % len(self.list))



    def __readsource__(self):
        """
        Connect to the t411 server
        """
        try:
            src = t411.T411(self.username, self.password)
        except Exception as e:
            logging.error("Error while trying connection to t411... %s" % e.message)
            sys.exit(1)
        else:
            print("Connected to the t411 server")
            return src

    def search_regexp(self):
        """
        Define the regexp used for the search
        """

        if ((self.season == None) and (self.episode == None)):
            regexp = '^%s.*' % self.title.lower()
        elif (self.episode == None):
            regexp = '^%s.*(s[0]*%s|season[\s\_\-\.]*%s).*' % (self.title.lower(), self.season, self.season)
        else:
            regexp = '^%s.*((s[0]*%s.*e[0]*%s)|[0]*%sx[0]*%s).*' % (self.title.lower(), self.season, self.episode, self.season, self.episode)
        return regexp


    def buildlist(self, limit=1000):
        """
        Build the torrent list
        Return list of list sorted by seeders count
        Id can be used to retrieve torrent associate with this id
        [[<title>, <Seeders>, <id>] ...]
        """

        try:
            s = self.source.search(self.title.lower(), limit)
        except Exception as e:
            logging.error("Can not send search request to the t411 server")
            logging.error(e.message)
            sys.exit(1)


        try:
            for t in s.items():
                pass
        except:
            logging.error("t411 server returned an invalid result")
            sys.exit(1)

        torrentlist = []
        for torrent in s['torrents']:
            if isinstance(torrent, dict):
                #logging.debug("Compare regex to: %s" % t.title.lower())
                if (re.search(self.regexp, torrent['name'].lower()) and (int(torrent['seeders']) >= self.seeders_min)):
                    # logging.debug("Matched")
                    torrentlist.append( {
                            'name': torrent['name'],
                            'seeders': torrent['seeders'],
                            'id': torrent['id']})

        logging.debug("Found %d matching items " % (len(torrentlist)))

        # Return the list
        return torrentlist

    def getTorrentList(self):
        return self.list


    def printTorrentList(self):
        if self.list is None or len(self.list) == 0:
            print('No torrent found')
        else:
            line = colored('id \t\tseeders \tname', 'white', attrs=['bold'])
            print(line)
            even = True
            for torrent in self.list:
                if even :
                    attrs = ['reverse', 'blink']
                    even = False
                else:
                    attrs = None
                    even = True
                line = colored(torrent['id']+ '\t\t' + torrent['seeders'] + '\t\t' + torrent['name'], 'white', attrs=attrs)
                print(line)
