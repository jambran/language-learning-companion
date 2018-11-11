

class Lexeme():
    def __init__(self, word, POS, features=None):
        self.word = word
        self.POS = POS
        self.features = features  # dict mapping feature name to list of possible values

    def __str__(self):
        return "%s\n\t%s\n\t%s" % (self.word, self.POS, str(self.features))
