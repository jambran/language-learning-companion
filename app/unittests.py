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
