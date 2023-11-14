
from typing import List
from dataclasses import dataclass

class Condition:
	def __init__(self, I: int = 0, BP = {0,1}, P: int = 0):
		self.I = I
		self.BP = BP
		self.P = P
		self.prefixP = ""
	def set_P(self, P:int):
		self.P = P
	def set_I(self, I):
		self.I = I
	def set_BP(self, BP):
		self.BP = BP
	def set_prefixP(self, prefixP):
		self.prefixP = prefixP
	def to_string(self) -> str:
		if self.BP in ["0", "1"]:
			sign = "="
		else:
			sign = "∈ "
		if self.P < 0:
			sign2 = ""
		else:
			sign2 = "+"
		return "{" + f"I = {self.I} ∧ B[P] {sign} {self.BP} ∧ P = P0{self.prefixP} {sign2} {self.P}" + "}"

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
	def prev_sibling(self): # Returns Instruction
		if self.parent == None:
			return None
		self_index = self.parent.children.index(self)
		if self_index == 0:
			return None
		prev_index = self_index - 1
		prev_sibling = self.parent.children[prev_index]
		return prev_sibling
	def next_sibling(self): # Returns Instruction
		if self.parent == None:
			return None
		self_index = self.parent.children.index(self)
		if self_index == len(self.parent.children) - 1:
			return None
		next_index = self_index + 1
		next_sibling = self.parent.children[next_index]
		return next_sibling
	def get_begin_boucle(self): # Returns Instruction
		parent = self
		while type(parent) != Boucle:
			parent = parent.parent
		return parent
	def get_end_boucle(self): # Returns Instruction
		parent = self
		while type(parent) != Boucle:
			parent = parent.parent
		end_boucle = parent.next_sibling()
		return end_boucle
	# Same function for every inherited classes
	def gen_pre_condition(self):
		if self.prev_sibling() == None:
			if self.parent != None:
				# If is first child right after Boucle or Si0 Si1:
				self.pre_condition.set_P(self.parent.post_condition.P)
				self.pre_condition.set_BP(self.parent.post_condition.BP)
				self.pre_condition.set_I(self.instruction_n)
		else:
			if type(self.prev_sibling()) == Boucle:
				self.pre_condition.set_P(self.prev_sibling().post_condition.P) # We do not know where P is at this point.
				self.pre_condition.set_prefixP(" + m")
				self.pre_condition.set_BP({0, 1})
			elif type(self.prev_sibling()) in (Si0, Si1):
				self.pre_condition.set_P(self.prev_sibling().post_condition.P)
				self.pre_condition.set_prefixP(" + m")
				self.pre_condition.set_BP(self.prev_sibling().post_condition.BP)
			else: # If has previous sibling that is not Boucle, Si0, Si1:
				self.pre_condition.set_P(self.parent.post_condition.P)
				self.pre_condition.set_BP(self.parent.post_condition.BP)
				self.pre_condition.set_I(self.instruction_n)

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
	def gen_pre_pos_conditions(self, ins: Instruction = None):
		if ins == None:
			ins = self
		for child in ins.children:
			child.gen_pre_condition()
			child.gen_post_condition()
			if type(child) in (Si0, Si1, Boucle):
				self.gen_pre_pos_conditions(child)
	def get_pre_pos_conditions(self, ins: Instruction = None):
		if ins == None:
			ins = self
		dico = {}
		for child in ins.children:
			dico[child.instruction_n] = (child.pre_condition.to_string(), child.post_condition.to_string())
			if type(child) in (Si0, Si1, Boucle):
				child_pre_pos_cond = self.get_pre_pos_conditions(child)
				for key in child_pre_pos_cond:
					dico[key] = child_pre_pos_cond[key]
		return dico

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
	def gen_post_condition(self):
		self.post_condition.set_BP("0")
		self.post_condition.set_P(self.pre_condition.P)
		self.post_condition.set_I(self.pre_condition.I + 1)

