import json
import os

def generate_circuit(n=8, circuit_name='src/circuits/n-bit max.json'):
    """
        Generates a variable-sized comparison circuit for two integers, in JSON format.
        If the desired comparison is between two numbers A and B, the inputs to the circuit must be A and (-B) in order to compute the right comparison.

        Args:
            n: number of bits of each of the two integers. This is the size of the circuit
            circuit_name: name and location for saving the circuit JSON file (e.g. src/circuits/name.json)

    """
    a_in = [i for i in range(1, n+1)] # Alice's inputs (A)
    b_in = [i for i in range(n+1, 2*n+1)] # Bob's inputs (B)
    
    ands = [(i, i+n, 2*n+i) for i in range(1, n)] # First level of AND gates (for carry)
    xors = [(i, i+n, 3*n+i-2) for i in range(2, n+1)] # XOR gates (for carry)
    
    snd_level_ands = [(ands[0][2], xors[0][2], xors[len(xors)-1][2]+1)] # Second level of AND gates (between ORs and XORs)
    ors = [(ands[1][2], snd_level_ands[0][2], snd_level_ands[0][2]+1)] # OR gates (actual carry; computed over first and second level ANDs)
    
    for i in range(n-3):
        snd_level_ands += [(ors[i][2], xors[i+1][2], ors[i][2]+1)]
        ors += [(ands[i+2][2], snd_level_ands[i+1][2], snd_level_ands[i+1][2]+1)]

    final_xor_adder = (xors[len(xors)-1][2], ors[len(ors)-1][2], ors[len(ors)-1][2]+1) # Bit representing the MSB of the sum between A and (-B). Used for multiplexing the output
    
    not_out = (final_xor_adder[2], final_xor_adder[2]+1) # Used for multiplexing

    out_ands_not = [(not_out[1], i, not_out[1]+i) for i in range(1, n+1)] # AND between Alice's inputs and the multiplexing bit
    out_ands = [(final_xor_adder[2], i, not_out[1]+i) for i in range(n+1, 2*n+1)] # AND between Bob's inputs and the multiplexing bit
    
    next_index = out_ands[len(out_ands)-1][2]+1
    out_xors = [(a[2], b[2], next_index+i) for i,(a,b) in enumerate(zip(out_ands_not, out_ands))] # Final result

    circuit = {
        "name": str(n) + "-bit max",
        "circuits": [
            {
                "id": str(n) + "-bit max",
                "alice": list(reversed(a_in)),
                "bob": list(reversed(b_in)),
                "out": [final_xor_adder[2]] + list(reversed([id_out[2] for id_out in out_xors])),
                "gates": [
                    {"id": gate_id, "type": "AND", "in": [in1, in2]} for in1, in2, gate_id in ands
                ] + [
                    {"id": gate_id, "type": "XOR", "in": [in1, in2]} for in1, in2, gate_id in xors
                ] + [
                    {"id": gate_id, "type": "AND", "in": [in1, in2]} for in1, in2, gate_id in snd_level_ands
                ] + [
                    {"id": gate_id, "type": "OR", "in": [in1, in2]} for in1, in2, gate_id in ors
                ] + [
                    {"id": final_xor_adder[2], "type": "XOR", "in": [final_xor_adder[0], final_xor_adder[1]]}
                ] + [
                    {"id": not_out[1], "type": "NOT", "in": [not_out[0]]}
                ] + [
                    {"id": gate_id, "type": "AND", "in": [in1, in2]} for in1, in2, gate_id in out_ands_not
                ] + [
                    {"id": gate_id, "type": "AND", "in": [in1, in2]} for in1, in2, gate_id in out_ands
                ] + [
                    {"id": gate_id, "type": "XOR", "in": [in1, in2]} for in1, in2, gate_id in out_xors
                ]
            }
        ]
    }

    # Circuits directory creation
    if not os.path.exists(os.path.dirname(circuit_name)):
        os.makedirs(os.path.dirname(circuit_name))
    # File writing
    with open(circuit_name, 'w') as fp:
        json.dump(circuit, fp, indent=2)

