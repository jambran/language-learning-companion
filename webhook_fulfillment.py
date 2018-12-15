"""
Jamie Brandon
David Rubio Vallejo
Micaela Kaplan
11/09/2018
"""

# ! /usr/bin/env python3
import json
import os
import sys
import random
import datetime
from flask import Flask, request, jsonify, make_response
from langdetect import detect

from CKY_parser import parse
from CKY_grammar import fluencyFriendPCFG as PCFG

app = Flask(__name__)


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
        weather_list = ["Parece que va a hacer buen tiempo",
                        "¡Hace sol!",
                        "Esta despejado",
                        "Hace un poco de frio"]
        response += random.choice(weather_list)

    elif intent == 'LaHora':
        response += "Ahora son las:\n"
        response += str(datetime.datetime.time(datetime.datetime.now()))[:5]

    elif intent == 'Luces':
        response += "¡Perfecto! The lights are set now."

    elif intent == 'Restaurantes':
        response += "¡Tu español es perfecto! I sent you some restaurants to your email account."

    return response


def df_get_city(req):
    return req.get('queryResult').get('parameters').get('City')


def give_corrected_response(intent, req):
    response = ""
    if intent == 'Alarmas':
        spanish_time = get_spanish_time_in_words(req)
        response = "That was almost correct!\n"
        response += "A better way would be: 'Pon la alarma a %s'.\n" % spanish_time
        response += "Or: 'Crea una alarma a %s'.\n" % spanish_time
        response += "Please try again! :)"

    elif intent == 'Calendario':
        # todo slot fill
        date = 'el cinco de marzo'
        response = "That was almost correct!\n"
        response += "A better way would be: 'Pon una nota para %s'.\n" % date
        response += "Please try again! :)"

    elif intent == 'ElTiempo':
        city = df_get_city()
        response = "That was almost correct!\n"
        response += "A better way would be: 'Dime que tiempo hace en %s'\n" % city
        response += "Or: 'Cual es el tiempo en %s'.\n" % city
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
        city = df_get_city(req)
        response = "That was almost correct!\n"
        response += "A better way would be: 'Muestrame restaurantes en %s'\n" % city
        response += "Please try again! :)"

    return response


def handle_intent_ssml(intent):
    """
    SSML for spanish intent
    :param intent:
    :return:
    """
    print("handling intent")
    ssml = ""
    if intent == 'Alarmas':
        ssml += "<speak> <lang xml:lang='es-ES'>Muy bien!</lang> The alarm is set now!</speak>"

    elif intent == 'Calendario':
        ssml += "<speak> <lang xml:lang='es-ES'>Muy bien!</lang> The event is in your calendar!</speak>"

    elif intent == 'Eltiempo':
        ssml += "<speak> <lang xml:lang='es-ES'>Muy bien! Espero que hace sol, "
        ssml +=  "pero la verdad es que no se</lang></speak>"

    elif intent == 'Lahora':
        print ("in la hora")
        ssml += "<speak><lang xml:lang='es-ES'>Ahora son las: <say-as interpret-as = 'time'> "
        ssml += str(datetime.datetime.time(datetime.datetime.now()))[:5] +"</say-as></lang></speak>"

    elif intent == 'LucesOn' or intent == 'LucesOff':
        ssml += "<speak><lang xml:lang='es-ES'>Perfecto!</lang> The lights are set now.</speak>"

    elif intent == 'Restaurantes':
        ssml += "<speak><lang xml:lang='es-ES'>Tu español es perfecto!</lang> I sent you some restaurants to your email account.</speak>"

    return ssml


def get_language(req):
    return detect(get_df_utterance(req))


def df_get_time(req):
    '''
    :param req: the request from DialogueFlow
    :return: string,  6am is "2018-12-14T06:00:00-05:00"
    '''
    time_string = req.get('queryResult').get('parameters').get('time')
    return time_string


def translate_timestring_to_spanish(time_string):
    """

    :param time_string: string, 6am is "2018-12-14T06:00:00-05:00"
    :return: string, the spanish words for this time
    """
    # note that these are strings, not ints!
    date = time_string[0:11]
    hour = time_string[11:13]
    minute = time_string[14:16]
    with open('time_dict') as f:
        time_dict = json.load(f)
    if hour == '01':
        aritcle = 'la '
    else:
        article = 'las '
    if minute == '00':
        return article + time_dict[hour]
    elif minute == '15':
        return article + time_dict[hour] + ' y cuarto'
    elif minute == '30':
        return article + time_dict[hour] + 'y media'
    elif minute == '45':
        h = int(hour) + 1
        if h < 10:
            h = '0' + str(h)
        else:
            h = str(h)
        return article + time_dict[h] + ' menos cuarto'
    else:
        # get the right gender for the minutes
        if minute == '01':
            minute == '01m'
        return article + time_dict[hour] + ' ' + time_dict[minute]


