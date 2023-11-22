
from typing import List
from dataclasses import dataclass

class Condition:
	def __init__(self, I: int = 0, BP = {0,1}, P = 0, prefixP = ""):
		self.I = I
		if type(BP) == set:
			self.BP = BP
		else:
			self.BP = {BP}
		if type(P) == set:
			self.P = P
		else:
			self.P = {P}
		self.prefixP = prefixP # + m > means that there was a loop and
				  # the Position became ambiguous.
	def set_P(self, P:int):
		self.P = P
	def set_I(self, I):
		self.I = I
	def set_BP(self, BP):
		if type(BP) == set:
			self.BP = BP
		else:
			self.BP = {BP}
	def set_prefixP(self, prefixP):
		self.prefixP = prefixP
	def to_string(self) -> str:
		res = "{" + f"I = {self.I} ∧ B[P] ∈ {self.BP} ∧ P = P0{self.prefixP} "
		if len(self.P) == 1:
			P = sorted(self.P)
			if P[0] > 0:
				res += f"+ {P[0]}"
			elif P[0] < 0:
				res += f"- {-P[0]}"
			res += "}"
		else: # > 1
			assert len(self.P) > 1
			res += f"+ {self.pos_to_string()}"
		return res
	def to_string_else(self, or_condition): # for Si0 and Si1, 2 possible post-conditions
		res = self.to_string()[:-1]
		res += " ∪ "
		res += or_condition.to_string()[1:]
		return res
	def pos_to_string(self):
		P = sorted(self.P)
		res = f"({P[0]}"
		for POS in P[1:]:
			res += f" ∪ {POS}"
		return res + ")"
	# simplify two conditions
	def or_condition(self, condition):
		self.P = self.P.union(condition.P)
		self.BP = self.BP.union(condition.BP)

class Instruction:
	def __init__(self, instruction_n: int, line_n: int, parent = None):
		self.instruction_n: int = instruction_n
		self.line_n: int = line_n
		self.pre_condition: Condition = Condition(I=instruction_n)
		self.post_condition: Condition = Condition()
		self.parent = parent
		self.previous = [] # List of Instructions that might lead to this Instruction
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
	def prev_sibling_or_parent(self):
		prev_sibl = self.prev_sibling()
		if prev_sibling == None:
			return self.parent
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
		stack = [parent]
		while type(parent) != Root:
			stack.append(parent)
			parent = parent.parent
		"""
		while type(parent) != Boucle:
			parent = parent.parent
		"""
		i = len(stack) - 1
		while type(stack[i]) != Boucle:
			i -= 1
		parent = stack[i]
		end_boucle = parent.next_sibling()
		return end_boucle
	def gen_previous(self):
		prev_sibl = self.prev_sibling()
		if prev_sibl != None:
			if type(prev_sibl) == Boucle:
				fins = prev_sibl.get_fins(prev_sibl.children)
				self.previous.extend(fins)
			elif type(prev_sibl) in (Si0, Si1):
				self.previous.append(prev_sibl)
				last_instruction_of_si = prev_sibl.children[-1]
				assert type(last_instruction_of_si) == Accolade
				self.previous.append(last_instruction_of_si)
			else:
				self.previous.append(prev_sibl)
		else:
			if self.parent != None:
				self.previous.append(self.parent)
	# Function that fusions pre-conditions of every possible previous member.
	def gen_pre_condition(self, gen_previous=True):
		if gen_previous:
			self.gen_previous()
		if len(self.previous) == 0:
			self.pre_condition.set_P(self.parent.post_condition.P)
			self.pre_condition.set_BP(self.parent.post_condition.BP)
			self.pre_condition.set_I(self.instruction_n)
			self.pre_condition.set_prefixP(self.parent.post_condition.prefixP)
		else:
			if type(self.previous[0]) not in (Si0, Si1) or self.previous[0] != self.prev_sibling():
				self.pre_condition.set_P(self.previous[0].post_condition.P)
				self.pre_condition.set_BP(self.previous[0].post_condition.BP)
			elif self.previous[0].post_condition_else != None:
				self.pre_condition.set_P(self.previous[0].post_condition_else.P)
				self.pre_condition.set_BP(self.previous[0].post_condition_else.BP)
			else:
				self.previous.pop(0)
				self.gen_pre_condition(False)
				return
			#self.pre_condition.set_I(self.instruction_n)
			for prev in self.previous[1:]:
				self.pre_condition.or_condition(prev.post_condition)
			for prev in self.previous[1:]:
				if type(prev) in (Si0, Si1):
					# if Si0 or Si1 test were not valid
					self.pre_condition.or_condition(prev.post_condition_else)
		if type(self) == Boucle:
			self.pre_condition.set_prefixP(" + m")

	def get_python_pre_assertion(self, indent) -> str:
		if self.pre_condition.BP in ('0', '1'):
			return self.nt(indent) + f"assert(BANDE[POS] == {self.pre_condition.BP})"
		return ""

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
		res += "pos = 51\n"
		res += "for chiffre in sys.argv[1:]:\n"
		res += "\tchiffre = int(chiffre)\n"
		res += "\tprint(chiffre)\n"
		res += "\tfor i in range(0, chiffre+1):\n"
		res += "\t\tBANDE[pos + i] = 1\n"
		res += "\tpos += i + 3\n"
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
			if type(child) in (Si0, Si1) and child.post_condition_else != None:
				child_post_cond = child.post_condition.to_string_else(child.post_condition_else)
			else:
				child_post_cond = child.post_condition.to_string()
			dico[child.instruction_n] = (child.to_string(), child.pre_condition.to_string(), child_post_cond)
			if type(child) in (Si0, Si1, Boucle):
				child_pre_pos_cond = self.get_pre_pos_conditions(child)
				for key in child_pre_pos_cond:
					dico[key] = child_pre_pos_cond[key]
		return dico

