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
	print(turing.print_program()) # Simplified version of the program
	# (without comments etc) and better indentation.

	print(turing.program_to_python()) # Program converted to python.

	turing.gen_pre_pos_conditions()
	dico = turing.get_pre_pos_conditions()

	for i in range(1, len(dico)+1):
		print(i, "pre-condition:",dico[i][0], "post-condition:",dico[i][1])
	print(turing.program_to_python()) # Program converted to python but with pre-assertions generated.

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Il manque le fichier TS.")
		print("Usage:\n\tpython main.py FICHIER.TS")
		sys.exit(1)
	main(sys.argv[1])