def get_spanish_time_in_words(req):
    return translate_timestring_to_spanish(df_get_time(req))


def handle_english_intent(intent, req):
    responses = []
    if intent == 'Alarmas' or intent == 'Alarm':
        spanish_time = get_spanish_time_in_words(req)
        responses = ['Por favor, dime "Pon la alarma para ' + spanish_time + '"',
                     'Puedes decir "Crea una alarma a ' + spanish_time + '"']

    elif intent == 'Calendario' or intent == 'Calendar':
        # todo slot fill
        responses = ['You can say: "Crea una nota para el cinco de marzo"',
                     'You could say: "Pon una nota el quince de abril"']

    elif intent == 'ElTiempo' or intent == 'Weather':
        city = df_get_city(req)
        if intent == 'ElTiempo':
            responses = ['You could say: "Cual es el tiempo en &s"' % city]
        else:
            responses = ['You can ask me: "Que tiempo hace en %s"' % city]

    elif intent == 'LaHora' or intent == 'Time':
        responses = ['You could ask me: "Que hora es"',
                     'You can say: "Dime la hora"',
                     'You can say: "Dime que hora es"',
                     'You could ask me: "Me dices la hora"']

    elif intent == 'Luces' or intent == 'Lights':
        responses = ['You can ask me: "Enciende las luces"',
                     'You could say: "Apaga la luz"']

    elif intent == 'Restaurantes' or intent == 'Restaurant':
        city = df_get_city(req)
        responses = ['You can say: "Muestrame restaurantes en %s"' % city,
                     'You can ask: "Enseñame bares chulos en %s"' % city]

    return random.choice(responses)


def give_corrected_ssml(intent, req):
    """
    ssml for corrected langauge
    :param intent:
    :param req:
    :return:
    """
    print("in corrected ssml")
    ssml = ""
    if intent == 'AlarmasIncorrect':
        # GET SLOT INFO FOR TIME
        print("in AlarmasIncorrect")
        time = req.get('request').get('intent').get('slots').get('timeslot').get('value')
        ssml += "<speak> Almost! try: <lang xml:lang ='es-ES'>Pon la alarma para <say-as interpret-as = 'time'>" + time +"</say-as></lang></speak>"
    elif intent == 'CalendariIncorrect':
        print("in CalendariIncorrect")
        # GET SLOT INFO FOR DATE
        date = req.get('request').get('intent').get('slots').get('date').get('value')
        ssml += "<speak> You were close! try: <lang xml:lang = 'es-ES'>Crea una nota para " + date+"</lang></speak>"
        print("ssml set as" + ssml)
    elif intent == 'EltiempoIncorrect':
        print("in EltiempoIncorrect")
        # GET SLOT INFO FOR CITY
        city = req.get('request').get('intent').get('slots').get('city').get('value')
        ssml += "<speak> That was close!: <lang xml:lang = 'es-ES'>Cual es el tiempo en " + city + "</lang></speak>"
    elif intent == 'LahoraIncorrect':
        print("in LahoraIncorrect")
        ssml += "<speak> Good try! The proper way to ask is: <lang xml:lang = 'es-ES'> Que hora es </lang> </speak>"
    elif intent == 'LucesOnIncorrect':
        print("in LucesOnIncorrect")
        ssml += "<speak> Very close! Try: <lang xml:lang = 'es-ES'>Enciende las luces </lang></speak>"
    elif intent == 'LucesOffIncorect':
        print("in luces off incorrect")
        ssml += "<speak> Almost! Instead, say: <lang xml:lang = 'es-ES'>Apaga la luz</lang></speak>"
    elif intent == 'RestaurantesIncorrect':
        print("in restaurantes incorrect")
        # GET SLOT INFO FOR CITY
        city = req.get('request').get('intent').get('slots').get('city').get('value')
        ssml += "<speak> Good try! Instead, say: <lang xml:lang = 'es-ES'>Muestrame restaurantes en " + city + "</lang></speak>"

    print ("returning: " + ssml)
    return ssml


