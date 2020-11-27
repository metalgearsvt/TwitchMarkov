class Conf:
    # Hard conf
    server = 'irc.chat.twitch.tv'
    port = 6667

    # Bot account conf
    # Lowercase name
    nickname = ""
    # oauth generate with https://twitchapps.com/tmi/
    token = ""

    # Run config
    # Lowercase channel to join.
    channel = ""

    # Add users to ignore, lowercase.
    ignoredUsers = [
        "nightbot", "moobot", "streamelements", "streamlabs"
    ]
    
    # Add mods who can use commands, lowercase.
    mods = [
        
    ]

    # THESE ARE WORDS THE BOT SHOULD NEVER LEARN.
    # I FEEL DISGUSTING TYPING THEM.
    # BUT BY THIS LIST EXISTING THEY WILL NOT PERPETUATE.
    # Some are here to keep the bot from being political.
    
    # I didn't want to commit them to GitHub.
    # Add your own, case insensitive.
    blacklisted_words = [
    ]

    # Rename these as you please.
    CMD_TOGGLE = "-neural"

    CMD_CLEAR = "-refreshing"
    CMD_WIPE = "-wipe"
    CMD_SET_NUMBER = "-number"
    CMD_ALIVE = "-ping"
    CMD_UNIQUE = "-unique"
    CMD_EXIT = "-exit"

    SELF_PREFIX = "Maintenance Message: "

    # Your Twitch name, lowercase.
    owner = ""