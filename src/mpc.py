import sys
import logging
import argparse
sys.path.append('./src/')

import alice as a
import bob as b
from util import verify_computation

def main():

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description='Run the Yao protocol between two parties to compute the maximum value of two sets.')
    parser.add_argument('party', 
                        metavar='party',
                        type=str.lower, 
                        choices=['alice', 'bob', 'Alice'], 
                        help='The party to run the protocol with.\nPossible values:\n \'alice\': the circuit garbler.\n \'bob\': the circuit evaluator.')
    
    loglevels = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL
        }

    parser.add_argument("-l",
                            "--loglevel",
                            metavar="level",
                            choices=loglevels.keys(),
                            default="warning",
                            help="The log level (default \'warning\').\nPossible values: \'debug\', \'info\', \'warning\', \'error\', \'critical\'.")
    
    loglevel = loglevels[parser.parse_args().loglevel]

    logging.getLogger().setLevel(loglevel)

    party = parser.parse_args().party

    if(party == 'alice'):
        alice = a.Alice()
        res = alice.start()
    elif(party == 'bob'):
        bob = b.Bob()
        res = bob.listen()
    else:
        print("Unknown party: ", party)
        print("Usage: python3 ./mpc.py [alice | bob]")

        return 1
    
    verify_computation(res)

if __name__ == '__main__':
    main()