def get_english_intent_ssml(intent, req):
    """
    ssml for english intent handling
    :param intent:
    :return:
    """
    print("in English Intent")
    ssml = ""
    if intent == 'Alarm':
        # GET SLOT INFO FOR TIME
        time = req.get('request').get('intent').get('slots').get('timeslot').get('value')
        ssml += "<speak> You can say: <lang xml:lang ='es-ES'>Pon la alarma para <say-as interpret-as = 'time'>"+time+"</say-as></lang></speak>"
    elif intent == 'Calendar':
        print("in calendar")
        # GET SLOT INFO FOR DATE
        time = req.get('request').get('intent').get('slots').get('date').get('value')
        ssml += "<speak> You can say: <lang xml:lang ='es-ES'>Pon una nota <say-as interpret-as = 'date'>"+time+"</say-as></lang></speak>"
    elif intent == 'Weather':
        # GET SLOT INFO FOR CITY
        city = req.get('request').get('intent').get('slots').get('city').get('value')
        ssml += "<speak> You can ask me: <lang xml:lang = 'es-ES'>Cual es el tiempo en " + city + "</lang></speak>"
    elif intent == 'Time':
        ssml += "<speak> Ask me: <lang xml:lang = 'es-ES'> Que hora es </lang> </speak>"
    elif intent == 'Lights-on':
        ssml += "<speak> You can say: <lang xml:lang = 'es-ES'>Enciende las luces </lang></speak>"
    elif intent == 'Lights-off':
        ssml += "<speak> Try saying: <lang xml:lang = 'es-ES'>Apaga la luz</lang></speak>"
    elif intent == 'Restaurant':
        # GET SLOT INFO FOR CITY
        city = req.get('request').get('intent').get('slots').get('cityslot').get('value')
        ssml += "<speak> You could ask: <lang xml:lang = 'es-ES'>Muestrame restaurantes en " + city + "</lang></speak>"

    print("returning"+ ssml)
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
    :param ssml:
    :return:
    """
    dct = {"version": "1.0",
           "response": {
               "outputSpeech": {
                   "type": "SSML",
                   "ssml": ssml
               },
           }
           }
    return dct


def request_is_from_alexa(req):
    return 'queryResult' not in req.keys()


@app.route("/", methods=['POST'])
def manage_request():
    """Main method that determines how to proceed based on the kind of intent detected"""

    ssml = ""
    try:
        req = request.get_json(silent=True, force=True)
        #print(req, file=sys.stdout)

        if request_is_from_alexa(req):
            reqType = req.get('request').get('type')
            if reqType == 'LaunchRequest':
                response = "Hello, welcome to Fluency Friend! If you ask me to do something in English, " \
                           "I can teach you to say it in Spanish. Ask me in Spanish and I can correct you!"
                ssml = "<speak> <lang xml:lang = 'es-ES'> Hola </lang>, welcome to Fluency Friend! " \
                       "If you ask me to do something in English, I can teach you to say it in Spanish. " \
                       "Ask me in Spanish and I can correct you! </speak>"

            else:
                response = "looking for intent"
                English = ['Calendar', 'Weather', 'Time', 'Restaurant', 'LightsOn', 'LightsOff', 'Alarm']
                SpanishCorrect = ['Calendario', 'Eltiempo', 'Lahora', 'Restaurantes', 'LucesOn', 'LucesOff', 'Alarmas']
                """SpanishIncorrect = ['CalendariIncorrect', 'EltiempoIncorrect', 'LahoraIncorrect', 'RestaurantesIncorrect',
                                    'AlarmasIncorrect', 'LucesOnIncorrect', 'LucesOffIncorrect']"""

                intent = get_al_utterance(req)
                print(intent)
                if intent in English:
                    ssml = get_english_intent_ssml(intent, req)

                else:
                    print("in else")
                    if intent in SpanishCorrect:
                        print("in spanish correct")
                        ssml = handle_intent_ssml(intent)

                    else:
                        ssml = give_corrected_ssml(intent, req)
                        print("ssml is:" + ssml)


        else:  # request from google assistant
            language = get_language(req)
            intent = get_df_intent(req)

            if language.startswith('en'):  # utterance in english
                response = handle_english_intent(intent, req)

            else:
                user_utterance = get_df_utterance(req)

                # if grammatical, congratulate and proceed with success message
                if parse(PCFG, user_utterance.split()) is not None:
                    response = handle_intent(intent)

                else:
                    # if ungrammatical, say how they should have said it
                    response = give_corrected_response(intent, req)

    except:  # in case something goes wrong, give a response to let the user know to try again
        response = "No te he entendido. Por favor intentalo de nuevo."
        ssml = "<speak><lang xml:lang='es-ES'>No te he entendido. Por favor intentalo de nuevo</lang></speak>"

    if request_is_from_alexa(req):
        dct = make_al_dct(ssml)
        return jsonify(dct)

    else:
        dct = make_df_dct(response)
        return make_response(jsonify(dct))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", '8080')))
