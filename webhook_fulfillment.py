"""
Jamie Brandon
David Rubio Vallejo
Micaela Kaplan
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
    return req.get('request').get('intent').get('name')

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
        response += str(datetime.datetime.time(datetime.datetime.now()))[:5]

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
    ssml = ""
    if intent == 'Alarmas':
        ssml += "<speak> <lang xml:lang='es-ES'>Muy bien!</lang> The alarm is set now!</speak>"

    elif intent == 'Calendario':
        ssml += "<speak> <lang xml:lang='es-ES'>Muy bien!</lang> The event is in your calendar!</speak>"

    elif intent == 'ElTiempo':
        ssml += "<speak> <lang xml:lang='es-ES'>Muy bien! Espero que hace sol, pero la verdad es que no se</lang></speak>"

    elif intent == 'LaHora':
        ssml += "Ahora son las:\n"
        ssml += str(datetime.datetime.time(datetime.datetime.now()))[:5]


    elif intent == 'LucesOn' or intent == 'LucesOff':
        ssml += "<speak?<lang xml:lang='es-ES'>Perfecto!</lang> The lights are set now.</speak>8"

    elif intent == 'Restaurantes':
        ssml += "<speak><lang xml:lang='es-ES'>Tu español es perfecto!</lang> I sent you some restaurants to your email account.</speak>"

    return response


def get_language(req):
    return detect(get_df_utterance(req))


def handle_english_intent(intent):
    if intent == 'Alarmas' or intent == 'Alarm':
        responses = ['Por favor, dime "Pon la alarma para las cinco y media"',
                     'Puedes decir "Crea una alarma a las tres cuarenta y cinco"']

    elif intent == 'Calendario' or intent == 'Calendar':
        responses = ['You can say: "Crea una nota para el cinco de marzo"',
                     'You could say: "Pon una nota el quince de abril"']

    elif intent == 'ElTiempo' or intent == 'Weather':
        responses = ['You could say: "Cual es el tiempo en Waltham"',
                     'You can ask me: "Que tiempo hace en Boston"']

    elif intent == 'LaHora' or intent == 'Time':
        responses = ['You could ask me: "Que hora es"',
                     'You can say: "Dime la hora"',
                     'You can say: "Dime que hora es"',
                     'You could ask me: "Me dices la hora"']

    elif intent == 'Luces' or intent == 'Lights':
        responses = ['You can ask me: "Enciende las luces"',
                     'You could say: "Apaga la luz"']

    elif intent == 'Restaurantes' or intent == 'Restaurant':
        responses = ['You can say: "Muestrame restaurantes en Waltham"',
                     'You can ask: "Enseñame bares chulos en Boston"']

    return random.choice(responses)

def give_corrected_ssml(intent):
    """
    ssml for corrected langauge
    :param intent:
    :return:
    """
    if intent == 'AlarmasIncorrect':
        # GET SLOT INFO FOR TIME
        time = req.get('request').get('intent').get('slots').get('timeslot').get('value')
        ssml = "<speak> Almost! try: <lang xml:lang ='es-ES'>Pon la almarma para <say-as interpret-as = 'cardinal'>"+time+"</say-as></lang></speak>"
    elif intent == 'CalendariIncorrect':
        # GET SLOT INFO FOR DATE
        date = req.get('request').get('intent').get('slots').get('dateslot').get('value')
        ssml = "<speak> You were close!: <lang xml:lang = 'es-ES'>Crea una nota para <say-as interpret-as = 'date' format = 'md'>"+date+"</say-as></lang></speak"
    elif intent == 'EltiempoIncorrect':
        #GET SLOT INFO FOR CITY
        city = req.get('request').get('intent').get('slots').get('city').get('value')
        ssml = "<speak> That was close!: <lang xml:lang = 'es-ES'>Cual es el tiempo en "+ city +"</lang></speak>"
    elif intent == 'LahoraIncorrect':
        ssml = "<speak> Good try! The proper way to ask is: <lang xml:lang = 'es-ES'> Que hora es </lang> </speak>"
    elif intent == 'LucesOnIncorrect':
        ssml = "<speak> Very close! Try: <lang xml:lang = 'es-ES'>Enciende las luces </lang></speak>"
    elif intent == 'LucesOffIncorect':
        ssml = "<speak> Almost! Instead, say: <lang xml:lang = 'es-ES'>Apaga la luz</lang></speak>"
    elif intent == 'RestaurantesIncorrect':
        #GET SLOT INFO FOR CITY
        city = req.get('request').get('intent').get('slots').get('cityslot').get('value')
        ssml = "<speak> Good try! Instead, say: <lang xml:lang = 'es-ES'>Muestrame restaurantes en" + city + "</lang></speak>"

    return ssml
def get_english_intent_ssml(intent, req):
    """
    ssml for english intent handling
    :param intent:
    :return:
    """
    if intent == 'Alarm':
        # GET SLOT INFO FOR TIME
        time = req.get('request').get('intent').get('slots').get('timeslot').get('value')
        ssml = "<speak> You can say: <lang xml:lang ='es-ES'>Pon la almarma para <say-as interpret-as = 'cardinal'>"+time+"</say-as></lang></speak>"
    elif intent == 'Calendar':
        # GET SLOT INFO FOR DATE
        date = req.get('request').get('intent').get('slots').get('dateslot').get('value')
        ssml = "<speak> You could say: <lang xml:lang = 'es-ES'>Crea una nota para <say-as interpret-as = 'date' format = 'md'>"+date+"</say-as></lang></speak"
    elif intent == 'Weather':
        #GET SLOT INFO FOR CITY
        city =  req.get('request').get('intent').get('slots').get('city').get('value')
        ssml = "<speak> You can ask me: <lang xml:lang = 'es-ES'>Cual es el tiempo en "+ city +"</lang></speak>"
    elif intent == 'Time':
        ssml = "<speak> Ask me: <lang xml:lang = 'es-ES'> Que hora es </lang> </speak>"
    elif intent == 'Lights-on':
        ssml = "<speak> You can say: <lang xml:lang = 'es-ES'>Enciende las luces </lang></speak>"
    elif intent == 'Lights-off':
        ssml = "<speak> Try saying: <lang xml:lang = 'es-ES'>Apaga la luz</lang></speak>"
    elif intent == 'Restaurant':
        #GET SLOT INFO FOR CITY
        city = req.get('request').get('intent').get('slots').get('cityslot').get('value')
        ssml = "<speak> You could ask: <lang xml:lang = 'es-ES'>Muestrame restaurantes en" + city + "</lang></speak>"

    return ssml

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

def make_al_dct(ssml):
    """
    make dictionary for alexa fulfillment
    :param response:
    :param ssml:
    :return:
    """
    dct = {"version": "1.0",
           "response": {
               "outputSpeech": {
                   "type": "SSML",
                   "SSML": ssml
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
                ssml = "<speak> <lang xml:lang = 'es-ES'> Hola </lang>, welcome to Fluency Friend! If you ask me to do something in English, I can teach you to say it in Spanish. Ask me in Spanish and I can correct you! </speak>"

            else:
                response = "looking for intent"
                SpanishCorrect = ['Calendario','Eltiempo', 'Lahora', 'Restaurantes', 'LucesOn','LucesOff', 'Alarmas' ]
                SpanishIncorrect = ['CalendariIncorrect', 'EltiempoIncorrect', 'LahoraIncorrect', 'RestaurantesIncorrect', 'AlarmasIncorrect', 'LucesOnIncorrect', 'LucesOffIncorrect']
                intent = get_al_utterance(req)
                if intent not in (SpanishCorrect or SpanishIncorrect):
                    ssml = get_english_intent_ssml(intent, req)
                else:
                    if intent in SpanishCorrect:
                        ssml = handle_intent_ssml(intent)

                    else:
                        # if ungrammatical, say how they should have said it
                        ssml = give_corrected_ssml(intent)

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
        dct = make_al_dct(ssml)
        return jsonify(dct)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", '8080')))
