#! /usr/bin/env python

from baseball_info import game_info
import datetime, plistlib, subprocess

from baseball_params import *

#####
# Functions to create a plist / applescript associated to a game
#####

def create_plist( game, game_num ):
    """ takes a game dictionary and outputs plist for it """
    t = game['game_time']
    if t.minute < 10:
        hr = t.hour - 1
        mn = (t.minute - 10) % 60
    else:
        hr = t.hour
        mn = (t.minute - 10)
    plist_dict = { 'Label' : 'local.bb_game' + str( game_num ),
                   'ProgramArguments': ['osascript',
                                        PRGPATH + 'game' + str(game_num) ],
                   'StartCalendarInterval': { 'Hour' : hr, 'Minute' : mn }
                    }
    return( plist_dict )

def create_applescript( game, game_num ):
    """ takes game dictionary and outputs an applescript file """
    userinput = ' '.join( [ PYTHONPATH, PRGPATH + 'baseball_stream.py',
                            str(game_num), '\'' + game['game_id'] + '\'',
                            '\''+ game['game_url'] + '\'' ] )
    text = ' '.join( [ 'tell','application', '\"Terminal\"','\n',
                         '\t', 'activate', '\n',
                         '\t', 'do', 'script', '\"'+ userinput + '\"', '\n',
                         'end', 'tell' ] )
    f = open( PRGPATH + 'game' + str(game_num), 'wb' )
    f.write( text )
    f.close()
    


# Get the game list for the day and create plists
# to run the twitter collector for each game.

glist = game_info()

if glist is not None:
    counter = 1
    for game in glist:
        create_applescript( game, counter )
        pl = create_plist( game, counter  )
        file_name = ''.join([ PLIST_DIR, pl['Label'], '.plist' ])
        f = open( file_name , 'wb' )
        plistlib.writePlist( pl, f )
        f.close()
        subprocess.call( ['launchctl','load', file_name] )
        counter = counter + 1
else:
    print "no games today"


