
"""
	Andrew Pfaendler
	2025-05-16

	ToDO:

"""

import argparse
import os, re


def detect(fn: str) -> str:
	""" take a filename and map the format to one of the three
		:param fn: filename w/o extension
	"""

	if re.search(r'.+ .+', fn):
		return "space"
	
	if re.search(r'.+_.+', fn):
		return "snake"
	
	return "cam"


def flatten(ls: list) -> list[str]:
	""" remove any nesting in a list
	"""
	out = []
	for e in ls:
		if isinstance(e, list):
			out.extend(flatten(e))
		else:
			out.append(e)
	return out


def sep_numbers(ls: list) -> list[str]:
	""" find number sequences over 3 chars and seperate
	"""
	for i, w in enumerate(ls):
		m = re.match(r'^(.*?)(\d{3,})(.*)$', w)
		if m:
			ls[i] = []
			for mi in range(1, len(m.groups()) + 1):
				val = m.group(mi)
				if val:
					ls[i].append(val)

	return flatten(ls)


def combine_singles(ls: list[str]) -> list[str]:
	""" combine runs of single alpha elements
	"""
	out = []
	tmp_str = ''
	for s in ls:
		if len(s) == 1:
			tmp_str += s
		else:
			if tmp_str:
				out.append(tmp_str)
				tmp_str = ''
			out.append(s)
	
	if tmp_str:
		out.append(tmp_str)

	return out			


def cam_parse(s: str) -> list[str]:
	out = []
	start = 0
	for i, c in enumerate(s):
		if i == 0:	# skip first char
			continue

		if c.isupper():
			out.append(s[start:i])
			start = i

	if start < len(s):
		out.append(s[start:])

	# look for number strings and seperate
	out = sep_numbers(out)

	# combine elements with single char
	out = combine_singles(out)

	return out


def replace_char(s: str, find: str, rpl: str) -> str:
	return s.replace(find, rpl)


def auto_parse(s: str, a: argparse.Namespace) -> list[str]:
	""" sequence parse the string for all type
			:param s: filename string (sans the jank)
	"""	

	# swap chars in string
	for c in a.Swap:
		s = s.replace(c, '_')

	# space split
	sp_split = s.split()

	# _ split
	under_split =[]
	for elem in sp_split:
		under_split.append(elem.split('_'))

	under_split = flatten(under_split)

	# cam split
	cam_split = []
	for elem in under_split:
		cam_split.append(cam_parse(elem))

	return flatten(cam_split)


def parse(s: str, a: argparse.Namespace) -> list[str]:
	""" parse string without extension
		:param s: the string to parse
		:param type: string format {cam, snake, space}
	"""
	if not s:
		return [""]
	
	use_str = s
	if a.JankRemove:
		tbl = str.maketrans("","", a.JankRemove)
		use_str = s.translate(tbl)
	
	use_type = a.From
	if a.From == "auto":
		# use_type = detect(use_str)
		return auto_parse(use_str, a)
	
	if use_type == "space":
		return use_str.split()
	
	if use_type == "snake":
		return use_str.split('_')

	if use_type == "cam":
		return cam_parse(use_str)
	
	return [""]


def make_type(ls: list[str], a: argparse.Namespace) -> str:
	""" make string of type from parsed elements
		:param ls: the parsed elements
		:param type: string format {cam, snake, space}
	"""
	type = a.To
	if not type in ["cam", "snake", "space"] or len(ls) == 0:
		return ""

	out_str = ""
	if type == "space":
		out_str = ' '.join(ls)
	
	if type == "snake":
		tmp = '_'.join(ls)
		if a.PreserveCase:
			out_str = tmp
		else:
			out_str = tmp.lower()

	if type == "cam":
		tmp = ''.join([x.title() for x in ls])
		if a.PreserveCase:
			out_str = tmp
		else:
			out_str = tmp[0].lower() + tmp[1:]
	
	return out_str
		

def mod_file_name(fn: str, a: argparse.Namespace) -> str:
	base = os.path.splitext(fn)[0]
	ext = os.path.splitext(fn)[1]
	parsed_base = parse(base, a)
	if parsed_base[0] == "":
		raise ValueError(f'could not parse: {fn}')
	
	mod_base = make_type(parsed_base, a)
	if mod_base == "":
		raise ValueError(f'to_type: {a.To} not reccognized')
	
	return mod_base + ext


def mod_dir_name(dn: str, a: argparse.Namespace) -> str:
	parsed_base = parse(dn, a)
	return make_type(parsed_base, a.To)


