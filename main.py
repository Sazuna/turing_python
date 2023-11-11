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
	print(tokens)
	res = entities.start(tokens)
	print(res)
	print(res[1].print_program())

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Il manque le fichier TS.")
		print("Usage:\n\tpython main.py FICHIER.TS")
		sys.exit(1)
	main(sys.argv[1])
