import argparse
import itertools
import os
import re

# Function that parses the given strings.xml to extract the KEY-VALUE pairings
# Notice that it CANNOT ensure that the file you provide be genuine
def populate_dictionary(xml_path):
	print("[ INFO ] Collecting relevant info from strings file...", end=" ")
	
	dictionary = {}
	
	try:
		if not xml_path.endswith(".xml"):
			raise BaseException("%s: not a XML file" %xml_path)
			
		with open(xml_path, "r", encoding = "utf-8") as file:
			for i in file.readlines():
				if "<string name" in i:
					dictionary[re.findall("<string name=\"(.*)\">", i)[0]] = re.findall(">(.*)</string>$", i)[0]
	except FileNotFoundError:
		print("done.\n[ FATAL ] %s does not exist. Aborting." %xml_path)
		exit(1)
	except IsADirectoryError:
		print("done.\n[ FATAL ] %s is not a file. Aborting." %xml_path)
		exit(1)
	except BaseException as e:
		print("done.\n[ FATAL ] Unknown error: %s. Aborting." %str(e))
		exit(1)
	
	print("done.")
	
	return dictionary

def purge_dictionary(dictionary):
	print("[ INFO ] Removing escape characters from dictionary...", end = " ")
	
	purged_dictionary = {}
	
	for i in dictionary:
		if re.search(r"\\[', \", n]", dictionary.get(i)):
			temp = re.sub(r"\\n", " ", dictionary.get(i))
			purged_dictionary[i] = re.sub(r"\\", "", temp)
		else:
			purged_dictionary[i] = dictionary.get(i)
	
	print("done.")
	
	return purged_dictionary

# Function that scans the provided path for any file that begins with an arbitrary number of digits and an underscore
# The file extension is not important
def scan_for_guide_parts(parts_path):
	print("[ INFO ] Enumerating guide parts...", end = " ")
	
	guide_parts = []
	
	try:
		for i in os.listdir(parts_path):
			if re.search("^[\d]*_", i):
				guide_parts.append(parts_path + "/" + i)
	except FileNotFoundError:
		print("done.\n[ FATAL ] %s does not exist. Aborting." %parts_path)
		exit(1)
	except NotADirectoryError:
		print("done.\n[ FATAL ] %s is not a directory. Aborting." %parts_path)
		exit(1)
	except BaseException as e:
		print("done.\n[ FATAL ] Unknown error: %s. Aborting." %str(e))
		exit(1)
		
	if not guide_parts:
		print("done.\n[ FATAL ] The directory %s is empty. Aborting." %parts_path)
		exit(1)
	else:
		print("done.")
	
	return sorted(guide_parts)

# Function that reads all of the detected files and returns a big string with their content
def read_file_contents(list_of_guide_parts):
	print("[ INFO ] Reading files' contents...", end = " ")
	
	raw_contents = []
	
	for i in list_of_guide_parts:
		with open(i, "r", encoding = "utf-8") as file:
			raw_contents.append(file.readlines())
			
	print("done.")
			
	return "".join(list(itertools.chain.from_iterable(raw_contents)))

# Function that analyzes the content of the files and lists the keywords
# Keyword syntax: {keyword}
def collect_keywords(file_contents):
	return re.findall("{(.*?)}", file_contents)

# Function that replaces the previously found keywords with the appropriate strings
# If a keyword has no corresponding string, it will be ignored and logged in a list
def replace_keywords(collected_keywords, dictionary, file_contents):
	print("[ INFO ] Replacing keywords...", end = " ")
	
	not_replaced = []
	
	for i in collected_keywords:
		try:
			if re.search("^@string/", dictionary.get(i)):
				key = re.sub("^@string/", "", re.findall("^@string/(.*)", dictionary.get(i))[0])
				
				while re.search("^@string/", dictionary.get(key)):
					key = re.sub("^@string/", "", re.findall("^@string/(.*)", dictionary.get(key))[0])
			else:
				key = i
			
			if key.startswith("help_"):
				temp = dictionary.get(key).split()
				value = " ".join(temp[0].lower().split() + temp[1:])
			else:
				value = dictionary.get(key)
			
			file_contents = re.sub("{" + i + "}", value, file_contents)
		except TypeError:
			not_replaced.append(i)
	
	print("done.")
	
	return file_contents, not_replaced

# Function that writes the final guide
def create_unified_guide(contents, guide_path, guide_name):
	print("[ INFO ] Writing unified guide...", end = " ")
	
	try:
		with open(guide_path + "/" + guide_name, "w", encoding = "utf-8") as file:
			file.write(contents)
	except BaseException as e:
		print("done.\n[ FATAL ] Unknown error: %s. Aborting." %str(e))
		exit(1)
	
	print("done.\n")
	
	return guide_path + "/" + guide_name

# Function that informs about the unified guide path
# It also shows whether and what keywords have been ignored
def finalize(final_guide_path, not_replaced):
	if not_replaced:
		if len(not_replaced) == 1:
			print("[ WARN ] One keyword has not been replaced: {%s}." %not_replaced[0])
		else:
			print("[ WARN ] %d keywords haven't been replaced:" %len(not_replaced))
			
			for i in not_replaced:
				print("\t- {%s}" %i)
	
	print("[ INFO ] Guide generated at %s. Goodbye." %final_guide_path)

###############
# Main body

_parser = argparse.ArgumentParser(description = "Assembles a MarkDown guide from a collection of MD files and one XML file. The guide will be located where the parts reside, or at the chosen location.")
_parser.add_argument("xml", type = str, help = "path to the xml file (single file)")
_parser.add_argument("parts", type = str, help = "path to the guide parts (directory)")
_parser.add_argument("guide", type = str, nargs = "?", default = "manual.md", help = "name and/or full path of the unified guide to be generated")
_args = _parser.parse_args()

_raw_keywords_dictionary = populate_dictionary(_args.xml)
_keywords_dictionary = purge_dictionary(_raw_keywords_dictionary)
_guide_parts = scan_for_guide_parts(_args.parts)
_contents = read_file_contents(_guide_parts)
_keywords = collect_keywords(_contents)
(_reworked_contents, _ignored_keywords) = replace_keywords(_keywords, _keywords_dictionary, _contents)

if os.path.dirname(_args.guide):
	_unified_guide_path = create_unified_guide(_reworked_contents, os.path.dirname(_args.guide), os.path.basename(_args.guide))
else:
	_unified_guide_path = create_unified_guide(_reworked_contents, _args.parts, _args.guide)

finalize(_unified_guide_path, _ignored_keywords)
