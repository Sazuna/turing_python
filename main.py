#!/bin/python3
# -*- coding: utf-8 -*-

import sys

import tokenize

import entities

def main(file):
	with open(file, 'r', encoding='ISO-8859-1') as f:
		program = f.read()
	program, lines_number = tokenize.clean_lines(program)
	tokens = tokenize.make_tokens(program, lines_number)
	turing = entities.start(tokens) # Create the Structure of the Machine Turing and makes sure it is valid.

	#print(turing.print_program()) # Simplified version of the program
	# (without comments etc) and better indentation.
	# TODO: repair this function (it's broken now)
	basename = '.'.join(file.split('.')[:-1])

	python_file = basename + ".py"
	#print(turing.program_to_python()) # Program converted to python.
	with open(python_file, 'w') as f:
		f.write(turing.program_to_python())

	turing.gen_pre_pos_conditions()

	conditions_file = basename + ".conditions.tsv"

	dico = turing.get_pre_pos_conditions()
	with open(conditions_file, 'w') as f:
		f.write('instruction_n\tinstruction\tpre-condition\tpost_condition\n')
		for i in range(1, len(dico)+1):
			f.write(f"{i}\t{dico[i][0]}\t{dico[i][1]}\t{dico[i][2]}\n")

	assertions_file = basename + ".assertions.py"
	with open(assertions_file, 'w') as f:
		f.write(turing.program_to_python()) # Program converted to python but with pre-assertions generated.

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Il manque le fichier TS.")
		print("Usage:\n\tpython main.py FICHIER.TS")
		sys.exit(1)
	main(sys.argv[1])
