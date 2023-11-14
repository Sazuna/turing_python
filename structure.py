
from typing import List
from dataclasses import dataclass

class Condition:
	def __init__(self, I: int =-1, BP = {0,1}, P: int = 0):
		self.I = I
		self.BP = BP
		self.P = P
	def set_P(self, P:int):
		self.P = P
	def set_I(self, I):
		self.I = I
	def set_BP(self, BP):
		self.BP = BP
	def to_string(self) -> str:
		if self.BP in ["0", "1"]:
			sign = "="
		else:
			sign = "∈ "
		if self.P < 0:
			sign2 = ""
		else:
			sign2 = "+"
		return "{" + f"I = {self.I} ∧ B[P] {sign} {self.BP} ∧ P = P0 {sign2} {self.P}" + "}"

class Instruction:
	def __init__(self, instruction_n: int, line_n: int, parent = None):
		self.instruction_n: int = instruction_n
		self.line_n: int = line_n
		self.pre_condition: Condition = Condition(I=instruction_n)
		self.post_condition: Condition = Condition()
		self.parent = parent
	# used to indent python programs
	def nt(self, indent: int) -> str:
		return '\n' + '\t' * indent

class Root(Instruction):
	def __init__(self):
		super().__init__(0, 0)
		self.children: List(Instruction) = []
	def add_child(self, child):
		self.children.append(child)
	def program_to_python(self, ins: Instruction = None, indent: int = 0):
		if ins == None:
			ins = self
		res = ""
		res += ins.to_python(indent)
		if type(ins) in (Root, Si0, Si1, Boucle):
			if type(ins) in (Si0, Si1, Boucle):
				indent += 1
			for child in ins.children:
				res += self.program_to_python(child, indent)
		return res
	def to_python(self, indent: int = 0) -> str:
		res = "#!/bin/python3\n"
		res += "#-*- coding: utf-8 -*-\n"
		res += "import sys\n"
		res += "POS=50\n"
		res += "MAX=100\n"
		res += "BANDE = [0] * MAX\n"
		return res
	def print_program(self, ins: Instruction = None, indent: int = 0):
		if ins == None:
			ins = self
		print(" "*indent, end="")
		for child in ins.children:
			print(child.to_string(), end=" ")
			if type(child) in (Si0, Si1, Boucle):
				self.print_program(child, indent + 1)
		print("")
	
class Si0(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
		self.children: List(Instruction) = []
	def to_string(self) -> str:
		return "si (0)"
	def add_child(self, child):
		self.children.append(child)
	def to_python(self, indent: int) -> str:
		return super().nt(indent) + "if BANDE[POS] == 0:"
	def valid(self):
		for child in self.children[:-1]:
			assert(type(child) != Accolade)
		assert(type(self.children[-1]) == Accolade)

class Si1(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
		self.children: List(Instruction) = []
	def to_string(self) -> str:
		return "si (1)"
	def add_child(self, child):
		print("child added to si(1): ", type(child))
		self.children.append(child)
	def to_python(self, indent) -> str:
		return super().nt(indent) + "if BANDE[POS] == 1:"
	def valid(self):
		for child in children[:-1]:
			assert(type(child) != Accolade)
		assert(type(self.children[-1]) == Accolade)

class Boucle(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
		self.children: List(Instruction) = []
	def to_string(self) -> str:
		return "boucle"
	def add_child(self, child):
		print("child added to Boucle: ", type(child))
		self.children.append(child)
	def valid(self):
		for child in self.children[:-1]:
			assert(type(child) != Accolade)
		assert(type(self.children[-1]) == Accolade)
		fin = False
		# Trouver le mot-clé fin
		has_fin = self.search_fin(self.children[:-1])
		assert(has_fin)
	def search_fin(self, children) -> bool:
		for child in children:
			if type(child) == Fin:
				return True
			else:
				if type(child) in (Si0, Si1, Boucle):
					if self.search_fin(child.children):
						return True
		return False
	def to_python(self, indent: int) -> str:
		return super().nt(indent) + "while True:"
	def gen_post_condition(self):
		super().post_condition.setBP("1")
		super().post_condition.setP(super().pre_condition.P)
		super().post_condition.setI(super().pre_condition.I + 1)
		# TODO generer pour la derniere instruction de la boucle, le retour au début de celle-ci. Et pour les Fin, lien vers l'instruction après la boucle.

class Fin(Instruction):
	def __init__(self, instruction_n: int, line_n: int, fin_boucle: bool = True, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
		self.fin_boucle = fin_boucle
	def to_string(self) -> str:
		return "fin"
	def to_python(self, indent: int) -> str:
		if self.fin_boucle:
			return super().nt(indent) + "break"
		else:
			return super().nt(indent) + "sys.exit(0)"

class Zero(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
	def to_string(self) -> str:
		return "0"
	def to_python(self, indent: int) -> str:
		return super().nt(indent) + "BANDE[POS] = 0"
	def gen_post_condition(self): 
		super().post_condition.setBP("0")
		super().post_condition.setP(super().pre_condition.P)
		super().post_condition.setI(super().pre_condition.I + 1)

class Un(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
	def to_string(self) -> str:
		return "1"
	def to_python(self, indent: int) -> str:
		return super().nt(indent) + "BANDE[POS] = 1"
	def gen_post_condition(self):
		super().post_condition.setBP("1")
		super().post_condition.setP(super().pre_condition.P)
		super().post_condition.setI(super().pre_condition.I + 1)

class Gauche(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
	def to_string(self) -> str:
		return "G"
	def to_python(self, indent: int) -> str:
		return super().nt(indent) + "POS -= 1"
	def gen_post_condition(self):
		super().post_condition.setBP('{0, 1}')
		super().post_condition.setP(super().pre_condition.P - 1)
		super().post_condition.setI(super().pre_condition.I + 1)
		

class Droite(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
	def to_string(self) -> str:
		return "D"
	def to_python(self, indent: int) -> str:
		return super().nt(indent) + "POS += 1"
	def gen_post_condition(self):
		super().post_condition.setBP('{0, 1}')
		super().post_condition.setP(super().pre_condition.P + 1)
		super().post_condition.setI(super().pre_condition.I + 1)

class Pause(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
	def to_string(self) -> str:
		return "P"
	def to_python(self, indent: int) -> str:
		return super().nt(indent) + "input()"

class Imprime(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
	def to_string(self) -> str:
		return "I"
	def to_python(self, indent: int) -> str:
		res = super().nt(indent) + "print(''.join([str(x) for x in BANDE]))"
		res += super().nt(indent) + "print(' '*POS + '^')"
		return res

class Accolade(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
	def to_string(self) -> str:
		return "}"
	def to_python(self, indent: int) -> str:
		return ""

class Hashtag(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
	def to_string(self) -> str:
		return "#"
	def to_python(self, indent: int) -> str:
		return ""

def main():
	condition = Condition(0, {0,1}, 0)
	print(condition.to_string())
	si0 = Si0(3, 20)
	print(si0.instruction_n)
	print(si0.to_python(0))

if __name__ == "__main__":
	main()
