import regex

from typing import List

def clean_lines(text: str):
	# split lines
	text = regex.split(r"\r\n|\n", text)
	new_text = []
	lines_number = []
	line_n = 0
	for line in text:
		line_n += 1
		# sometimes, } is not separated from its previous word
		line = regex.sub("}", " }", line)
		line = regex.sub("\(", " (", line)

		new_line = ""
		for token in line.split():
			token = token.strip()
			if len(token) > 0 and token[0] == '%':
				break
				# ignore comment lines or inline comments
			new_line += token + " "
		if len(new_line) > 0:
			new_text.append(new_line)
			lines_number.append(line_n)
	return (new_text, lines_number)

def make_tokens(lines: List[str], lines_number: List[int]):
	"""
	Cut lines into tokens (token, line_number, instruction_number).
	"""
	tokens = []
	instruction_n = 0
	assert(len(lines) == len(lines_number))
	for line, line_n in zip(lines, lines_number):
		for token in regex.findall(r'((si \((0|1)\))|[^ ]+)', line):
			token = token[0]
			instruction_n += 1
			tokens.append((token, line_n, instruction_n))
	return tokens
