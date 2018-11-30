from CKY_tree import *
from CKY_util import *


class RHS:
    def __init__(self, rhs1, rhs2=None):
        self.rhs1 = rhs1
        if rhs2 is None:
            self.isUnary = True
        else:
            self.isUnary = False
            self.rhs2 = rhs2

    def __str__(self):
        if self.isUnary:
            return self.rhs1
        else:
            return self.rhs1 + " " + self.rhs2

    def __repr__(self):
        return "'" + str(self) + "'"

    def __eq__(self, other):
        if self.isUnary != other.isUnary: return False
        if self.rhs1 != other.rhs1: return False
        if self.isUnary: return True
        if self.rhs2 != other.rhs2: return False
        return True

    def __hash__(self):
        if self.isUnary:
            return hash((True, self.rhs1))
        return hash((False, self.rhs1, self.rhs2))


class Rule:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.isUnary = rhs.isUnary

    def __str__(self):
        return self.lhs + " => " + str(self.rhs)

    def __repr__(self):
        return "'" + str(self) + "'"

    def __eq__(self, other):
        if self.lhs != other.lhs: return False
        return eq(self.rhs, other.rhs)

    def __hash__(self):
        return hash((self.lhs, self.rhs))


class PCFG:
    def __init__(self, pcfgC={}):
        self.pcfgC = pcfgC  # the raw cfg itself, pcfgC[lhs][rhs] = Count(lhs -> rhs)
        self.pcfg = None  # the normalized version of pcfgC, pcfg[lhs][rhs] = p(rhs | lhs)
        self.pcfgR = None  # a "rotated" version of pcfg, pcfgR[rhs1][rhs2][lhs] = p(rhs1 rhs2 | lhs), where rhs2 is None for unary rules

    def __str__(self):
        rules = []
        for lhs in self.pcfgC.keys():
            for rhs, count in self.pcfgC[lhs].items():
                rules.append(str(Rule(lhs, rhs)) + '\t| ' + str(count) + '\n')
        return ''.join(rules)

    def __len__(self):  # number of unique rules
        count = 0
        for lhs in self.pcfgC.keys():
            count += len(self.pcfgC[lhs])
        return count

    def increase_rule_count(self, rule):
        self.pcfg = None
        self.pcfgR = None

        if rule.lhs not in self.pcfgC:
            self.pcfgC[rule.lhs] = Counter()

        self.pcfgC[rule.lhs][rule.rhs] += 1

    def normalize(self):
        self.pcfg = {}
        for lhs in self.pcfgC.keys():
            # first, copy the elements
            self.pcfg[lhs] = Counter()
            for rhs, c in self.pcfgC[lhs].items():
                self.pcfg[lhs][rhs] = c
            # now normalize
            self.pcfg[lhs].normalize()
        # since pcfg has changed, pcfgR should be reset to None
        self.pcfgR = None

    def rotate(self):
        if self.pcfg is None:
            self.normalize()

        self.pcfgR = {}
        for lhs in self.pcfg.keys():
            for rhs, prob in self.pcfg[lhs].items():
                rhs1 = rhs.rhs1
                rhs2 = None
                if not rhs.isUnary:
                    rhs2 = rhs.rhs2

                # we have a rule of the form "lhs -> rhs1 rhs2"
                # so set probability of lhs in [rhs1][rhs2] to prob

                if rhs1 not in self.pcfgR:
                    self.pcfgR[rhs1] = {}

                if rhs2 not in self.pcfgR[rhs1]:
                    self.pcfgR[rhs1][rhs2] = {}

                self.pcfgR[rhs1][rhs2][lhs] = prob

    def iter_binary_rules_on_rhs(self, rhs1, rhs2):
        if self.pcfgR is None:
            self.rotate()

        if rhs1 not in self.pcfgR:
            return

        if rhs2 not in self.pcfgR[rhs1]:
            return

        for lhs, ruleLogProb in self.pcfgR[rhs1][rhs2].items():
            yield (lhs, ruleLogProb)

    def iter_unary_rules_on_rhs(self, rhs):
        for lhs, ruleLogProb in self.iter_binary_rules_on_rhs(rhs, None):
            yield (lhs, ruleLogProb)


