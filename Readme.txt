
baseball-twitter-collector opens the Twitter live-stream during game-time, collects all tweets associated to your specified team (default: Oakland Athletics) during the game, and disconnects from the stream when the game ends.

* Requires OSX to run.
* Requires scheduling the file "baseball_plist.py" to run at 11AM EST daily via launchd.

Summary of the .py files:
* "baseball_plist.py" creates a plist for running the script for the days game.
* "baseball_info.py" updates the game status / time from the ESPN.com website. 
* "baseball_params.py" contains your filepaths, tokens, keys, etc.
* "baseball_stream.py" contains the twitter API interaction.
