#!/bin/python3
# -*- coding: utf-8 -*-

import sys
import re
from structure import Instruction, Root, Si0, Si1, Boucle, Fin, Zero, Un, Gauche, Droite, Pause, Imprime, Accolade, Hashtag

instruction: Instruction

def start(tokens):
	program: Root = Root()

	token = next_token(tokens)
	return (call(token, tokens, program), program)

def call(token, tokens, program):
	# token is composed as (token, line_number, instruction_number)
	print(token)
	match token[0]:
		case '0':
			program.add_child(Zero(token[2], token[1], token[0]))
			return zero(tokens, program)
		case '1':
			program.add_child(Un(token[2], token[1], token[0]))
			return un(tokens, program)
		case 'G':
			program.add_child(Gauche(token[2], token[1], token[0]))
			return gauche(tokens, program)
		case 'D':
			program.add_child(Droite(token[2], token[1], token[0]))
			return droite(tokens, program)
		case 'boucle':
			boucle_ = Boucle(token[2], token[1], token[0])
			program.add_child(boucle_)
			return boucle(token, tokens, boucle_)
		case 'si (0)':
			si_0 = Si0(token[2], token[1], token[0])
			program.add_child(si_0)
			return si0(token, tokens, si_0)
		case 'si (1)':
			si_1 = Si1(token[2], token[1], token[0])
			program.add_child(si_1)
			return si1(token, tokens, si_1)
		case 'fin':
			program.add_child(Fin(token[2], token[1], token[0]))
			return fin(tokens, program)
		case '}':
			program.add_child(Accolade(token[2], token[1], token[0]))
			return accolade(tokens, program)
		case 'I':
			program.add_child(Imprime(token[2], token[1], token[0]))
			return imprime(tokens, program)
		case 'P':
			program.add_child(Pause(token[2], token[1], token[0]))
			return pause(tokens, program)
		case '#':
			program.add_child(Hashtag(token[2], token[1], token[0]))
			return hashtag(tokens, program)
		case _:
			print("Mot hors du vocab.")
			invalide(token)

def zero(tokens, program):
	token = next_token(tokens)
	return call(token, tokens, program)

def un(tokens, program):
	token= next_token(tokens)
	return call(token, tokens, program)

def gauche(tokens, program):
	token = next_token(tokens)
	return call(token, tokens, program)

def droite(tokens, program):
	token = next_token(tokens)
	return call(token, tokens, program)

def boucle(old_token, tokens, program):
	token = next_token(tokens)
	print("token après boucle:", token)
	fin = call(token, tokens, program)
	print("fin:", fin)
	if "fin" not in fin:
		print("Pas de fin dans la boucle.")
		invalide(old_token)
	fin = re.sub("fin", "okfin", fin)
	#elif("fin" in fin):
	#	fin = re.sub("fin", "", fin)
	# Ce code a été supprimé car le mot clé fin arrête toutes
	# les boucles imbriquées de hiérarchie supérieure à la boucle
	# contenant le fin.
	if fin[-1] != "}":
		print("Pas d'accolade fermante après le mot clé boucle.")
		invalide(old_token)
	token = next_token(tokens, old_token)
	return fin[:-1] + call(token, tokens, program)
	# supprime juste l'accolade

def fin(tokens, program):
	token = next_token(tokens)
	return "fin" + call(token, tokens, program)

def si0(old_token, tokens, program):
	token = next_token(tokens)
	accolade = call(token, tokens, program)
	if len(accolade) < 1 or accolade[-1] != '}':
		print("Pas d'accolade fermante après le mot clé si.")
		invalide(tokens, old_token)

	token = next_token(tokens)
	return accolade[:-1] + call(token, tokens, program) # suppression du dernier caractere

def si1(tokens, program):
	token = next_token(tokens)
	accolade = call(token, tokens, program)
	if len(accolade) < 1 or accolade[-1] != '}':
		print("Pas d'accolade fermante après le mot clé si.")
		invalide(tokens, old_token)

	token = next_token(tokens, program)
	return accolade[:-1] + call(token, tokens, program) # suppression du dernier caractere

def accolade(tokens, program):
	return '}'

def imprime(tokens, program):
	token = next_token(tokens)
	return call(token, tokens, program)

def pause(tokens, program):
	token = next_token(tokens)
	return call(token, tokens, program)

def hashtag(tokens, program):
	if len(tokens) > 0:
		print("Il y a des tokens après #")
		invalide(tokens[0])
	print("# rencontré, fin du programme.")
	return "#"

def next_token(tokens, token=('_', 1, 1)) -> tuple:
	if len(tokens) == 0:
		print("Plus de tokens. # non rencontré.")
		invalide(token)
	token = tokens[0]
	del tokens[0]
	return token

def invalide(token):
	print("\033[91m", end="")
	print(f"Erreur rencontrée à la ligne:\t {token[1]}\non token n°{token[2]}: {token[0]}")
	print("Programme invalide.")
	sys.exit(1)
