#! /usr/bin/env python

import urllib2, datetime, string, re
from bs4 import BeautifulSoup

from baseball_params import *

BASE_URL = 'http://espn.go.com'


def date_str( d ):
    """ takes a datetime object and outputs a string
    representation as found on ESPN website """
    MONTH_DICT = {1:'January',2:'February',3:'March',
              4:'April',5:'May',6:'June',
              7:'July',8:'August',9:'September',
              10:'October',11:'November',12:'December' }
    month_str = MONTH_DICT[ d.month ]
    date_str = ''.join( [ month_str, ' ', str( d.day ), ', ', str( d.year )] )
    return(date_str)


def game_info():
    """ outputs a list of games dictionaries with keys
    game_time, game_url, game_vs. """
    today = date_str( datetime.date.today() )
    tomorrow = date_str( datetime.date.today()
                        + datetime.timedelta(days=1) )
    # Lookup MLB schedule on ESPN website:
    response = urllib2.urlopen('http://espn.go.com/mlb/schedule')
    schedule = response.read()
    # restrict schedule to be only
    # games listed for the current day
    minIndex = string.find(schedule,today)
    maxIndex = string.find(schedule,tomorrow)
    schedule = schedule[minIndex:maxIndex]
    # extract team info
    soup = BeautifulSoup( schedule )
    games = soup.find_all('tr')  # info for each game
    team_games = []
    for game in games:
        if TEAM_LOC in str( game ) or TEAM_NAME in str( game ):
            team_games.append( game )
    if team_games != []:
        L = []
        for game in team_games:
            # Find the game time of game.
            time_pattern = '1[0-2]:[0-5][0-9] [AP]M|[1-9]:[0-5][0-9] [AP]M'
            t = re.search( time_pattern, str(game) )
            time_str = t.group(0)
            game_time = datetime.datetime.strptime(time_str,'%I:%M %p').time()
            # Find the game url
            game_tag =  game.find_all('a')[0]
            game_url =  BASE_URL + game_tag['href']
            game_id = ''.join( re.findall('[0-9]', game_tag['href'] ) )
            # Create a game dictionary
            D = { 'game_time' : game_time,
                  'game_url'  : game_url,
                  'game_id'   : game_id  }
            L.append( D )
    else:
         L =  None
    return( L )


def in_game_info( g_id, g_url ):
    """ inputs a game id (output from game_info)
    outputs 'pregame','live' + inning, or FINAL """ 
    response = urllib2.urlopen( g_url )
    page = response.read()
    soup = BeautifulSoup( page )
    games = soup.find('div', {'class':'scoreboard-container'})
    games = games.find_all('a')
    for game in games:
        if g_id in str(game):
            # find game status (pregame/live/final)
            status = game.find('div',{'class':'game-status'})['class']
            status = status[1]
            if status[1] == 'pregame':
                clock = game.find('span',{'class':'clock'}).text
                if clock == "Postponed":
                    status = 'PPD'
            # home / away teams:
            teams = game.find('div',{'class','teams'})
            home_team = teams.find('span',{'class','home'}).text
            away_team = teams.find('span',{'class','away'}).text
            # scores:
            home_score = game.find('span',{'class','homeScore'}).text
            away_score = game.find('span',{'class','awayScore'}).text
            # Compile dictionary w/this info
            D = { 'status' : status,
                  'home_team' : home_team,
                  'away_team' : away_team,
                  'home_score' : home_score,
                  'away_score' : away_score,
                  }
            break
    return( D )

