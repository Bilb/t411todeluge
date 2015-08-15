#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Python interface for T411.me

Authors :
 * Arnout Pierre <pierre@arnout.fr>
 * Ackermann Audric <audric.bilb@gmail.com>
"""


from getpass import getpass
from json import loads, dumps
from urllib2 import urlopen, URLError, HTTPError, Request
import os, sys, logging, requests, base64

import t411


HTTP_OK = 200
API_URL = 'https://api.t411.io/%s'
USER_CREDENTIALS_FILE = 'user.json'



class T411Exception(BaseException):
    pass

class T411(object):
    """ Base class for t411 interface """

    def __init__(self, username, password) :
        """ Get user credentials and authentificate it, if any credentials
        defined use token stored in user file
        """

        try :
            with open(USER_CREDENTIALS_FILE) as user_cred_file:
                self.user_credentials = loads(user_cred_file.read())

                if 'uid' not in self.user_credentials or 'token' not in \
                        self.user_credentials:
                    logging.error('Wrong data found in user file: %s' % USER_CREDENTIALS_FILE)
                    raise T411Exception('Wrong data found in user file')
                else:
                    # nothing todo : we got credentials from file
                    logging.info('Using credentials from user file: %s' %USER_CREDENTIALS_FILE)
        except IOError as e:
            # we have to ask the user for its credentials and get
            # the token from the API
            while True:
                user = raw_input('Please enter username: ')
                password = getpass('Please enter password: ')
                try:
                    self._auth(user, password)
                except T411Exception as e:
                    logging.error('Error while trying identification as %s: %s' %(user, e.message))
                else:
                    break
        except T411Exception as e:
            raise T411Exception(e.message)
        except Exception as e:
            logging.error('Error while reading user credentials: %s.'% e.message)
            raise T411Exception('Error while reading user credentials: %s.'\
                    % e.message)

    def _auth(self, username, password) :
        """ Authentificate user and store token """
        self.user_credentials = self.call('auth', {'username': username, 'password': password})

        if 'error' in self.user_credentials:
            raise T411Exception('Error while fetching authentication token: %s'\
                    % self.user_credentials['error'])
        # Create or update user file
        user_data = dumps({'uid': '%s' % self.user_credentials['uid'], 'token': '%s' % self.user_credentials['token']})
        with open(USER_CREDENTIALS_FILE, 'w') as user_cred_file:
            user_cred_file.write(user_data)
        return True

    def call(self, method = '', params = None) :
        """ Call T411 API """

        # authentification request
        if method == 'auth' :
            req = requests.post(API_URL % method, data=params)
        # other type requests : include Authorizaton credentials to the request
        else:
            req = requests.post(API_URL % method, data=params,
                headers={'Authorization': self.user_credentials['token']}  )

        if req.status_code == requests.codes.OK:
            return req.json()
        else :
            raise T411Exception('Error while sending %s request: HTTP %s' % \
                    (method, req.status_code))

    def search(self, to_search, limit) :
        """ Get torrent results for specific search """
        return self.call('torrents/search/%s?&limit=%s' % (to_search, limit))

    def download(self, torrent_id, location) :
        """ Download a torrent """
        method = 'torrents/download/%s' % torrent_id


        print("Downloading torrent %s to : %s"  %(torrent_id, location))
        try:
            with open(location, 'wb') as handle:
                req = requests.get(API_URL % method,
                    headers={'Authorization': '%s' %self.user_credentials['token']})

                if req.status_code == requests.codes.OK:
                    torrent_data = None
                    try:
                        req_json = req.json()
                        if 'error' in req_json:
                            logging.error('Got an error response from t411 server: %s' %req_json['error'])
                    except ValueError:
                        # unable to jsonify it, we considere response is the torrent file.
                        # just download it
                        torrent_data = ''
                        for block in req.iter_content(1024):
                            if not block:
                                break
                            handle.write(block)
                            torrent_data += block

                        #print("Download success. Torrent file saved to '%s'" % location)
                    return base64.b64encode(torrent_data)
                else:
                    logging.error('Invalid response status_code : %s' (req.status_code))
        except Exception as e:
            logging.error('Download of torrent %s failed : %s' %(torrent_id, e.message))
            raise T411Exception(e.message)




    def me(self) :
        """ Get personal informations """
        return self.call('users/profile/%s' % self.user_credentials['uid'])

    def user(self, user_id) :
        """ Get user informations """
        return self.call('users/profile/%s' % user_id)

    def categories(self) :
        """ Get categories """
        return self.call('categories/tree')

    def terms(self) :
        """ Get terms """
        return self.call('terms/tree')

    def details(self, torrent_id) :
        """ Get torrent details """
        return self.call('torrents/details/%s' % torrent_id)




    def top100(self) :
        """ Get top 100 """
        return self.call('/torrents/top/100')

    def top_today(self) :
        """ Get top today """
        return self.call('/torrents/top/today')


    def top_week(self) :
        """ Get top week """
        return self.call('/torrents/top/week')

    def top_month(self) :
        """ Get top month """
        return self.call('/torrents/top/month')

    def get_bookmarks(self) :
        """ Get bookmarks of user """
        return self.call('/bookmarks')

    def add_bookmark(self, torrent_id) :
        """ Get bookmarks of user """
        return self.call('/bookmarks/save/%s' % torrent_id)


    def delete_bookmark(self, torrent_id) :
        """ Delete a bookmark """
        return self.call('/bookmarks/delete/%s' % torrent_id)


if __name__ == "__main__":
    t411 = T411()





def getbest(self):
    """
    Return the best choice (or None if no serie founded)
    """
    if (len(self.list) > 0):
        return self.list[0]
    else:
        return None


def getall(self):
    """
    Return all the matched series (or None if no serie founded)
    """
    if (len(self.list) > 0):
        return self.list
    else:
        return None



    def downloadbest(self):
        best = self.getbest()
        if best is not None:
            #use title of torrent as filename. Will be saved as 'filename' + '.torrent'
            print(best)
            return self.source.download(best[2], filename=best[0])

        else:
            logging.error("Can't download because no torrent was found for this search.")
            return None
