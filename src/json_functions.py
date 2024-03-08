# -*- coding: utf-8 -*-

"""Read the configuration file
"""
__version__ = '1.0'
__author__ = 'letesdev, tomas'

import json, subprocess, datetime

def lecture_fichier_configuration(text_editor, config_file):
	"""Read and print the configuration file config.json
	The user may also edit it by choising the second option. The default text 
	editor will be used in this case.
	"""
	# open the configuration file
	with open(config_file) as json_file:
		config = json.load(json_file)
		# print the content of the file
		print(json.dumps(config, indent=4))
		# ask the user for what he wants to do
		choix = 0
		while 1:
			possibles_choix = {	0:"Revenir au menu principal. ",
								1:"Ouvrir notepad pour editer le fichier de configuration. "}
			print("")
			for q, a in possibles_choix.items():
				print('{0}. {1}'.format(q, a))
			print("")
			try:
				choix = int(input("Entrez votre décision: "))
				if choix not in [0, 1]:
					print ("Choix incorrect !")
					choix = 0  # discard the incorrect input
				else:
					print('Choix fait: {0}'.format(possibles_choix[choix]))
					if choix == 0:
						break
					if choix == 1:
						# call the default text editor
						subprocess.call([text_editor,config_file])
						
			except:
				pass
	return None

def get_parameters():
	"""read config.json and return its content as a dictionnary"""
	archivo_entrada_abierto = False
	config = {}  # will contain the content of config.json deserialized
	if not archivo_entrada_abierto:
		try:
			with open('./configuration/config.json') as json_file:
				try:
					config = json.load(json_file)
				except:
					print("Error en el json")
			archivo_entrada_abierto = True
		except:
			print("Erreur avec l'ouverture du fichier de configuration.")
	return config

def ecriture_fichier_sortie(output_filename, output_path, possibles_transbordements):
	"""Write all possible transhipments found in a file.

	The name of the file is the current date (for example 2019_11_25.json is
	the name of the file generated on the 25th of November 2019)
	If the file doesn't exist, it will be created, else it will be overwritten
	"""
	if output_filename == "":  # the file doesn't exist yet
		now = datetime.datetime.today()
		output_filename = "{0}{1}_{2}_{3}.json".format(output_path, now.year, now.month, now.day)
	else:  # the file already exists
		output_filename = "{0}{1}.json".format(output_path, output_filename)
	# write all possible transhipments found in the file	
	with open(output_filename, 'w') as outfile:
		json.dump(possibles_transbordements, outfile, indent = 4)
