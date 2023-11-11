
from typing import List
from dataclasses import dataclass

class Condition:
	def __init__(self, I: int =-1, BP = {0,1}, P: int =-1):
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
		return "{" + f"I = {self.I} ∧ B[P] {sign} {self.BP} ∧ P = {self.P}" + "}"

class Instruction:
	def __init__(self, instruction_n: int, line_n: int, indent: int = 0):
		self.instruction_n: int = instruction_n
		self.line_n: int = line_n
		self.pre_condition: Condition = Condition(I=instruction_n)
		self.post_condition: Condition = Condition()
		self.indent = indent
	# used to indent python programs
	def nt(self) -> str:
		return '\n' + '\t' * self.indent

class Root(Instruction):
	def __init__(self):
		super().__init__(0, 0)
		self.children: List(Instruction) = []
	def add_child(self, child):
		self.children.append(child)
	def to_python(self) -> str:
		res = "#!/bin/python3\n"
		res += "#-*- coding: utf-8 -*-\n"
		res += "import sys\n"
		res += "POS=50\n"
		res += "MAX=100\n"
		res += "BANDE = [0] * MAX\n"
		return res
	def print_program(self, ins: Instruction = None):
		if ins == None:
			ins = self
		for child in ins.children:
			print(child.to_string())
			if type(child) in (Si0, Si1, Boucle):
				self.print_program(child)
	
class Si0(Instruction):
	def __init__(self, instruction_n: int, line_n: int, indent: int = 0):
		super().__init__(instruction_n, line_n, indent)
		self.children: List(Instruction) = []
	def to_string(self) -> str:
		return "si (0)"
	def add_child(self, child):
		self.children.append(child)
	def to_python(self) -> str:
		return super().nt() + "if BANDE[POS] == 0:"
	def valid(self):
		for child in self.children[:-1]:
			assert(type(child) != Accolade)
		assert(type(self.children[-1]) == Accolade)

class Si1(Instruction):
	def __init__(self, instruction_n: int, line_n: int, indent: int = 0):
		super().__init__(instruction_n, line_n, indent)
		self.children: List(Instruction) = []
	def to_string(self) -> str:
		return "si (1)"
	def add_child(self, child):
		self.children.append(child)
	def to_python(self) -> str:
		return super().nt() + "if BANDE[POS] == 1:"
	def valid(self):
		for child in children[:-1]:
			assert(type(child) != Accolade)
		assert(type(self.children[-1]) == Accolade)

class Boucle(Instruction):
	def __init__(self, instruction_n: int, line_n: int, indent: int = 0):
		super().__init__(instruction_n, line_n, indent)
		self.children: List(Instruction) = []
	def to_string(self) -> str:
		return "boucle"
	def add_child(self, child):
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
	def to_python(self) -> str:
		return super().nt() + "while True:"

class Fin(Instruction):
	def __init__(self, instruction_n: int, line_n: int, indent: int = 0, fin_boucle: bool = False):
		super().__init__(instruction_n, line_n, indent)
		self.fin_boucle = fin_boucle
	def to_string(self) -> str:
		return "fin"
	def to_python(self) -> str:
		if self.fin_boucle:
			return super().nt() + "break"
		else:
			return super().nt() + "sys.exit(0)"

class Zero(Instruction):
	def __init__(self, instruction_n: int, line_n: int, indent: int = 0):
		super().__init__(instruction_n, line_n, indent)
	def to_string(self) -> str:
		return "0"
	def to_python(self) -> str:
		return super().nt() + "BANDE[POS] = 0"

class Un(Instruction):
	def __init__(self, instruction_n: int, line_n: int, indent: int = 0):
		super().__init__(instruction_n, line_n, indent)
	def to_string(self) -> str:
		return "1"
	def to_python(self) -> str:
		return super().nt() + "BANDE[POS] = 1"

class Gauche(Instruction):
	def __init__(self, instruction_n: int, line_n: int, indent: int = 0):
		super().__init__(instruction_n, line_n, indent)
	def to_string(self) -> str:
		return "G"
	def to_python(self) -> str:
		return super().nt() + "POS -= 1"

class Droite(Instruction):
	def __init__(self, instruction_n: int, line_n: int, indent: int = 0):
		super().__init__(instruction_n, line_n, indent)
	def to_string(self) -> str:
		return "D"
	def to_python(self) -> str:
		return super().nt() + "POS += 1"

class Pause(Instruction):
	def __init__(self, instruction_n: int, line_n: int, indent: int = 0):
		super().__init__(instruction_n, line_n, indent)
	def to_string(self) -> str:
		return "P"
	def to_python(self) -> str:
		return super().nt() + "input()"

class Imprime(Instruction):
	def __init__(self, instruction_n: int, line_n: int, indent: int = 0):
		super().__init__(instruction_n, line_n, indent)
	def to_string(self) -> str:
		return "I"
	def to_python(self) -> str:
		res = super().nt() + "print(''.join([str(x) for x in BANDE]))"
		res += super().nt() + "print(' '*POS + '^')"
		return res

class Accolade(Instruction):
	def __init__(self, instruction_n: int, line_n: int, indent: int = 0):
		super().__init__(instruction_n, line_n, indent)
	def to_string(self) -> str:
		return "}"

class Hashtag(Instruction):
	def __init__(self, instruction_n: int, line_n: int, indent: int = 0):
		super().__init__(instruction_n, line_n)
	def to_string(self) -> str:
		return "#"

def main():
	condition = Condition(0, {0,1}, 0)
	print(condition.to_string())
	si0 = Si0(3, 20)
	print(si0.instruction_n)
	print(si0.to_python())

if __name__ == "__main__":
	main()
