# t411todeluge
Download torrents from t411 and send them to a remote deluge daemon



Setup
-----

      sudo pip install -r requirements.txt

You need a username and password to access your deluge's server.
To create one either append it to

* ~/.config/deluge/auth, or to
* /var/lib/deluge/.config/deluge/auth

Like that:

      username:password:permission



For example, (10 being the higher permission):

      johndoe:123456:10

Next, copy the default ini config file :

      cp config.ini.default config.ini
      nano config.ini
      # edit your info for t411 & deluge
      # and that's it

Use
---

Search by title :

      ./t411todeluge.py -t "Mr.Robot"

Search by title, and season :

      ./t411todeluge.py -t "Mr.Robot" -s 1

Search by title, season and episode :

      ./t411todeluge.py -t "Mr.Robot" -s 1 -e 2

Of course, you can just search anything in the title

      ./t411todeluge.py -t "Daft.Punk"

And to upload a torrent to your deluge server, just add:

      -i torrent_id_got_from_first_column_in_search

For example:

      ./t411todeluge.py -i 5339837


Troubleshoot
------------

In case of your t411 token being invalid, just remove the user.access file in the root directory, so it get a new one from t411.
It's one thing to improve later (reuse username & password when token is invalid to get a new one automatically)