class Si0(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
		self.children: List(Instruction) = []
		self.post_condition_else = None
	def to_string(self) -> str:
		return "si (0)"
	def add_child(self, child):
		self.children.append(child)
	def to_python(self, indent: int) -> str:
		res = super().get_python_pre_assertion(indent)
		res += super().nt(indent) + "if BANDE[POS] == 0:"
		res += super().nt(indent) + "\tpass" # if must have minimum one instruction inside of it
		return res
	def valid(self):
		for child in self.children[:-1]:
			assert(type(child) != Accolade)
		assert(type(self.children[-1]) == Accolade)
	def gen_post_condition(self):
		if 0 in self.pre_condition.BP:
			self.post_condition.set_BP(0)
			self.post_condition.set_P(self.pre_condition.P)
			self.post_condition.set_I(self.pre_condition.I + 1)
			self.post_condition.set_prefixP(self.pre_condition.prefixP)
		if 1 in self.pre_condition.BP:
			I = self.next_sibling().instruction_n
			BP = 1
			P = self.pre_condition.P
			prefixP = self.pre_condition.prefixP
			self.post_condition_else = Condition(I, BP, P, prefixP)

class Si1(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
		self.children: List(Instruction) = []
		self.post_condition_else = None
	def to_string(self) -> str:
		return "si (1)"
	def add_child(self, child):
		self.children.append(child)
	def to_python(self, indent) -> str:
		res = super().get_python_pre_assertion(indent)
		res += super().nt(indent) + "if BANDE[POS] == 1:"
		res += super().nt(indent) + "\tpass" # if must have minimum one instruction inside of it
		return res
	def valid(self):
		for child in children[:-1]:
			assert(type(child) != Accolade)
		assert(type(self.children[-1]) == Accolade)
	def gen_post_condition(self):
		if 1 in self.pre_condition.BP:
			self.post_condition.set_BP(1)
			self.post_condition.set_P(self.pre_condition.P)
			self.post_condition.set_I(self.pre_condition.I + 1)
			self.post_condition.set_prefixP(self.pre_condition.prefixP)
		if 0 in self.pre_condition.BP:
			I = self.next_sibling().instruction_n
			BP = 0
			P = self.pre_condition.P
			prefixP = self.pre_condition.prefixP
			self.post_condition_else = Condition(I, BP, P, prefixP)

class Fin(Instruction):
	def __init__(self, instruction_n: int, line_n: int, fin_boucle: bool = True, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
		self.fin_boucle = fin_boucle
	def to_string(self) -> str:
		return "fin"
	def to_python(self, indent: int) -> str:
		res = super().get_python_pre_assertion(indent)
		if self.fin_boucle:
			return res + super().nt(indent) + "break"
		else:
			return res + super().nt(indent) + "sys.exit(0)"
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
		self.post_condition.set_prefixP(self.pre_condition.prefixP)
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
	def get_fins(self, children, fins = []) -> List[Fin]:
		for child in children:
			if type(child) == Fin:
				fins.append(child)
			else:
				if type(child) in (Si0, Si1, Boucle):
					self.get_fins(child.children, fins)
		return fins
	def to_python(self, indent: int) -> str:
		res = super().get_python_pre_assertion(indent)
		res += super().nt(indent) + "while True:"
		res += super().nt(indent) + "\tpass" # Boucle must have minimum one instruction inside of it
		return res
	def gen_post_condition(self):
		self.post_condition.set_BP(self.pre_condition.BP)
		self.post_condition.set_P(self.pre_condition.P)
		self.post_condition.set_I(self.pre_condition.I + 1)
		self.post_condition.set_prefixP(self.pre_condition.prefixP)

class Zero(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
	def to_string(self) -> str:
		return "0"
	def to_python(self, indent: int) -> str:
		res = super().get_python_pre_assertion(indent)
		return res + super().nt(indent) + "BANDE[POS] = 0"
	def gen_post_condition(self): 
		self.post_condition.set_BP(0)
		self.post_condition.set_P(self.pre_condition.P)
		self.post_condition.set_I(self.pre_condition.I + 1)
		self.post_condition.set_prefixP(self.pre_condition.prefixP)

class Un(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
	def to_string(self) -> str:
		return "1"
	def to_python(self, indent: int) -> str:
		res = super().get_python_pre_assertion(indent)
		return res + super().nt(indent) + "BANDE[POS] = 1"
	def gen_post_condition(self):
		self.post_condition.set_BP(1)
		self.post_condition.set_P(self.pre_condition.P)
		self.post_condition.set_I(self.pre_condition.I + 1)
		self.post_condition.set_prefixP(self.pre_condition.prefixP)

class Gauche(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
	def to_string(self) -> str:
		return "G"
	def to_python(self, indent: int) -> str:
		res = super().get_python_pre_assertion(indent)
		return res + super().nt(indent) + "POS -= 1"
	def gen_post_condition(self):
		self.post_condition.set_BP({0, 1})
		self.post_condition.set_P({P - 1 for P in self.pre_condition.P})
		self.post_condition.set_I(self.pre_condition.I + 1)
		self.post_condition.set_prefixP(self.pre_condition.prefixP)
		

class Droite(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
	def to_string(self) -> str:
		return "D"
	def to_python(self, indent: int) -> str:
		res = super().get_python_pre_assertion(indent)
		return res + super().nt(indent) + "POS += 1"
	def gen_post_condition(self):
		self.post_condition.set_BP({0, 1})
		self.post_condition.set_P({P + 1 for P in self.pre_condition.P})
		self.post_condition.set_I(self.pre_condition.I + 1)
		self.post_condition.set_prefixP(self.pre_condition.prefixP)

class Pause(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
	def to_string(self) -> str:
		return "P"
	def to_python(self, indent: int) -> str:
		res = super().get_python_pre_assertion(indent)
		return res + super().nt(indent) + "input()"
	def gen_post_condition(self):
		self.post_condition.set_BP(self.pre_condition.BP)
		self.post_condition.set_P(self.pre_condition.P)
		self.post_condition.set_I(self.pre_condition.I + 1)
		self.post_condition.set_prefixP(self.pre_condition.prefixP)

class Imprime(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
	def to_string(self) -> str:
		return "I"
	def to_python(self, indent: int) -> str:
		res = super().get_python_pre_assertion(indent)
		res += super().nt(indent) + "print(''.join([str(x) for x in BANDE]))"
		res += super().nt(indent) + "print(' '*POS + '^')"
		return res
	def gen_post_condition(self):
		self.post_condition.set_BP(self.pre_condition.BP)
		self.post_condition.set_P(self.pre_condition.P)
		self.post_condition.set_I(self.pre_condition.I + 1)
		self.post_condition.set_prefixP(self.pre_condition.prefixP)

class Accolade(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
	def to_string(self) -> str:
		return "}"
	def to_python(self, indent: int) -> str:
		res = super().get_python_pre_assertion(indent)
		return res
		return "" # If we do not want to print pre-assertion before }
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
		self.post_condition.set_prefixP(self.pre_condition.prefixP)

class Hashtag(Instruction):
	def __init__(self, instruction_n: int, line_n: int, parent: Instruction = None):
		super().__init__(instruction_n, line_n, parent)
	def to_string(self) -> str:
		return "#"
	def to_python(self, indent: int) -> str:
		res = super().get_python_pre_assertion(indent)
		return res
	def gen_post_condition(self):
		self.post_condition.set_BP(self.pre_condition.BP)
		self.post_condition.set_P(self.pre_condition.P)
		self.post_condition.set_I(-1) # No next
		self.post_condition.set_prefixP(self.pre_condition.prefixP)
