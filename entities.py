#!/bin/python3
# -*- coding: utf-8 -*-

import sys
import re
from structure import Instruction, Root, Si0, Si1, Boucle, Fin, Zero, Un, Gauche, Droite, Pause, Imprime, Accolade, Hashtag

instruction: Instruction

def start(tokens):
	program: Root = Root()

	token = next_token(tokens)
	res = (call(token, tokens, program, 0, False), program)[0]
	if '}' in res:
		print("} rencontré en dehors d'une boucle ou d'un si.")
		print("Veuillez vérifier la bonne fermeture des accolades.")
		invalide(("}", -1, -1))
	if res[-1] != "#":
		print("Terminé sans avoir rencontré de #.")
		invalide(("#", -1, -1))
	if "fin" in res:
		print("fin recontré à l'extérieur d'une boucle, le programme pourrait s'arrêter avant la fin.")
	print("Programme valide.")

	return program

def call(token, tokens, program, indent: int, fin_boucle: bool):
	print(token[0], fin_boucle)
	# token is composed as (token, line_number, instruction_number)
	match token[0]:
		case '0':
			program.add_child(Zero(token[2], token[1], indent))
			return zero(tokens, program, indent, fin_boucle)
		case '1':
			program.add_child(Un(token[2], token[1], indent))
			return un(tokens, program, indent, fin_boucle)
		case 'G':
			program.add_child(Gauche(token[2], token[1], indent))
			return gauche(tokens, program, indent, fin_boucle)
		case 'D':
			program.add_child(Droite(token[2], token[1], indent))
			return droite(tokens, program, indent, fin_boucle)
		case 'boucle':
			boucle_ = Boucle(token[2], token[1], indent)
			program.add_child(boucle_)
			indent += 1
			return boucle(token, tokens, boucle_, indent, True)
		case 'si (0)':
			si_0 = Si0(token[2], token[1], indent)
			program.add_child(si_0)
			indent += 1
			return si0(token, tokens, si_0, indent, fin_boucle)
		case 'si (1)':
			si_1 = Si1(token[2], token[1], indent)
			program.add_child(si_1)
			indent += 1
			return si1(token, tokens, si_1, indent, fin_boucle)
		case 'fin':
			print("fin boucle:", fin_boucle)
			program.add_child(Fin(token[2], token[1], indent, fin_boucle))
			return fin(tokens, program, indent, fin_boucle)
		case '}':
			program.add_child(Accolade(token[2], token[1], indent))
			indent -= 1
			return accolade(tokens, program, indent, fin_boucle)
		case 'I':
			program.add_child(Imprime(token[2], token[1], indent))
			return imprime(tokens, program, indent, fin_boucle)
		case 'P':
			program.add_child(Pause(token[2], token[1], indent))
			return pause(tokens, program, indent, fin_boucle)
		case '#':
			program.add_child(Hashtag(token[2], token[1], indent))
			return hashtag(tokens, program, indent, fin_boucle)
		case _:
			print("Mot hors du vocab.")
			invalide(token)

def zero(tokens, program, indent, fin_boucle = False):
	token = next_token(tokens)
	return call(token, tokens, program, indent, fin_boucle)

def un(tokens, program, indent, fin_boucle = False):
	token = next_token(tokens)
	return call(token, tokens, program, indent, fin_boucle)

def gauche(tokens, program, indent, fin_boucle = False):
	token = next_token(tokens)
	return call(token, tokens, program, indent, fin_boucle)

def droite(tokens, program, indent, fin_boucle):
	token = next_token(tokens)
	return call(token, tokens, program, indent, fin_boucle)

def boucle(old_token, tokens, program, indent, fin_boucle):
	token = next_token(tokens)
	fin = call(token, tokens, program, indent, True) # True = in boucle
	if "fin" not in fin:
		print("Pas de fin dans la boucle.")
		invalide(old_token)
	fin = re.sub("fin", "okfin", fin)
	if fin[-1] != "}":
		print("Pas d'accolade fermante après le mot clé boucle.")
		invalide(old_token)
	token = next_token(tokens, old_token)
	return fin[:-1] + call(token, tokens, program, indent, fin_boucle)
	# supprime juste l'accolade

def fin(tokens, program, indent, fin_boucle):
	token = next_token(tokens)
	return "fin" + call(token, tokens, program, indent, fin_boucle)

def si0(old_token, tokens, program, indent, fin_boucle):
	token = next_token(tokens)
	accolade = call(token, tokens, program, indent, fin_boucle)
	if len(accolade) < 1 or accolade[-1] != '}':
		print("Pas d'accolade fermante après le mot clé si.")
		invalide(tokens, old_token)

	token = next_token(tokens)
	return accolade[:-1] + call(token, tokens, program, indent, fin_boucle) # suppression du dernier caractere

def si1(old_token, tokens, program, indent, fin_boucle):
	token = next_token(tokens)
	accolade = call(token, tokens, program, indent, fin_boucle)
	if len(accolade) < 1 or accolade[-1] != '}':
		print("Pas d'accolade fermante après le mot clé si.")
		invalide(tokens, old_token)

	token = next_token(tokens, program)
	return accolade[:-1] + call(token, tokens, program, indent, fin_boucle) # suppression du dernier caractere

def accolade(tokens, program, indent, fin_boucle):
	return '}'

def imprime(tokens, program, indent, fin_boucle):
	token = next_token(tokens)
	return call(token, tokens, program, indent, fin_boucle)

def pause(tokens, program, indent, fin_boucle):
	token = next_token(tokens)
	return call(token, tokens, program, indent, fin_boucle)

def hashtag(tokens, program, indent, fin_boucle):
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
