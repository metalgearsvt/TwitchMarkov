from conf import Conf
from emoji import demojize
import datetime
import socket
import markovify
import re
import traceback

GENERATE_ON = 35
CLEAR_LOGS_AFTER = False
ALLOW_MENTIONS = True
UNIQUE = True
SEND_MESSAGES = True
CULL_OVER = 8000
TIME_TO_CULL = datetime.timedelta(hours=1)

messageCount = 0
TIMES_TO_TRY = 1000
PERCENT_UNIQUE_TO_SAVE = 50.0
STATE_SIZE = 2
PHRASES_LIST = []
LOGFILE = "uninitialized.txt"

def listMeetsThresholdToSave(part, whole):
    global PERCENT_UNIQUE_TO_SAVE
    pF = float(len(part))
    wF = float(len(whole))
    if wF == 0:
        return False
    uniqueness = (pF/wF) * float(100)
    return (uniqueness >= PERCENT_UNIQUE_TO_SAVE)

def filterMessage(message):

    if checkBlacklisted(message):
        return None
    
    # Remove links
    # TODO: Fix
    message = re.sub(r"http\S+", "", message)

    # Remove mentions
    if ALLOW_MENTIONS == False:
        message = re.sub(r"@\S+", "", message)

    # Remove just repeated messages.
    words = message.split()
    # Make list unique
    uniqueWords = list(set(words))
    if not listMeetsThresholdToSave(uniqueWords, words):
        return None

    # Space filtering
    message = re.sub(r" +", " ", message)
    message = message.strip()
    return message

def writeMessage(message):
    global CLEAR_LOGS_AFTER
    global LOGFILE
    message = filterMessage(message)
    if message != None and message != "":
        if messageCount == 0 and CLEAR_LOGS_AFTER:
            f = open(LOGFILE, "w", encoding="utf-8")
        else:
            f = open(LOGFILE, "a", encoding="utf-8")
        f.write(message + "\n")
        f.close()
        return True
    return False

def generateMessage():
    global LOGFILE
    global PHRASES_LIST
    with open(LOGFILE, encoding="utf-8") as f:
        text = f.read()
    text_model = markovify.NewlineText(text, state_size=STATE_SIZE)
    testMess = None
    if UNIQUE and (len(PHRASES_LIST) > 0):
        foundUnique = False
        tries = 0
        while not foundUnique and tries < 20:
            testMess = text_model.make_sentence(tries=TIMES_TO_TRY)
            if not (testMess in PHRASES_LIST):
                foundUnique = True
            tries += 1
    else:
        testMess = text_model.make_sentence(tries=TIMES_TO_TRY)
    if not (testMess is None):
        PHRASES_LIST.append(testMess)
    else:
        PHRASES_LIST = [testMess]
    return testMess

def generateAndSendMessage(sock, channel):
    if SEND_MESSAGES:
        markoved = generateMessage()
        if markoved != None:
            sendMessage(sock, channel, markoved)
        else:
            print("Could not generate.")

def sendMessage(sock, channel, message):
    if SEND_MESSAGES:
        sock.send("PRIVMSG #{} :{}\r\n".format(channel, message).encode("utf-8"))

def sendMaintenance(sock, channel, message):
    sock.send("PRIVMSG #{} :{}\r\n".format(channel, Conf.SELF_PREFIX + message).encode("utf-8"))

