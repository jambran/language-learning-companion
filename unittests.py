import unittest
from GrammarChecker import GrammarChecker
import os


class GrammarCheckerTest(unittest.TestCase):

    def test_grammatical(self):
        print("TESTING GRAMMATICAL")
        gc = GrammarChecker()
        grammatical_file = os.path.join("test_parse_sents", "good_sentences.txt")
        with open(grammatical_file) as f:
            for line in f:
                if line.startswith('#'):
                    continue
                line = line.strip()
                truth_val = gc.is_grammatical(line)
                print(line + ': ' + str(truth_val))
                self.assertTrue(gc.is_grammatical(line))

    def test_1(self):
        gc = GrammarChecker()
        self.assertTrue(gc.is_grammatical("pon la alarma para las dos"))

    def test_2(self):
        gc = GrammarChecker()
        self.assertTrue(gc.is_grammatical("pon una alarma a las tres cincuenta y dos"))

    # def test_3(self):
    #     gc = GrammarChecker()
    #     self.assertTrue(gc.is_grammatical("crea una nota"))

    def test_4(self):
        gc = GrammarChecker()
        self.assertTrue(gc.is_grammatical("crea una nota para el cinco de marzo de dos mil diecinueve"))

    def test_ungrammatical(self):
        print("TESTING UNGRAMMATICAL")
        gc = GrammarChecker()
        ungrammatical_file = os.path.join("test_parse_sents", "bad_sentences.txt")
        with open(ungrammatical_file) as f:
            for line in f:
                if line.startswith('#'):
                    continue
                line = line.strip()
                truth_val = gc.is_grammatical(line)
                print(line + ': '+ str(truth_val))
                self.assertFalse(truth_val)

if __name__ == '__main__':
    gc = GrammarChecker()
    unittest.main()
