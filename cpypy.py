import re
import sys
import argparse

def setup_arguments(parser):
	parser.add_argument('in_file', help="file name to transpile")
	parser.add_argument('out_file', help="output file")


def is_import_line(line):
	return re.search("import", line) is not None


def ends_with_colon(line):
	return re.search(":[\s]*\n$", line) is not None


def is_empty_line(line):
	return re.search("^[\t|\s]*\n$", line) is not None


def need_semicolon(line):
	return not ends_with_colon(line) and not is_empty_line(line) and not is_import_line(line)


def scope_changes(line, scope):
	count = 0
	line_to_check = line
	while line_to_check[0] == '\t':
		count = count + 1
		line_to_check = line_to_check[1:]
	return count - scope


def get_scope_tabs(scope):
	scope_tabs = '';
	for i in range(scope):
		scope_tabs = scope_tabs + '\t'
	return scope_tabs


def is_if_statement(line):
	return re.search("^[\t|\s]*if\s", line) is not None


def get_if_statement(line):
	x = re.search("^[\t|\s]*if\s", line)
	y = re.search(":[\s]*\n$", line)
	statement = line[x.end():y.start()]
	statement = re.sub("\sis\snot\s", " != ", statement)
	statement = re.sub("\s*not\s", "!", statement)
	statement = re.sub("\sis\s", " == ", statement)
	return re.sub(line[x.end():y.start()], "( " + statement + " )", line)


def is_elif_statement(line):
	return re.search("^[\t|\s]*elif\s", line) is not None


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	setup_arguments(parser)
	args = parser.parse_args()

	input_file = open(args.in_file, "r")
	output_file = open(args.out_file, "w")

	lines = input_file.readlines()
	input_file.close()

	scope = 0

	for line in lines:
		write_line = line
		n_scope_changes = scope_changes(line, scope)
		if is_import_line(line):
			write_line = re.sub("import", "#include", line)
		if is_if_statement(line):
			write_line = get_if_statement(line)
		if need_semicolon(line):
			write_line = write_line[:-1] + ';\n'
		if n_scope_changes < 0:
			scope_close = ''
			while n_scope_changes < 0:
				scope = scope - 1
				n_scope_changes = n_scope_changes + 1
				scope_close = scope_close + get_scope_tabs(scope) + '}\n'
			write_line = scope_close + write_line
		if n_scope_changes > 0:
			scope_close = ''
			while n_scope_changes > 0:
				scope_close = scope_close + get_scope_tabs(scope) + '{\n'
				scope = scope + 1
				n_scope_changes = n_scope_changes - 1
			write_line = scope_close + write_line
		if ends_with_colon(line):
			write_line = write_line[:-2] + '\n' + get_scope_tabs(scope) + '{\n'
			scope = scope + 1
		output_file.write(write_line)
	
	if scope > 0:
		scope_close = ''
		while scope > 0:
			scope = scope - 1
			scope_close = scope_close + get_scope_tabs(scope) + '}\n'
		output_file.write(scope_close)

	output_file.close()

