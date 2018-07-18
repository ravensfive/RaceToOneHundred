# main python program
import json, re, random

# lambda function handler - including specific reference to our skill
def lambda_handler(event, context):
    # if skill ID does not match my ID then raise error
    if (event["session"]["application"]["applicationId"] !=
            "amzn1.ask.skill.e26d2d99-6c48-498a-b589-b7b73b94d033"):
        raise ValueError("Invalid Application ID")

    # test if session is new
    if event["session"]["new"]: 
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    # test and set session status
    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

# define session start
def on_session_started(session_started_request, session):
    print ("Starting new session")

# define session launch
def on_launch(launch_request, session):
    return get_welcome_response()

# control intent call 
def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    if intent_name == "SetupGame":
        return setup_game(intent)
    elif intent_name == "SetupPlayers":
        return setup_players(intent)
    elif intent_name == "StartGame":
        return start_game()
    elif intent_name == "WhatsTheScore":
        return whats_the_score()
    elif intent_name == "PlayTurn":
        return play_turn()
    elif intent_name == "ResetGame":
        return reset_game('delete')
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

# define end session
def on_session_ended(session_ended_request, session):
    print("Ending session")

# handle end of session
def handle_session_end_request():
    card_title = "Thanks"
    speech_output = "See you soon"
    should_end_session = True
    speech_output = "<speak>" + speech_output + "</speak>"
    card_output = cleanssml(speech_output)
    return build_response({}, build_speechlet_response(card_title, speech_output, card_output, None, should_end_session))

# define welcome intent
def get_welcome_response():
    session_attributes = {}
    # set default value for numPoints
    global numPoints
    numPoints = 0
    card_title = "Welcome"
    speech_output = "Welcome to the race to one hundred game, if your ready to start the game, just say setup game to your chosen number of points "   
    reprompt_text = "Welcome to the race to one hundred game, if your ready to start the game, just say setup game to your chosen number of points"   
    should_end_session = False
    speech_output = "<speak>" + speech_output + "</speak>"
    card_output = cleanssml(speech_output)
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, card_output, reprompt_text, should_end_session))

# define setup game
def setup_game(intent):
    session_attributes = {}
    global numPoints
    # pick up number of players from slot in intent
    numPoints = intent['slots']['gamepoints']['value']

    # setup new json
    setupJson()

    # how many players do you have?
    card_title = "Game Setup"
    speech_output =  "I have setup a game to " + str(numPoints) + ", now we need to add your players, there is no maximum, just say add player followed by their name"
    reprompt_text = ""
    should_end_session = False
    speech_output = "<speak>" + speech_output + "</speak>"
    card_output = cleanssml(speech_output)
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, card_output, reprompt_text, should_end_session))

# define setup game
def setup_players(intent):
    # setup session attributes
    session_attributes = {}

    # test if the number of points has been set
    if numPoints != 0 :
        # pick up number of players from slot in intent
        playerName = intent['slots']['playername']['value']

        # append player to json
        addplayertoJson(len(playerdata['players'])+1,playerName,0,0,False,False,False,0,0)

        speech_output = playerName + " has been added to the game, either add another or say lets play" 
    
    else :
        speech_output = "I don't know how many points you want to play too, make sure you setup the game, by saying setup game to your chosen number of points"
    
    card_title = "Player Added"
    reprompt_text = ""
    should_end_session = False
    speech_output = "<speak>" + speech_output + "</speak>"
    card_output = cleanssml(speech_output)
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, card_output, reprompt_text, should_end_session))

