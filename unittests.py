import unittest
from GrammarChecker import GrammarChecker

class GrammarCheckerTest(unittest.TestCase):

    def test_grammatical(self):
        print("TESTING GRAMMATICAL")
        gc = GrammarChecker()
        grammatical_file = "good_sentences.txt"
        with open(grammatical_file) as f:
            for line in f:
                print(line)
                self.assertTrue(gc.is_grammatical(line))

    def test_ungrammatical(self):
        print("TESTING UNGRAMMATICAL")
        gc = GrammarChecker()
        ungrammatical_file = "bad_sentences.txt"
        with open(ungrammatical_file) as f:
            for line in f:
                print(line)
                self.assertFalse(gc.is_grammatical(line))

if __name__ == '__main__':
    gc = GrammarChecker()
    unittest.main()