def rename_path(path: str, new_path: str) -> int:
	try:
		os.rename(path, new_path)
		return 1
	except Exception as e:
		print(f'could not rename:\n{path}\nto\n{new_path}\n{e}')
		return 0


def is_ext_ok(fn, a: argparse.Namespace) -> bool:
	if a.Ext is None:
		return True
	
	ext = os.path.splitext(fn)[1][1:]	# remove `.`
	return ext == a.Ext


def proc_files(p: str, a: argparse.Namespace, cnts = [0,0]):
	""" loop over all files in directory and change names from type to type
		:param a: cml args
	"""

	# files
	if not a.SkipFiles and not a.OneDir:
	
		# single file case
		if os.path.isfile(p):
			if not is_ext_ok(p, a):
				return cnts
			
			fp = os.path.basename(p)
			mod_fn = mod_file_name(fp, a)
			if mod_fn == p:		# no update
				return cnts
			
			if a.ListOps:	# only list what would be done, don't mutate
				print(f'f: {p} -> {mod_fn}')
				return [0,0]
			
			cnts[0] += rename_path(p, mod_fn)
			return cnts
		

		# all files in dir case
		for fn in os.listdir(p):
			fp = os.path.join(p, fn)
			if os.path.isfile(fp):
				if not is_ext_ok(fn, a):
					continue

				mod_fn = mod_file_name(fn, a)
				if mod_fn == fn:	# no update
					continue

				mod_fp = os.path.join(p,mod_fn)
				if a.ListOps:
					print(f'f: {fp} -> {mod_fp}')
					continue

				cnts[0] += rename_path(fp, mod_fp)


	# dirs
	if a.OneDir:
		mod_dn = mod_dir_name(p, a)
		if mod_dn == p:		# no update
			return cnts
		
		if a.ListOps:
			print(f'd: {p} -> {mod_dn}')
			return [0,0]
		cnts[1] += rename_path(p, mod_dn)
		return cnts


	if a.IncludeDirs:
		for dn in os.listdir(p):
			dp = os.path.join(p, dn)
			if os.path.isdir(dp):
				mod_dn = mod_dir_name(dn, a)
				if mod_dn == dn:	# no update
					continue

				mod_dp = os.path.join(p, mod_dn)
				if a.ListOps:
					print(f'd: {dp} -> {mod_dp}')
					continue

				cnts[1] += rename_path(dp, mod_dp)

	# recurse
	if a.Recursive and not a.OneDir:
		for dn in os.listdir(p):
			dp = os.path.join(p, dn)
			if os.path.isdir(dp):
				proc_files(dp, a, cnts)

	return cnts



def main():
	""" ARGS:
	"""
	
	parser = argparse.ArgumentParser()
	parser.add_argument(
        '-f', '--From',
        help="from type; default = auto",
        type=str,
        choices=["cam", "snake", "space", "auto"],
        default = "auto"
    )
      
	parser.add_argument(
		'-t', '--To',
		help="to type; default = snake",
		type=str,
		choices=["cam", "snake", "space"],
		default="snake"
	)

	parser.add_argument(
		'-r', '--Recursive',
		help="recursive process",
		action="store_true"
	)

	parser.add_argument(
		'-p', '--PreserveCase',
		help="preserve the case in names found",
		action="store_true"
	)

	parser.add_argument(
		'-d', '--IncludeDirs',
		help="process directory names as well",
		action="store_true"
	)

	parser.add_argument(
		'-x', '--SkipFiles',
		help="suppress file modification",
		action="store_true"
	)

	parser.add_argument(
		'-l', '--ListOps',
		help="list file modifications only, no mutations",
		action="store_true"
	)

	parser.add_argument(
		'-e', '--Ext',
		help="specifies the extenions to modify, otherwise all",
		type=str,
		default=None
	)

	parser.add_argument(
		'-j', '--JankRemove',
		help="string with jank chars to remove from file name",
		type=str,
		default=None
	)

	parser.add_argument(
		'-s', '--Swap',
		help="swap chars to replace with _",
		type=str,
		default=".-/+,"
	)

	parser.add_argument(
		'--OneDir',
		help="specifies the path is a single dir",
		action="store_true"
	)
      
	parser.add_argument(
        'Path',
    	help="path containing the files to convert",
		type=str,
	)
	args = parser.parse_args()

	# process files
	cnts = proc_files(args.Path, args)

	if cnts[0] > 0:
		print(f'modified: {cnts[0]} file names to {args.To} format')

	if cnts[1] > 0:
		print(f'modified: {cnts[1]} directory names to {args.To} format')

      



if __name__ == '__main__':
    main()