# define setup game
def whats_the_score():
    # setup session attributes
    session_attributes = {}

    # test if there are players loaded into the json file
    if len(playerdata['players']) != 0 :
        
        # setup temporary variables
        speech_output = ""
        high_score = 0
        high_score_player_string = ""
        num_of_players_winning = 0

        # loop through json and establish the highest score and start to build play back string
        for p in playerdata['players']:
                # does this player have a score higher than the current high score
                if int(p['Score']) > high_score:
                    # if its higher set the high score to the newest high score
                    high_score = int(p['Score']) 
                # start output string
                speech_output = speech_output + " , " + p['Name'] + ' has ' + p['Score'] + " " + generatebreakstring(500,"ms")

        # loop through and extract all the players with the highest score
        for p in playerdata['players']:
                # does this player have the highest socre
                if int(p['Score']) == high_score :
                    # record how many players have the high score
                    num_of_players_winning + 1
                    # build string of winning players for play back
                    high_score_player_string = high_score_player_string + p['Name']  
        
        # if there is more than one player then it must be a draw, build the string to play it back
        if num_of_players_winning > 1 :
            speech_output = speech_output + ", its currently a draw between " + high_score_player_string + " with " + str(high_score) + " points" 
        # else there must be a winner, build the string to play it back
        else :
            speech_output = speech_output + high_score_player_string + " is winning, with " + str(high_score) + " points, " + generatebreakstring(500,"ms") + " just say roll dice to continue your game"
    
    else :
        speech_output = "You don't seem to have loaded any players, you can add a player by saying, add player, followed by their name"

    # output
    card_title = "Scores on the doors!"
    reprompt_text = ""
    should_end_session = False
    speech_output = "<speak>" + speech_output + "</speak>"
    card_output = cleanssml(speech_output)
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, card_output, reprompt_text, should_end_session))  

# define welcome intent
def start_game():
    # set up session attributes
    session_attributes = {}

    # test if there are players loaded into the json file
    if len(playerdata['players']) != 0 :

        # setup temporary variables
        speech_output = ""

        # select random number between 1 and the maximum length of the json file
        selectedplayer = random.randint(1,len(playerdata['players'])) - 1
        
        # udpate player in json file
        playerdata['players'][selectedplayer]['nextPlay'] = True

        speech_output = playerdata['players'][selectedplayer]['Name'] + " will start, " + playerdata['players'][selectedplayer]['Name'] + ". just say roll dice to get started"
    
    else:
     speech_output = "You don't seem to have loaded any players, you can add a player by saying, add player, followed by their name"
    
    # output
    card_title = "Starting Player Selected"
    reprompt_text = ""
    should_end_session = False
    speech_output = "<speak>" + speech_output + "</speak>"
    card_output = playerdata['players'][selectedplayer]['Name'] + " will start"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, card_output, reprompt_text, should_end_session)) 

# define play turn intent
def play_turn():
    # set up session attributes
    session_attributes = {}

    # setup temporary variables
    speech_output = ""
    playerselected = False

    # test if a player has already been selected at random 
    #if 'ID' in playerdata['players']:
    for p in playerdata['players'] :
        if p['nextPlay'] == True:
                playerselected = True

    # if no start player has been selected yet then make the choice
    if playerselected == False :
        # select random number between 1 and the maximum length of the json file
        selectedplayer = random.randint(1,len(playerdata['players'])) - 1
        
        # udpate player in json file
        playerdata['players'][selectedplayer]['nextPlay'] = True

        speech_output = playerdata['players'][selectedplayer]['Name'] + " will start, " + playerdata['players'][selectedplayer]['Name'] + ". just say roll dice to get started"
    
    # else play the turn
    else:
        playingPlayerID = 0
        next_player = ""

        # loop through players in json    
        for p in playerdata['players']:    
            # test if they are next to play
            if p['nextPlay'] == True :  
                
                # roll the dice and update variables in the json
                diceRoll = random.randint(1,6)
                p['lastRoll'] = diceRoll
                p['lastScore'] = p['Score']
                p['Score'] = str(int(p['Score']) + diceRoll)
                p['numGoes'] = p['numGoes'] + 1
                p['nextPlay'] = False
                p['didPlay'] = True

                # set playing player ID - will be used to set the next player later in function
                playingPlayerID = int(p['ID'])
                
                # test if some one has one the game
                if int(p['Score']) >= int(numPoints) :
                    p['hasWon'] = True
                    p['winsInSession'] = p['winsInSession'] + 1

                # build output
                speech_output = " <audio src='https://s3.amazonaws.com/alexaskillravensfive/DiceRoll.mp3' /> you rolled a " + str(p['lastRoll']) + generatebreakstring(500,'ms') + ", you now have " + str(p['Score']) + ' points, '  + generatebreakstring(500,'ms')

        # one in 10 chance of having another go
        if random.randint(1,10) == 10:
            next_player = "you get an extra go, say roll dice to go again "
            playerdata['players'][playingPlayerID-1]['nextPlay'] = True
        # set next player - if the playing ID is equal to the number of players then, reset to player one
        elif playingPlayerID == len(playerdata['players']):
            # set nextPlay to true
            playerdata['players'][0]['nextPlay'] = True        
            # build next_player string to be added to the speech output
            next_player = playerdata['players'][0]['Name'] + ", you're next up, you have " + str(playerdata['players'][0]['Score']) + ' points, '
        # if not then increment up to next player
        else :
            # set nextPlay to true
            playerdata['players'][playingPlayerID]['nextPlay'] = True
            # build next_player string to be added to the speech output
            next_player = playerdata['players'][playingPlayerID]['Name'] + ", you're next up, you have " + str(playerdata['players'][playingPlayerID]['Score']) + ' points'
    
        # do we have a winner
        winner = testforwinner()

        # if there is a winner then change winner message to the winner name
        if winner != "" :
            speech_output = speech_output + ", " + winner + " wins, if you want to play again with the same players just say lets play, if you want to setup a new game, say setup game to your chosen points number"    
            # reset game, also increments session wins by one
            reset_game('reset')
        else:
            speech_output = speech_output + next_player + ", say roll dice when you're ready"    

    # output
    card_title = "Dice Rolled"
    reprompt_text = ""
    should_end_session = False
    speech_output = "<speak>" + speech_output + "</speak>"
    card_output = cleanssml(speech_output)
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, card_output, reprompt_text, should_end_session)) 

