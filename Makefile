ALICE = python3 src/mpc.py alice  # circuit generator 
BOB = python3 src/mpc.py bob      # circuit evaluator 

default:
	@echo 'Usage 1: make {alice, bob}'
clean:
	rm -rf __pycache__
	rm -rf src/__pycache__
	rm -f src/results/a.res
	rm -f src/results/b.res

alice:
	${ALICE}

bob:
	${BOB}
