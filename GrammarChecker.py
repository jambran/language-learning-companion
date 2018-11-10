from collections import defaultdict

def load_lexicon(filename="lexicon.txt"):
    f = open(filename)
    lexicon = defaultdict(list)
    for line in f:
        [word, POS] = line.split()[:2]
        features = line.split()[2:]
        features = [feature.split(":") for feature in features]
        lexicon[POS].append((word,features))
    f.close()
    return lexicon


def load_templates(filename="templates.txt"):
    f = open(filename)
    templates=[]
    for line in f:
        templates.append(line.split())
    f.close()
    return templates

class GrammarChecker():

    def __init__(self):
        self.lexicon = load_lexicon(filename='lexicon.txt')
        self.templates = load_templates()
