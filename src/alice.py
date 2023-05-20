import logging
import os
import ot
import util
from garbler import YaoGarbler
from abc import ABC
from circuit_generator import generate_circuit

class Alice(YaoGarbler):
    """Alice is the creator of the Yao circuit.

    Alice creates a Yao circuit and sends it to the evaluator along with her
    encrypted inputs. Alice will finally print the truth table of the circuit
    for all combination of Alice-Bob inputs.

    Alice does not know Bob's inputs but for the purpose
    of printing the truth table only, Alice assumes that Bob's inputs follow
    a specific order.

    Attributes:
        circuits: the JSON file containing circuits
        oblivious_transfer: Optional; enable the Oblivious Transfer protocol
            (True by default).
    """
    def __init__(self, oblivious_transfer=True):
        self.socket = util.GarblerSocket()
        self.ot = ot.ObliviousTransfer(self.socket, enabled=oblivious_transfer)

    def start(self):
        """Start Yao protocol."""

        # Compute local maximum and write it to a file for verification
        local_max = self.local_computation()

        # Create result directory
        if not os.path.exists('src/results'):
            os.makedirs('src/results')
        # Write Alice's result
        with open('src/results/a.res', 'w') as a_res:
            a_res.write(str(local_max))

        
        # Circuit generation
        generate_circuit(n=33)
        super().__init__("src/circuits/n-bit max.json")

        # Send the circuit to Bob
        circuit = self.circuits[0]
        to_send = {
            "circuit": circuit["circuit"],
            "garbled_tables": circuit["garbled_tables"],
            "pbits_out": circuit["pbits_out"],
        }
        logging.debug(f"Sending {circuit['circuit']['id']}")

        print("Enstablishing communication with Bob...")
        self.socket.send_wait(to_send)
        print("Communication enstablished")
        print("Sent circuit to Bob")

        return self.compute_mpc(circuit, local_max)




    def compute_mpc(self, entry, local_max):

        """
            MPC computation using Yao's protocol

            Args:
                entry: circuit to be garbled and sent to Bob
                local_max: maximum of Alice's inputs, computed locally

        """
        circuit, pbits, keys = entry["circuit"], entry["pbits"], entry["keys"]
        outputs = circuit["out"]
        a_wires = circuit.get("alice", [])  # Alice's wires
        a_inputs = {}  # map from Alice's wires to (key, encr_bit) inputs
        b_wires = circuit.get("bob", [])  # Bob's wires
        b_keys = {  # map from Bob's wires to a pair (key, encr_bit)
            w: self._get_encr_bits(pbits[w], key0, key1)
            for w, (key0, key1) in keys.items() if w in b_wires
        }
        N = len(a_wires)
        
        # Convert Alice's input into a binary string
        bin_inputs = util.bindigits(local_max, N) 
        print("Input (A): ", bin_inputs[1:])
        bits_a = [int(b) for b in bin_inputs]
        
        # Map Alice's wires to (key, encr_bit)
        for i in range(len(a_wires)):
            a_inputs[a_wires[i]] = (keys[a_wires[i]][bits_a[i]], pbits[a_wires[i]] ^ bits_a[i])

        # Send Alice's encrypted inputs and keys to Bob
        result = self.ot.get_result(a_inputs, b_keys)
        
        #Compute binary and integer representationn of the circuit result
        str_result, converted_result = util.convert_result(result)

        print("Received binary result: ", str_result[1:])
        print("Multiplexer bit:", list(result.values())[0])
        print("Result converted to decimal:", converted_result)

        print()

        return converted_result

    def local_computation(self):
        """ Locally compute the maximum of the input values """

        inputs = input("Enter Alice's inputs: ").split()
        inputs = [int(x) for x in inputs if x.isdigit() or (x[0] == '-' and x[1:].isdigit())]
        alice_max = max(inputs)
        
        if(alice_max >= -2**31 and alice_max <= 2**31 - 1):
            return alice_max
        else:
            raise Exception("Alice's max exceeds maximum size allowed (32 bits)")


    def _get_encr_bits(self, pbit, key0, key1):
        return ((key0, 0 ^ pbit), (key1, 1 ^ pbit))
