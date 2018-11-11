from collections import defaultdict
from Lexeme import Lexeme
import os

def load_lexicon(filename):
    lexicon = defaultdict(lambda: [])  # maps POS to the Lexemes
    vocab = []  # holds all lexemes
    with open(filename) as f:
        for line in f:
            if line.startswith('#') or line == "\n":  # ignore comment lines or empty lines in files
                continue
            line = line.split()
            word = line[0]
            POS = line[1]
            features = line[2:]
            feature_dictionary = defaultdict(lambda: [])
            for feature in features:
                feat = feature.split(':')
                feat_type = feat[0]
                feat_val = feat[1]
                # build the feature dictionary
                feature_dictionary[feat_type].append(feat_val)
            lexeme = Lexeme(word=word,
                            POS=POS,
                            features=feature_dictionary
                            )
            vocab.append(lexeme)
            lexicon[POS].append(lexeme)
    return lexicon, vocab


def load_grammar(filename):
    grammar = defaultdict(list)
    with open(filename) as f:

        for line in f:
            if line.startswith('#') or line == "\n":  # ignore comment lines or empty lines in files
                continue
            line = line.split()
            lhs = line[0].split("-")
            nonterminal = lhs[0]
            lhs_features = lhs[1:]
            productions = [production.split("-") for production in line[2:]]
            grammar[nonterminal].append((productions,lhs_features))
    return grammar


class GrammarChecker():

    def __init__(self):
        # lexicon maps POS to list of Lexemes with that POS, vocab is list of all lexemes
        self.lexicon, self.vocab = load_lexicon(filename=os.path.join('language_rules', 'lexicon.txt'))
        self.grammar = load_grammar(filename=os.path.join('language_rules', 'grammar.txt'))# dict of POS to rewrite rule
        # self.vocab = [word[0] for word in self.lexicon[symbol]]

    def get_parse(self, sentence):
        sentence = sentence.split()
        result = self.recursive_parse(sentence, "TOP", 0, debug=False)
        return result[0]

    def is_grammatical(self, sentence, debug=False):
        sentence = sentence.split()
        result = self.recursive_parse(sentence, "TOP", 0, debug=debug)
        if type(result) == str:
            return False
        if result[1] == len(sentence):
            return True
        # we didn't complete a rule - stopped early
        return False

    def recursive_parse(self, sentence, symbol, index, debug=False, tabs=""):
        if debug: print(tabs, symbol, index)

        # base case: we have a terminal node, e.g. NNP > Elaine
        if symbol in self.lexicon:  # if this is a POS, terminal node, no rewrite rule
            if index >= len(sentence):
                return "YIKES: parse index is longer than sentence"
            possible_words = set( [lexeme.word for lexeme in self.lexicon[symbol]] )
            word = sentence[index]
            if word in possible_words:
                return ([symbol], index + 1)
            else:
                return "YIKES: Word is not in lexicon: %s" % word

        ## recursive case: we have a rewrite rule
        tree = [symbol]
        productions = self.grammar[symbol]
        productions = [production[0] for production in productions]
        for rule in productions:
            tempindex = index
            tempchildren = []
            failure = False
            for element in rule:
                return_value = self.recursive_parse(sentence, element[0], tempindex, debug=debug, tabs=tabs+'\t')
                if type(return_value) == str: # "YIKES" occured
                    failure = True
                    break
                else:
                    subtree, tempindex = return_value
                    tempchildren.append(subtree)

            # if symbol == 'CNP':
            #     x='hello'
            if not failure:
                if symbol == 'TOP' and tempindex == len(sentence): # we've finished parsing the whole sentence!
                    tree.extend(tempchildren)
                    return (tree, tempindex)
                if  symbol == 'TOP':
                    # "YIKES: we ended parsing too soon"
                    continue  # try another rule

                tree.extend(tempchildren)
                return (tree, tempindex)

         # we tried all the rules, and none of them worked. No good
        return "YIKES: no production rule satisfied"


if __name__ == '__main__':
    # sentence = "que hora es"
    gc = GrammarChecker()
    # print(gc.is_grammatical(sentence))

    print(gc.recursive_parse("pon una alarma a las tres cincuenta y dos".split(), "TOP", 0, debug=True))