# timeFliesSent = "time flies like an arrow".split()

fluencyFriendPCFG = PCFG({
    "TOP": {RHS("S"): 1.0},

    "S": {RHS("NP", "VP"): 1.0,
          RHS("VP"): 1.0,
          RHS("NP", "VP_PP"): 1.0,
          RHS("WH2", "VB-ES"): 1.0,
          RHS("WH1", "NP_VB-ES"): 1.0,
          RHS("WH1", "NP_VB-HACE"): 1.0,
          # RHS("VP", "NP_PP"): 1.0,
          RHS("VP", "PP"): 1.0},

    "NP_VB-ES": {RHS("NP", "VBes"): 1.0},
    "VB-ES": {RHS("VBes", "NP_PP"): 1.0},

    "NP_VB-HACE": {RHS("NP", "VB-HACE"): 1.0},
    "VB-HACE": {RHS("VBhace", "PP"): 1.0},

    # "VP_PP": { RHS("VP", "PP")     : 1.0 },

    "NP": {RHS("CNP"): 1.0,
           RHS("NNP"): 1.0,
           RHS("CNP", "PP"): 1.0,
           RHS("UCNP", "PP"): 1.0,
           RHS("UCNP"): 1.0},

    "CNP": {RHS("DT", "NN"): 1.0,
            RHS("DT", "AP_NN"): 1.0,
            RHS("DT", "NPMonth_PP"): 1.0},

    "AP_NN": {RHS("AP", "NN"): 1.0},
    "NPMonth_PP": {RHS("NPMonth", "PP"): 1.0},

    "UCNP": {RHS("NN"): 1.0},

    "VP": {RHS("VB", "NP"): 1.0,
           RHS("VB", "NP_PP"): 1.0,
           RHS("VB"): 1.0,
           RHS("VB", "S"): 1.0},

    "NP_PP": {RHS("NP", "PP"): 1.0},

    "PP": {RHS("Pin", "NP"): 1.0,
           RHS("Pin", "NNP"): 1.0,
           RHS("Pfor", "NPHour"): 1.0,
           RHS("Pof", "NPYear"): 1.0,
           RHS("Pof", "NPMonth"): 1.0},

    "NPMonth": {RHS("NB1", "PP"): 1.0},
    "NPYear": {RHS("NB1", "Mil_NB1"): 1.0},

    "Mil_NB1": {RHS("Mil", "NB1"): 1.0},

    "NPHour": {RHS("DT", "NB1_NB2"): 1.0,
               RHS("DT", "NB1"): 1.0,
               RHS("DT", "NB1_CC"): 1.0,
               RHS("DT", "NB1_ADVMin"): 1.0},

    "NB1_NB2": {RHS("NB1", "NB2"): 1.0},

    "NB1_CC": {RHS("NB1", "CC_NB1"): 1.0,
               RHS("NB1", "CC_NB2"): 1.0,
               RHS("NB1", "CC_NB3"): 1.0},

    "CC_NB1": {RHS("CC", "NB1"): 1.0},
    "CC_NB2": {RHS("CC", "NB2"): 1.0},
    "CC_NB3": {RHS("CC", "NB3"): 1.0},

    "NB1_ADVMin": {RHS("NB1", "ADVMin_NB1"): 1.0,
                   RHS("NB1", "ADVMin_NB2"): 1.0,
                   RHS("NB1", "ADVMin_NB3"): 1.0, },

    "ADVMin_NB1": {RHS("ADVMin", "NB1"): 1.0},
    "ADVMin_NB2": {RHS("ADVMin", "NB2"): 1.0},
    "ADVMin_NB3": {RHS("ADVMin", "NB3"): 1.0},

    "NB1": {RHS("Num"): 1.0},
    "NB2": {RHS("Num", "CC_Num"): 1.0},
    "NB3": {RHS("Num3"): 1.0},

    "CC_Num": {RHS("CC", "Num"): 1.0},

    # Start of lexicon
    "WH1": {RHS('que'): 1.0},
    "WH2": {RHS('cual'): 1.0},

    # cuanto WH num:sg
    # cuando WH num:sg
    # como
    # quien WH num:sg
    # quienes WH num:pl

    "VB": {RHS('muestrame'): 1.0,
           RHS('enseñame'): 1.0,
           RHS('dime'): 1.0,
           RHS('enciende'): 1.0,
           RHS('apaga'): 1.0,
           RHS('recomiendame'): 1.0,
           RHS('escribe'): 1.0,
           RHS('pon'): 1.0,
           RHS('crea'): 1.0},

    "VBes": {RHS('es'): 1.0},
    "VBhace": {RHS('hace'): 1.0},

    "NN": {RHS('alarma'): 1.0,
           RHS('nota'): 1.0,
           RHS('tiempo'): 1.0,
           RHS('hora'): 1.0,
           RHS('luz'): 1.0,
           RHS('luces'): 1.0,
           RHS('restaurantes'): 1.0},

    "DT": {RHS('las'): 1.0,
           RHS('la'): 1.0,
           RHS('los'): 1.0,
           RHS('el'): 1.0,
           RHS('una'): 1.0},

    "Num": {RHS('uno'): 1.0,
            RHS('una'): 1.0,
            RHS('dos'): 1.0,
            RHS('tres'): 1.0,
            RHS('cuatro'): 1.0,
            RHS('cinco'): 1.0,
            RHS('seis'): 1.0,
            RHS('siete'): 1.0,
            RHS('ocho'): 1.0,
            RHS('nueve'): 1.0,
            RHS('diez'): 1.0,
            RHS('once'): 1.0,
            RHS('doce'): 1.0,
            RHS('trece'): 1.0,
            RHS('catorce'): 1.0,
            RHS('quince'): 1.0,
            RHS('dieciseis'): 1.0,
            RHS('diecisiete'): 1.0,
            RHS('dieciocho'): 1.0,
            RHS('diecinueve'): 1.0,
            RHS('veinte'): 1.0,
            RHS('veintiuno'): 1.0,
            RHS('veintidos'): 1.0,
            RHS('veintitres'): 1.0,
            RHS('veinticuatro'): 1.0,
            RHS('veinticinco'): 1.0,
            RHS('veintiseis'): 1.0,
            RHS('veintisiete'): 1.0,
            RHS('veintiocho'): 1.0,
            RHS('veintinueve'): 1.0,
            RHS('treinta'): 1.0,
            RHS('cuarenta'): 1.0,
            RHS('cincuenta'): 1.0,
            RHS('sesenta'): 1.0},

    "Mil": {RHS('mil'): 1.0},
    "CC": {RHS('y'): 1.0},

    "Num3": {RHS('media'): 1.0,
             RHS('cuarto'): 1.0},

    "Pin": {RHS('en'): 1.0},

    "Pfor": {RHS('para'): 1.0,
             RHS('a'): 1.0},

    "Pof": {RHS('de'): 1.0},

    "ADVMin": {RHS('menos'): 1.0},
    "ADV": {RHS('mas'): 1.0},

    "NMonth": {RHS('enero'): 1.0,
               RHS('febrero'): 1.0,
               RHS('marzo'): 1.0,
               RHS('abril'): 1.0,
               RHS('mayo'): 1.0,
               RHS('junio'): 1.0,
               RHS('julio'): 1.0,
               RHS('agosto'): 1.0,
               RHS('septiembre'): 1.0,
               RHS('octubre'): 1.0,
               RHS('noviembre'): 1.0,
               RHS('diciembre'): 1.0},

    "NNP": {RHS('waltham'): 1.0,
            RHS('boston'): 1.0,
            RHS('cambridge'): 1.0,
            RHS('lexington'): 1.0}
})