class Si1(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
		self.children: List(Instruction) = []
	def to_string(self) -> str:
		return "si (1)"
	def add_child(self, child):
		self.children.append(child)
	def to_python(self, indent) -> str:
		return super().nt(indent) + "if BANDE[POS] == 1:"
	def valid(self):
		for child in children[:-1]:
			assert(type(child) != Accolade)
		assert(type(self.children[-1]) == Accolade)
	def gen_post_condition(self):
		self.post_condition.set_BP("1")
		self.post_condition.set_P(self.pre_condition.P)
		self.post_condition.set_I(self.pre_condition.I + 1)

class Boucle(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
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
	def to_python(self, indent: int) -> str:
		return super().nt(indent) + "while True:"
	def gen_post_condition(self):
		self.post_condition.set_BP(self.pre_condition.BP)
		self.post_condition.set_P(self.pre_condition.P)
		self.post_condition.set_I(self.pre_condition.I + 1)

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
	def gen_post_condition(self):
		self.post_condition.set_BP(self.pre_condition.BP)
		self.post_condition.set_P(self.pre_condition.P)
		if self.fin_boucle:
			fin_boucle = self.get_end_boucle()
			self.post_condition.set_I(fin_boucle.instruction_n)
		else:
			parent = self
			while type(parent) != Root:
				parent = parent.parent
			end_of_program = parent.children[-1]
			self.post_condition.set_I(end_of_program.instruction_n)

class Zero(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
	def to_string(self) -> str:
		return "0"
	def to_python(self, indent: int) -> str:
		return super().nt(indent) + "BANDE[POS] = 0"
	def gen_post_condition(self): 
		self.post_condition.set_BP("0")
		self.post_condition.set_P(self.pre_condition.P)
		self.post_condition.set_I(self.pre_condition.I + 1)

class Un(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
	def to_string(self) -> str:
		return "1"
	def to_python(self, indent: int) -> str:
		return super().nt(indent) + "BANDE[POS] = 1"
	def gen_post_condition(self):
		self.post_condition.set_BP("1")
		self.post_condition.set_P(self.pre_condition.P)
		self.post_condition.set_I(self.pre_condition.I + 1)

class Gauche(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
	def to_string(self) -> str:
		return "G"
	def to_python(self, indent: int) -> str:
		return super().nt(indent) + "POS -= 1"
	def gen_post_condition(self):
		self.post_condition.set_BP('{0, 1}')
		self.post_condition.set_P(self.pre_condition.P - 1)
		self.post_condition.set_I(self.pre_condition.I + 1)
		

class Droite(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
	def to_string(self) -> str:
		return "D"
	def to_python(self, indent: int) -> str:
		return super().nt(indent) + "POS += 1"
	def gen_post_condition(self):
		self.post_condition.set_BP('{0, 1}')
		self.post_condition.set_P(self.pre_condition.P + 1)
		self.post_condition.set_I(self.pre_condition.I + 1)

class Pause(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
	def to_string(self) -> str:
		return "P"
	def to_python(self, indent: int) -> str:
		return super().nt(indent) + "input()"
	def gen_post_condition(self):
		self.post_condition.set_BP(self.pre_condition.BP)
		self.post_condition.set_P(self.pre_condition.P)
		self.post_condition.set_I(self.pre_condition.I + 1)

class Imprime(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
	def to_string(self) -> str:
		return "I"
	def to_python(self, indent: int) -> str:
		res = super().nt(indent) + "print(''.join([str(x) for x in BANDE]))"
		res += super().nt(indent) + "print(' '*POS + '^')"
		return res
	def gen_post_condition(self):
		self.post_condition.set_BP(self.pre_condition.BP)
		self.post_condition.set_P(self.pre_condition.P)
		self.post_condition.set_I(self.pre_condition.I + 1)

class Accolade(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
	def to_string(self) -> str:
		return "}"
	def to_python(self, indent: int) -> str:
		return ""
	def gen_post_condition(self):
		self.post_condition.set_BP(self.pre_condition.BP)
		self.post_condition.set_P(self.pre_condition.P)
		if type(self.parent) == Boucle:
			self.post_condition.set_I(self.parent.instruction_n)
		elif type(self.parent) in (Si0, Si1):
			self.post_condition.set_I(self.parent.next_sibling().instruction_n)
		else:
			print("Accolade hors d'une Boucle ou d'un Si.")
			sys.exit(1)

class Hashtag(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
	def to_string(self) -> str:
		return "#"
	def to_python(self, indent: int) -> str:
		return ""
	def to_string(self) -> str:
		return ""
	def gen_post_condition(self):
		self.post_condition.set_BP(self.pre_condition.BP)
		self.post_condition.set_P(self.pre_condition.P)
		self.post_condition.set_I(-1) # No next
