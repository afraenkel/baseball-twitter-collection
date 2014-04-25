#! /usr/bin/env python

#####
# For opening the twitter live-stream:
# when run directly, needs three arguments:
# (1) game # of the day being collected
# (2) game id # on espn.com (for live updates)
# (3) game url on espn.com
#####

import sys, os, subprocess, time, json, tweepy

from baseball_params import *
from baseball_info import in_game_info, game_info

# Twitter authentication 

auth = tweepy.OAuthHandler( CONSUMER_KEY, CONSUMER_SECRET )
auth.set_access_token( ACCESS_KEY, ACCESS_SECRET )
api = tweepy.API(auth)

# stream listener class for baseball games:

class CustomStreamListener(tweepy.StreamListener):
    def __init__(self,api = None, fprefix = 'streams',
                 game_num = sys.argv[1], game_id = sys.argv[2],
                 game_url = sys.argv[3] ):
        self.api = api
        # attributes for game-updates:
        self.time_counter = time.time()
        self.game_num = game_num
        self.game_id = game_id
        self.game_url = game_url
        # attributes for file storage:
        self.fprefix = fprefix
        self.output = open( BASE_LOC + fprefix + '.'
                            + time.strftime('%Y%m%d-%H%M%S') + '.json', 'a')
        self.output_RT = open( BASE_LOC + fprefix + '.'
                               + time.strftime('%Y%m%d-%H%M%S')
                               + '_RT.json', 'a')
        self.log = open( BASE_LOC + fprefix + '.'
                         + time.strftime('%Y%m%d-%H%M%S') + '_log.json', 'a')
        # initialize JSON files:
        self.output.write("[")
        self.output_RT.write("[")
        self.log.write("[")
    
    def on_status(self, status):
        print status.text.encode('utf-8')
        # Dictionary for saving (text,id,time)
        D={'text': status.text.encode('utf-8'),
           'id': status.id_str,
           'time': str(status.created_at) }
        # Save tweets/retweets in different files
        if hasattr(status, 'retweeted_status') is True:
            D['RT_id'] = status.retweeted_status.id_str
            json.dump( D, self.output_RT )
            self.output_RT.write(',')
        else:
            json.dump( D, self.output )
            self.output.write(',')
        # keep track of elasped time and occasionally
        # check for the game status.
        action = True
        if time.time() - self.time_counter > 15*60:
            gd = in_game_info( self.game_id, self.game_url )
            gd['time'] = time.strftime('%Y%m%d-%H%M%S')
            # write to the log file
            json.dump( gd, self.log )
            self.log.write(',')
            status = gd['status']
            # determine if game's live
            if status in ['final','PPD']:
                self.output.write("]")
                self.output.close()
                self.output_RT.write("]")
                self.output_RT.close()
                self.log.write("]")
                self.log.close()
                action = False
            else:
                self.time_counter = time.time()
        return( action )

    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream

sapi = tweepy.streaming.Stream(auth, CustomStreamListener(), timeout=60)
sapi.filter(track=[ TEAM_HASH , TEAM_ACCT ])

# Clean up launchd and remove temp files:

plist_label = PLIST_DIR + 'local.bb_game' + str( sys.argv[1] )
subprocess.call( ['launchctl','unload', plist_label + '.plist'] )
os.remove( plist_label + '.plist' )
os.remove( PRGPATH + 'game' + str( sys.argv[1] ) )
