class Conf:
    # Hard conf
    server = 'irc.chat.twitch.tv'
    port = 6667

    # Bot account conf
    nickname = ""
    token = ""

    # Run config
    channel = ""

    ignoredUsers = [
    ]

    mods = [
    ]

    # THESE ARE WORDS THE BOT SHOULD NEVER LEARN.
    # I FEEL DISGUSTING TYPING THEM.
    # BUT BY THIS LIST EXISTING THEY WILL NOT PERPETUATE.
    # Some are here to keep the bot from being political.
    blacklisted_words = [
    ]

    CMD_TOGGLE = "-neural"

    CMD_CLEAR = "-refreshing"
    CMD_WIPE = "-wipe"
    CMD_SET_NUMBER = "-number"
    CMD_ALIVE = "-ping"
    CMD_UNIQUE = "-unique"
    CMD_EXIT = "-exit"

    SELF_PREFIX = "Maintenance Message: "

    owner = ""