"""
Jamie Brandon
David Rubio Vallejo
11/09/2018
"""

# ! /usr/bin/env python3
import os
import sys
import random
import datetime
from flask import Flask, request, jsonify, make_response
from GrammarChecker import GrammarChecker
from langdetect import detect

app = Flask(__name__)

gc = GrammarChecker()


def get_df_intent(req):
    """Returns the intent name as defined in the DialogFlow app"""
    return req.get('queryResult').get('intent').get('displayName')


def get_df_utterance(req):
    """
    original user utterance
    :param req: request object from DF
    :return: string, user utterance
    """
    return req.get('originalDetectIntentRequest').get('payload').get('inputs')[0].get('rawInputs')[0].get('query')

def get_al_utterance(req):
    """
    original user utterance -- alexa
    :param req: request object from ALEXA
    :return: string, user utterance
    """
    return req.get('request')

def handle_intent(intent):
    """
    provide the response string given the user's intent
    :param intent: string, whatever intent DF matched
    :return: response string
    """
    response = ""
    if intent == 'Alarmas':
        response += "¡Muy bien! The alarm is set now!"

    elif intent == 'Calendario':
        response += "¡Muy bien! The event is in your calendar!"

    elif intent == 'ElTiempo':
        weather_list = ["Parece que va a hacer buen tiempo", "¡Hace sol!", "Esta despejado", "Hace un poco de frio"]
        response += random.choice(weather_list)

    elif intent == 'LaHora':
        response += "Ahora son las:\n"
        print("EN INTENT LaHora", file=sys.stdout)
        response += str(datetime.datetime.time(datetime.datetime.now()))[:5]
        print("THE ERROR IS NOT WIITH DATETIME", file=sys.stdout)

    elif intent == 'Luces':
        response += "¡Perfecto! The lights are set now."

    elif intent == 'Restaurantes':
        response += "¡Tu español es perfecto! I sent you some restaurants to your email account."

    return response


def give_corrected_response(intent):
    if intent == 'Alarmas':
        response = "That was almost correct!\n"
        response += "A better way would be: 'Pon la alarma a las diez y media'.\n"
        response += "Or: 'Crea una alarma a las cuatro menos veinticinco'.\n"
        response += "Please try again! :)"

    elif intent == 'Calendario':
        response = "That was almost correct!\n"
        response += "A better way would be: 'Pon una nota para el cinco de marzo'.\n"
        response += "Please try again! :)"

    elif intent == 'ElTiempo':
        response = "That was almost correct!\n"
        response += "A better way would be: 'Dime que tiempo hace en Waltham'\n"
        response += "Or: 'Cual es el tiempo en Boston'.\n"
        response += "Please try again! :)"

    elif intent == 'LaHora':
        response = "That was almost correct!\n"
        response += "A better way would be: 'Que hora es'\n"
        response += "Or: 'Me dices la hora'.\n"
        response += "Please try again! :)"

    elif intent == 'Luces':
        response = "That was almost correct!\n"
        response += "A better way would be: 'Enciende las luces'\n"
        response += "Or: 'Apaga la luz'.\n"
        response += "Please try again! :)"

    elif intent == 'Restaurantes':
        response = "That was almost correct!\n"
        response += "A better way would be: 'Muestrame restaurantes en Waltham'\n"
        response += "Please try again! :)"

    return response

def handle_intent_ssml(intent):
    """
    SSML for spanish intent
    :param intent:
    :return:
    """


def get_language(req):
    if "queryResult" in req:
        return detect(get_df_utterance(req))
    else:
        return detect(get_al_utterance(req))


