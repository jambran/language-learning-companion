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

# reads CSV file as a dataframe object
houses = pd.read_csv(os.path.join(os.getcwd(), 'app', 'houses.csv'))
fulfillmentText = 'fulfillmentText'
# column headers to access the dataframe
display_columns = ['PRICE', 'BEDS', 'BATHS', 'LOCATION']
# set to store the filters
filters = {}


def get_intent():
    """Returns the intent name as defined in the DialogFlow app"""
    req = request.get_json(silent=True, force=True)
    print((req), file=sys.stdout)
    return req.get('queryResult').get('intent').get('displayName')


def get_filtered_df():
    """Returns a dataframe that displays only the elements selected by the filters that the user requested"""
    tmp = houses
    print("FILTERS: " + str(filters), file=sys.stdout)
    for column in filters:
        if column == 'FILTER':
            continue
        if column == 'PRICE':
            print(column, file=sys.stdout)
            print(filters[column], file=sys.stdout)
            max = filters[column]['Max']
            min = filters[column]['Min']
            try:
                tmp = tmp[tmp[column] < max]
                tmp = tmp[tmp[column] > min]
            except TypeError as e:
                print(e, file=sys.stdout)
            continue
        else:
            print(column, file=sys.stdout)
            print(filters[column], file=sys.stdout)
            try:
                tmp = tmp[tmp[column] == filters[column]]
            except TypeError as e:
                print(e, file=sys.stdout)
    return tmp


def filter_apartments():
    """Returns the first 5 (or less) entries in the database that meet the filtering criteria"""
    df = get_filtered_df()
    return df[display_columns].head()


def make_entity_match_column(entity):
    """
    trim off any integers at end, then make uppercase
    :param entity: the entity type from DialogFlow
    :return: the corresponding column in houses
    """
    while entity[-1].isdigit():
        entity = entity[:-2]
    return entity.upper()


def refine_filter():
    """Identifies the filters requested by the user and stores them in the "filters" global variable set"""

    global filters
    req = request.get_json(silent=True, force=True)
    parameters = req.get('queryResult').get('parameters')

    for entity in parameters:
        # if the entity value is empty, the user didnt request to filter by that, so ignore it
        if parameters[entity] == '' or entity == 'Filter':
            continue

        column = make_entity_match_column(entity)
        # if the value of the 'entity' key is "1 bedroom" we want to add just the integer as the value to search
        # for in the column of the df
        split_param = parameters[entity].split()
        quantity = split_param[0]

        print('entity:', entity, file=sys.stdout)
        print('parameters ent value:', parameters[entity], file=sys.stdout)
        print('split:', split_param, file=sys.stdout)
        print('split at 0:', quantity, file=sys.stdout)

        # if the entity is beds or bath, we want to make its value a float to check it correctly in the dataframe
        if entity == 'Beds' or entity == 'Baths':
            filters[column] = float(quantity)

        # distinguish between Max and Min values of price (and turn them into float too)
        elif entity == 'Max' or entity == 'Min':  # handling prices here
            if 'PRICE' not in filters.keys():
                # we need to initialize the dictionary in case they only gave one of min and max
                filters['PRICE'] = {'Max': 20000000,
                                    'Min': 0}
            if entity == 'Max':
                filters['PRICE']['Max'] = float(parameters['Max'])
            else:
                filters['PRICE']['Min'] = float(parameters['Min'])

        # the rest of the possible values are strings
        else:
            filters[column] = split_param[0]
            print('IN THE ELSE STATEMENT')


def show_filter_options():
    """Prints directions to help the user enter the right keywords for filtering"""

    req = request.get_json(silent=True, force=True)
    parameters = req.get('queryResult').get('parameters')

    if 'Filter' in parameters:
        filt = parameters['Filter']
        if filt == 'City':
            return "Your options are: Arlington, Cambridge, Lexington, Waltham, Winchester, or Belmont."
        elif filt == 'Baths':
            return "Please enter the minimum number of bathrooms you want (e.g '1.5 bathrooms')."
        elif filt == 'Beds':
            return "Please enter the minimum number of beds you want (e.g. '2 bedrooms')."
        elif filt == 'Location':
            return "Please enter a neighborhood within Arlington, Cambridge, Lexington, Waltham, Winchester, or Belmont."
        elif filt == 'Price':
            return "Please enter the maximum amount you want to spend."


def print_specs(row):
    """Formats the df output"""
    ret = ""
    for col in houses.columns:
        if len(col) > 15:
            col = col[:15]
        ret += "\n%15s\t" % (col)
        ret += row[col]
    return ret


def get_specs():
    global filters

    req = request.get_json(silent=True, force=True)
    parameters = req.get('queryResult').get('parameters')

    # check to see if the user gave information about the index of the listing
    try:
        index = parameters['sys.number']
        row = houses.loc[[index]]  # the row in that dataframe
        return print_specs(row)
    except KeyError:  # we couldn't determine which house, so send info about all
        ret = ""
        for i, row in houses.iterrows():
            ret += "\n\n house number %d" % i
            ret += print_specs(row)
        return ret


@app.route("/", methods=['POST'])
def manage_request():
    """Main method that determines how to proceed based on the kind of intent detected"""

    global filters

    try:
        # retrieve the intent
        intent = get_intent()
        print(filters, file=sys.stdout)

        if intent == 'Show Listings':
            response = "I found {} apartments in the area.\nHow would you like to filter them?".format(len(houses))
            response += "\nYou can filter by " + ', '.join(['city', 'price', 'beds', 'baths', 'location'])

        # provides the user with some directions for how to enter correct filters
        elif intent == 'Filter Options':
            response = show_filter_options()

        elif intent == 'Filter Listings':
            refine_filter()
            if (len(filter_apartments()) == 0):
                response = "No houses match those filters.\n%s\nI've reset your filters. Please try again." \
                           % (str(filters))
                filters = {}
            else:
                response = "Here are the top apartments with the specifications: {}".format(str(filters))
                response += "\n{}".format(filter_apartments())

        elif intent == 'Empty Filters':
            filters = {}
            response = "Your previous filters were deleted."

        elif intent == 'Info Request':  # for emails, if they ever get implemented.
            response = "Here are the specifications:\n"
            response += get_specs()
            response += "I'll send those to your email now"

        elif intent == 'Display filters':
            response = "These are your filters so far:\n"
            response += str(filters)

    except:  # in case something goes wrong, give a response to let the user know to try again
        response = "Hmm. Something went wrong. What would you like to do?"

    return make_response(jsonify({fulfillmentText: response}))


def top_apartments(num_apartments=10):
    return houses.head(num_apartments)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", '8080')))
