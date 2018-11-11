"""
Jamie Brandon
David Rubio Vallejo
ASR PA5
11/09/2018
"""

# ! /usr/bin/env python3
import os
import sys
from flask import Flask, request, jsonify, make_response
import pandas as pd

app = Flask(__name__)

fulfillmentText = 'final_response'

def get_intent():
    """Returns the intent name as defined in the DialogFlow app"""
    req = request.get_json(silent=True, force=True)
    print((req), file=sys.stdout)
    return req.get('queryResult').get('intent').get('displayName')



@app.route("/", methods=['POST'])
def manage_request():
    """Main method that determines how to proceed based on the kind of intent detected"""

    response = "You're in llc.py!"
    # try:
    #     # retrieve the intent
    #     intent = get_intent()
    #
    #
    # except:  # in case something goes wrong, give a response to let the user know to try again
    #     response = "Hmm. Something went wrong. What would you like to do?"

    return make_response(jsonify({fulfillmentText: response}))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", '8080')))
