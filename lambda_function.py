from __future__ import print_function
import db
from ir import IrishRailRTPI
import json
import string

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


def get_welcome_response():
    #start up message
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Are you getting the bus or the train?"
    #if user input is not understood use reprompt text
    reprompt_text = "which transport service are you looking for?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

#train times from ir.py file
def get_train_time(intent):
    session_attributes = {}
    card_title = "train times"
    speech_output = ""
    train_times = IrishRailRTPI()
    origin = "Coolmine"
    destination = "Maynooth"
    data = json.dumps(train_times.get_station_by_name(origin, destination), indent=4, sort_keys=False)
    resp = json.loads(data)
    try:
        for i in range(len(resp)):  #len(resp) returns the amount of dictionaries
            print("{} : {}".format(i,resp[i]['destination']))
            des = resp[i]['destination']
            if des.lower()==destination.lower(): #filter out by direction and make into lower case
                due_time = resp[i]["due_in_mins"]
                if due_time == "Due":
                    speech_output = "The next "+destination+" is due now"
                else:
                    speech_output = "the next "+destination+" train is in "+due_time+" minutes"
                break
    
    except:
        speech_output = "There were no trains found for your request. Please try asking again"

    reprompt_text = "would you like train or bus times"
    should_end_session = True

    return build_response(session_attributes,build_speechlet_response(
        card_title, speech_output,reprompt_text, should_end_session
        ))

#get the bus times from db.py file
def get_bus_time(intent):
    card_title="Bus times"
    session_attributes={}

    route = intent['slots']['RouteName']['value']
    form_route = route.translate({ord(c): None for c in string.whitespace}) #remove whitespaces
    stop_number = int(intent['slots']['stopNumber']['value'])
    g = db.RtpiApi(user_agent='test')
    bus_times=g.rtpi(stop_number,form_route)
    try:
        next_bus = bus_times.results[0]['duetime']
        
        if next_bus == "Due":
            speech_output = "the next "+form_route+" bus calling at stop "+str(stop_number)+" is due now "
        else:
            speech_output="the next "+form_route+" bus calling at stop: "+str(stop_number)+" is in "+str(next_bus)+ " minutes"

    except:
        speech_output = "there are currently no such buses at the requested stop"
        
    reprompt_text="would you like train or bus times"
    should_end_session=True

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def handle_end_request():
    card_title = "Thank you for using the Transport times skill"
    speech_output = "Thank you for using this skill"
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def session_started(session_started_request, session):
    #start of the session
    pass

def launch(launch_request, session):
    #default request
    return get_welcome_response()

def on_intent(intent_request, session):
    #find out what intent needs to be triggered from user input
    intent = intent_request['intent']
    name_intent = intent_request['intent']['name']

    if name_intent == "GetTrainTimes":
        return get_train_time(intent)
    elif name_intent == "GetBusTimes":
        return get_bus_time(intent)
    #built in intents to stop interaction
    elif name_intent == "AMAZON.CancelIntent" or name_intent == "AMAZON.StopIntent":
        return handle_end_request()
    elif name_intent == "AMAZON.HelpIntent":
        return get_welcome_response()
    else:
        raise ValueError("Invalid intent")

def session_ended(session_ended_request, session):
    print("session_ended requestId=" + session_ended_request['requestId'] +", sessionId=" + session['sessionId'])


def lambda_handler(event, context):
    #what type of request is incoming?
    if event['session']['new']:
        session_started({'requestId': event['request']['requestId']}, event['session'])
    if event['request']['type'] == "LaunchRequest":
        return launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return session_ended(event['request'], event['session'])