def handleAdminMessage(username, channel, sock):
    global CLEAR_LOGS_AFTER
    global LOGFILE
    global SEND_MESSAGES
    global GENERATE_ON
    global UNIQUE
    if username == channel or username == Conf.owner or username in Conf.mods:
        # Log clearing after message.
        if message == Conf.CMD_CLEAR:
            if CLEAR_LOGS_AFTER == True:
                CLEAR_LOGS_AFTER = False
                sendMaintenance(sock, channel, "No longer clearing memory after message! betch200IQ")
            else:
                CLEAR_LOGS_AFTER = True
                sendMaintenance(sock, channel, "Clearing memory after every message! FeelsDankMan")
            return True
        # Wipe logs
        if message == Conf.CMD_WIPE:
            f = open(LOGFILE, "w", encoding="utf-8")
            f.close()
            sendMaintenance(sock, channel, "Wiped memory banks. D:")
            return True
        # Toggle functionality
        if message == Conf.CMD_TOGGLE:
            if SEND_MESSAGES:
                SEND_MESSAGES = False
                sendMaintenance(sock, channel, "Messages will no longer be sent! D:")
            else:
                SEND_MESSAGES = True
                sendMaintenance(sock, channel, "Messages are now turned on! :)")
            return True
        # Toggle functionality
        if message == Conf.CMD_UNIQUE:
            if UNIQUE:
                UNIQUE = False
                sendMaintenance(sock, channel, "Messages will no longer be unique. PogO")
            else:
                UNIQUE = True
                sendMaintenance(sock, channel, "Messages will now be unique. PogU")
            return True
        # Generate message on how many numbers.
        if message.split()[0] == Conf.CMD_SET_NUMBER:
            try:
                stringNum = message.split()[1]
                if stringNum != None:
                    num = int(stringNum)
                    if num <= 0:
                        raise Exception
                    GENERATE_ON = num
                    sendMaintenance(sock, channel, "Messages will now be sent after " + GENERATE_ON + " chat messages. DankG")
            except:
                    sendMaintenance(sock, channel, "Current value: " + str(GENERATE_ON) + ". To set, use: " + str(Conf.CMD_SET_NUMBER) + " [number of messages]")
            return True
        # Check if alive.
        if message == Conf.CMD_ALIVE:
            sendMaintenance(sock, channel, "Yeah, I'm alive and learning. betch2IQ")
            return True
        # Kill
        if (username == channel or username == Conf.owner) and message == Conf.CMD_EXIT:
            sendMaintenance(sock, channel, "You have killed me. D:")
            exit()
    return False

def isUserIgnored(username):
    if (username in Conf.ignoredUsers):
        return True
    return False

def cullFile():
    fin = open(LOGFILE, "r", encoding="utf-8")
    data_list = fin.readlines()
    fin.close()
    
    size = len(data_list)
    if size <= CULL_OVER:
        return
    size_delete = size // 2
    del data_list[0:size_delete]
    
    fout = open(LOGFILE, "w", encoding="utf-8")
    fout.writelines(data_list)
    fout.close()

def checkBlacklisted(message):
    # Check words that the bot should NEVER learn.
    for i in Conf.blacklisted_words:
        if re.search(r"\b" + i, message, re.IGNORECASE):
            return True
    return False

def shouldCull(last_cull):
    now_time = datetime.datetime.now()
    time_since_cull = now_time - last_cull
    if time_since_cull > TIME_TO_CULL:
        cullFile()
        last_cull = datetime.datetime.now()
    return last_cull

# PROGRAM HERE

last_cull = datetime.datetime.now()

while True:
    # Initialize socket.
    sock = socket.socket()

    # Connect to the Twitch IRC chat socket.
    sock.connect((Conf.server, Conf.port))

    # Authenticate with the server.
    sock.send(f"PASS {Conf.token}\n".encode('utf-8'))
    sock.send(f"NICK {Conf.nickname}\n".encode('utf-8'))
    sock.send(f"JOIN #{Conf.channel}\n".encode('utf-8'))

    LOGFILE = Conf.channel + "Logs.txt"

    print("Connected", Conf.nickname, ".")

    # Main loop
    while True:
        try:
            # Receive socket message.
            resp = sock.recv(2048).decode('utf-8')

            # Keepalive code.
            if resp.startswith('PING'):
                sock.send("PONG\n".encode('utf-8'))
            # Actual message that isn't empty.
            elif len(resp) > 0:
                try:
                    msg = demojize(resp)
                    # Break out username / channel / message.
                    regex = re.search(r':(.*)\!.*@.*\.tmi\.twitch\.tv PRIVMSG #(.*) :(.*)', msg)
                    # If we have a matching message, do something.
                    if regex != None:
                        # The variables we need.
                        username, channel, message = regex.groups()
                        message = message.strip()

                        # Handle ignored users.
                        if isUserIgnored(username):
                            continue

                        # Broadcaster saying something.
                        if handleAdminMessage(username, channel, sock):
                            continue

                        # Validate and print message to the log.
                        if not writeMessage(message):
                            continue

                        # At this point, it's not an admin message, and it's a successful, valid entry.

                        # Increase messages logged.
                        messageCount += 1

                        # Generate Markov
                        if (messageCount % GENERATE_ON) == 0:
                            generateAndSendMessage(sock, channel)
                            last_cull = shouldCull(last_cull)
                            messageCount = 0
                except Exception as e:
                    print("Inner")
                    traceback.print_exc() 
                    print(e)
        except Exception as e:
            print("Outer")
            traceback.print_exc() 
            print(e)
            break