def reset_game(resettype):
    # set up session attributes
    session_attributes = {}

    if resettype == "delete":
        del playerdata['players']
        speech_output = "I've reset the game, just say setup game to your chosen number of points to start the game"
    else:
        # reset json
        for p in playerdata['players']:
            p['lastScore'] = 0
            p['lastRoll'] = 0
            p['Score'] = 0
            p['nextPlay'] = False
            p['didPlay'] = False
            p['hasWon'] = False
            p['numGoes'] = 0

            speech_output =  "I've reset the game, say lets play or roll dice to start the game again"

    # output
    card_title = "Reset Game"
    reprompt_text = ""
    should_end_session = False
    speech_output = "<speak>" + speech_output + "</speak>"
    card_output = cleanssml(speech_output)
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, card_output, reprompt_text, should_end_session))       
                
    
# build message response
def build_speechlet_response(title, output, cardoutput, reprompt_text, should_end_session):
    return {"outputSpeech": {"type": "SSML", "ssml":  output},
            "card": {"type": "Simple","title": title,"content": cardoutput},
            "reprompt": {"outputSpeech": {"type": "PlainText","text": reprompt_text}},
            "shouldEndSession": should_end_session}

# build response
def build_response(session_attributes, speechlet_response):
    return {
    "version": "1.0",
    "sessionAttributes": session_attributes,
    "response": speechlet_response }

# function to generate the ssml needed for a break
def generatebreakstring(pause, timetype):
    # generate the SSML string for break with dynamic length
    breakstring = '<break time="' + str(pause) + timetype + '"/>'
    return breakstring

# function to automatically remove ssml markup, needed to generate the card output - which is what is shown on screen
def cleanssml(ssml):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', ssml)
    return cleantext

# setup Json for game
def setupJson() :
    global playerdata
    playerdata = {}
    playerdata['players'] = []

# add player to json
def addplayertoJson(ID,Name,lastScore,lastRoll,nextPlay,didPlay,hasWon,numGoes,sessionWins) :
    playerdata['players'].append({    
    'ID': ID ,
    'Name': Name,
    'lastScore': lastScore,
    'lastRoll': lastRoll,
    'Score': "0",
    'nextPlay': nextPlay,
    'didPlay': didPlay,
    'hasWon': hasWon,
    'numGoes': numGoes,
    'winsInSession': sessionWins
    })

# test for a winner
def testforwinner():
    # setup temporary variables
    winner = ""
    # loop through players in json
    for p in playerdata['players'] :   
        # if anyone has hasWon set to true then there is a winner return the name
        if p['hasWon'] == True :
                winner = p['Name'] 
    return winner          


        
