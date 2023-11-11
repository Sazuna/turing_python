#!/bin/python3
# -*- coding: utf-8 -*-

import sys
import re
from structure import Instruction, Root, Si0, Si1, Boucle, Fin, Zero, Un, Gauche, Droite, Pause, Imprime, Accolade, Hashtag


def start(tokens):
	program: Root = Root()
	token = next_token(tokens)
	return call(token, tokens)

def call(token, tokens):
	# token is composed as (token, line_number, instruction_number)
	print(token)
	match token[0]:
		case '0':
			return zero(tokens)
		case '1':
			return un(tokens)
		case 'G':
			return gauche(tokens)
		case 'D':
			return droite(tokens)
		case 'boucle':
			return boucle(token, tokens)
		case 'si (0)':
			return si0(token, tokens)
		case 'si (1)':
			return si1(token, tokens)
		case 'fin':
			return fin(tokens)
		case '}':
			return accolade(tokens)
		case 'I':
			return imprime(tokens)
		case 'P':
			return pause(tokens)
		case '#':
			return hashtag(tokens)
		case _:
			print("Mot hors du vocab.")
			invalide(token)

def zero(tokens):
	token = next_token(tokens)
	return call(token, tokens)

def un(tokens):
	token= next_token(tokens)
	return call(token, tokens)

def gauche(tokens):
	token = next_token(tokens)
	return call(token, tokens)

def droite(tokens):
	token = next_token(tokens)
	return call(token, tokens)

def boucle(old_token, tokens):
	token = next_token(tokens)
	print("token après boucle:", token)
	fin = call(token, tokens)
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
	return fin[:-1] + call(token, tokens)
	# supprime juste l'accolade

def fin(tokens):
	token = next_token(tokens)
	print("on rentre dans fin")
	return "fin" + call(token, tokens)

def si0(old_token, tokens):
	token = next_token(tokens)
	accolade = call(token, tokens)
	if len(accolade) < 1 or accolade[-1] != '}':
		print("Pas d'accolade fermante après le mot clé si.")
		invalide(tokens, old_token)

	token = next_token(tokens)
	return accolade[:-1] + call(token, tokens) # suppression du dernier caractere

def si1(tokens):
	token = next_token(tokens)
	accolade = call(token, tokens)
	if len(accolade) < 1 or accolade[-1] != '}':
		print("Pas d'accolade fermante après le mot clé si.")
		invalide(tokens, old_token)

	token = next_token(tokens)
	return accolade[:-1] + call(token, tokens) # suppression du dernier caractere

def accolade(tokens):
	return '}'

def imprime(tokens):
	token = next_token(tokens)
	return call(token, tokens)

def pause(tokens):
	token = next_token(tokens)
	return call(token, tokens)

def hashtag(tokens):
	if len(tokens) > 0:
		print("Il y a des tokens après #")
		invalide(tokens[0])
	print("# rencontré, fin du programme.")
	return "#"

def next_token(tokens, token=(-1, -1, -1)) -> tuple:
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
