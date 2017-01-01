from __future__ import print_function
import urllib
import json


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
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


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Movie Ratings. Please give me a movie by saying, get the rating for Ghostbusters."
    reprompt_text = "Please give me a movie by saying, get the rating for Ghostbusters."

    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying Movie Ratings. Have a nice day! "

    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def movie_ratings(intent, session):
    card_title = intent['name']
    session_attributes = {}

    if 'Movie' in intent['slots']:
        movie = intent['slots']['Movie']['value']
        session_attributes = {}

        movie_with_spaces = movie.replace(" ", "%20")
        url = "http://www.omdbapi.com/?t=" + movie_with_spaces
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        response = data["Response"]

        if response == "False":
            speech_output = "I can't find the movie, " + movie + ". Please try again or try a different movie."
        else:
            imdb_rating = data["imdbRating"]
            title = data["Title"]

            if imdb_rating == "N/A":
                speech_output = "The IMDb rating for " + title + ", is unavailable. Please try a different movie."
            else:
                speech_output = "The IMDb rating for " + title + ", is " + imdb_rating + " out of 10."

        reprompt_text = ""
    else:
        speech_output = "I'm not sure which movie you specified. Please try again."
        reprompt_text = ""

    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    return get_welcome_response()


def on_intent(intent_request, session):
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "MovieRatings":
        return movie_ratings(intent, session)
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])


# --------------- Main handler ------------------

def lambda_handler(event, context):
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])