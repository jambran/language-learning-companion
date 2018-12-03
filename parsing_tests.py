import unittest
from CKY_parser import *
from CKY_grammar import *


def check_wellformed(split_sent):
    """Returns True if the sentence is grammatical, False otherwise"""
    return parse(fluencyFriendPCFG, split_sent) is not None


class TestParsing(unittest.TestCase):

    def test_good_sents(self):
        """Tests whether well-formed sentences are accepted by our grammar"""

        good_list = ["pon una alarma a las tres y cincuenta y ocho".split(),
                     "que hora es".split(),
                     "dime la hora".split(),
                     "cual es la hora".split(),
                     "que tiempo hace en Boston".split(),
                     "enciende la luz".split(),
                     "enciende las luces".split(),
                     "apaga la luz".split(),
                     "apaga las luces".split(),
                     "muestrame restaurantes en Waltham".split(),
                     "crea un evento el veintitres de enero".split()]

        for good_sent in good_list:
            # print(good_sent)
            self.assertTrue( check_wellformed(good_sent) )



if __name__ == '__main__':
    unittest.main()