def handle_english_intent(intent):
    if intent == 'Alarmas':
        responses = ['Por favor, dime "Pon la alarma para las cinco y media"',
                     'Puedes decir "Crea una alarma a las tres cuarenta y cinco"']

    elif intent == 'Calendario':
        responses = ['You can say: "Crea una nota para el cinco de marzo"',
                     'You could say: "Pon una nota el quince de abril"']

    elif intent == 'ElTiempo':
        responses = ['You could say: "Cual es el tiempo en Waltham"',
                     'You can ask me: "Que tiempo hace en Boston"']

    elif intent == 'LaHora':
        responses = ['You could ask me: "Que hora es"',
                     'You can say: "Dime la hora"',
                     'You can say: "Dime que hora es"',
                     'You could ask me: "Me dices la hora"']

    elif intent == 'Luces':
        responses = ['You can ask me: "Enciende las luces"',
                     'You could say: "Apaga la luz"']

    elif intent == 'Restaurantes':
        responses = ['You can say: "Muestrame restaurantes en Waltham"',
                     'You can ask: "Enseñame bares chulos en Boston"']

    return random.choice(responses)

def give_corrected_ssml(intent):
    """
    ssml for corrected langauge
    :param intent:
    :return:
    """
    return ""

def get_english_intent_ssml(intent):
    """
    ssml for english intent handling
    :param intent:
    :return:
    """
    return ""

def make_df_dct(response):
    return {"fulfillmentText": response,
            "source": "example.com",
            "payload": {
                "google": {
                    "richResponse": {
                        "items": [
                            {"simpleResponse": {
                                "textToSpeech": response
                            }
                            }
                        ]
                    }
                }
            }
            }

def make_al_dct(response, ssml):
    """
    make dictionary for alexa fulfillment
    :param response:
    :param ssml:
    :return:
    """
    dct = {"version": "1.0",
           "response": {
               "outputSpeech": {
                   "type": "PlainText",
                   "text": response
               },
           }
           }
    return dct

@app.route("/", methods=['POST'])
def manage_request():
    """Main method that determines how to proceed based on the kind of intent detected"""

    response = ""
    ssml = ""
    try:
        req = request.get_json(silent=True, force=True)
        if 'queryResult' not in req.keys():
            reqType= req.get('request').get('type')
            if reqType == 'LaunchRequest':
                response = "Hello, welcome to Fluency Friend! If you ask me to do something in English, I can teach you to say it in Spanish. Ask me in Spanish and I can correct you!"
                ssml = "<speak> Hello, welcome to Fluency Friend! If you ask me to do something in English, I can teach you to say it in Spanish. Ask me in Spanish and I can correct you! </speak>"
            else:
                response = "testing"
                """response = "looking for intent"
                language = get_language(req)
                intent = req.get('request').get('intent').get('name')
                if language.startswith('en'):
                    response = handle_english_intent(intent)
                    ssml = get_english_intent_ssml(intent)
                else:
                    user_utterance = get_al_utterance(req)
                    if gc.is_grammatical(user_utterance):
                        response = handle_intent(intent)
                        ssml = handle_intent_ssml(intent)

                    else:
                        # if ungrammatical, say how they should have said it
                        response = give_corrected_response(intent)
                        ssml = give_corrected_ssml(intent)"""


        else:
            language = get_language(req)
            intent = get_df_intent(req)

            if language.startswith('en'):  # utterance in english
                response = handle_english_intent(intent)

            else:
                user_utterance = get_df_utterance(req)

            # if grammatical, congratulate and proceed with success message

                if gc.is_grammatical(user_utterance):
                    response = handle_intent(intent)

                else:
                # if ungrammatical, say how they should have said it
                    response = give_corrected_response(intent)


    except:  # in case something goes wrong, give a response to let the user know to try again
        response = "No te he entendido. Por favor intentalo de nuevo."
        ssml = "<speak><lang xml:lang='es-ES'>No te he entendido. Por favor intentalo de nuevo</lang></speak>"

    if 'queryResponse' in req.keys():
        dct = make_df_dct(response)
        return make_response(jsonify(dct))

    else:
        dct = make_al_dct(response,ssml)
        return jsonify(dct)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", '8080')))
