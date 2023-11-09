
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
	def __init__(self, instruction_n: int, line_n: int):
		self.instruction_n: int = instruction_n
		self.line_n: int = line_n
		self.pre_condition: Condition = Condition(I=instruction_n)
		self.post_condition: Condition = Condition()


class Root:
	#count = 0
	def __init__(self):
		self.instruction_n: int = 0
		self.children: List(Instruction) = []
	def add_child(self, child):
		self.children.append(child)
	
class Si0(Instruction):
	def __init__(self, instruction_n: int, line_n: int):
		super().__init__(instruction_n, line_n)
		self.children: List(Instruction) = []
	def add_child(self, child):
		self.children.append(child)

	def valid(self):
		for child in children[:-1]:
			assert(type(child) != Accolade)
		assert(type(self.children[-1]) == Accolade)

class Si1(Instruction):
	def __init__(self, instruction_n:int, line_n:int):
		super().__init__(instruction_n, line_n)
		self.children: List(Instruction) = []
	def to_string() -> str:
		return "si (1)"
	def add_child(self, child):
		self.children.append(child)
	def valid(self):
		for child in children[:-1]:
			assert(type(child) != Accolade)
		assert(type(self.children[-1]) == Accolade)

class Boucle(Instruction):
	def __init__(self, instruction_n:int, line_n:int):
		super().__init__(instruction_n, line_n)
		children: List(Instruction) = []
	def to_string() -> str:
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

class Zero(Instruction):
	def __init__(self, instruction_n:int, line_n:int):
		super().__init__(instruction_n, line_n)
	def to_string() -> str:
		return "0"

class Un(Instruction):
	def __init__(self, instruction_n:int, line_n:int):
		super().__init__(instruction_n, line_n)
	def to_string() -> str:
		return "1"

class Gauche(Instruction):
	def __init__(self, instruction_n:int, line_n:int):
		super().__init__(instruction_n, line_n)
	def to_string() -> str:
		return "G"

class Droite(Instruction):
	def __init__(self, instruction_n:int, line_n:int):
		super().__init__(instruction_n, line_n)
	def to_string() -> str:
		return "D"

class Pause(Instruction):
	def __init__(self, instruction_n:int, line_n:int):
		super().__init__(instruction_n, line_n)
	def to_string() -> str:
		return "P"

class Imprime(Instruction):
	def __init__(self, instruction_n:int, line_n:int):
		super().__init__(instruction_n, line_n)
	def to_string() -> str:
		return "I"
class Accolade:
	def __init__(self, instruction_n:int, line_n:int):
		super().__init__(instruction_n, line_n)
	def to_string() -> str:
		return "}"

class Hashtag:
	def __init__(self, instruction_n:int, line_n:int):
		super().__init__(instruction_n, line_n)
	def to_string() -> str:
		return "#"

def main():
	condition = Condition(0, {0,1}, 0)
	print(condition.to_string())
	si0 = Si0(3, 20)
	print(si0.instruction_n)

if __name__ == "__main__":
	main()
