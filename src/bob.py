import logging
import os
import ot
import util
from abc import ABC

class Bob:
    """Bob is the receiver and evaluator of the Yao circuit.

    Bob receives the Yao circuit from Alice, computes the results and sends
    them back.

    Args:
        oblivious_transfer: Optional; enable the Oblivious Transfer protocol
            (True by default).
    """
    def __init__(self, oblivious_transfer=True):
        self.socket = util.EvaluatorSocket()
        self.ot = ot.ObliviousTransfer(self.socket, enabled=oblivious_transfer)

    def listen(self):
        """Start listening for Alice messages."""
        
        # Compute local maximum and write it to a file for verification
        local_max = self.local_computation()

        # Create result directory
        if not os.path.exists('src/results'):
            os.makedirs('src/results')
        # Write Bob's result
        with open('src/results/b.res', 'w') as b_res:
            b_res.write(str(local_max))


        logging.info("Start listening")
        try:

            print("Waiting for Alice...")
            # Circuit size agreement
            #self.socket.receive()         
            #self.socket.send(required_bits)                     

            # Get circuit from Alice
            entry = self.socket.receive()
            print("Enstablished communication with Alice")      
            self.socket.send(True)      
            # MPC computation
            result = self.send_evaluation(entry, local_max) #

            #Compute binary and integer representationn of the circuit result
            str_result, converted_result = util.convert_result(result)

            print("Binary result of the circuit: ", str_result[1:])
            print("Multiplexer bit: ", list(result.values())[0])
            print("Result converted to decimal:", converted_result)

            print()
            return converted_result
        
        except KeyboardInterrupt:
            logging.info("Stop listening")


    def send_evaluation(self, entry, inputs):
        """Evaluate yao circuit for all Bob and Alice's inputs and
        send back the results.

        Args:
            entry: A dict representing the circuit to evaluate.
        """
        circuit, pbits_out = entry["circuit"], entry["pbits_out"]
        garbled_tables = entry["garbled_tables"]
        b_wires = circuit.get("bob", [])  # list of Bob's wires
        N = len(b_wires)

        print(f"Received circuit from Alice")

        # Print Bob's input B
        print("Input (B): ", util.bindigits(inputs, N)[1:])
        # Compute (-B) to use in the circuit
        bin_inputs = util.bindigits(-inputs, N)
        print("Circuit input (-B):", bin_inputs[1:])
        bits_b = [int(b) for b in bin_inputs] 

        # Create dict mapping each wire of Bob to Bob's input
        b_inputs_clear = {
            b_wires[i]: bits_b[i]
            for i in range(len(b_wires))
        }

        # Evaluate and send result to Alice
        result = self.ot.send_result(circuit, garbled_tables, pbits_out,
                            b_inputs_clear)
        
        return result
        
        
    def local_computation(self):
        """ Locally compute the maximum of the input values """

        inputs = input("Enter Bob's inputs: ").split()
        inputs = [int(x) for x in inputs if x.isdigit() or (x[0] == '-' and x[1:].isdigit())]
        bob_max = max(inputs)

        if(bob_max >= -2**31 and bob_max <= 2**31 - 1):
            return bob_max
        else:
            raise Exception("Bob's max exceeds maximum size allowed (32 bits)")

