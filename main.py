# -*- coding: utf-8 -*-

"""Run this file to launch the software

The current version works using a terminal 
It is currently compatible with Windows and Linux. 
"""

__version__ = '1.0'
__author__ = 'letesdev'

# libraries
import os, platform
from src.database_functions import export_types_json, search_mmsi
from src.messages_functions import decode
from src.guard_functions import find_transbordements, find_mmsi_in_message_type_5
from src.json_functions import lecture_fichier_configuration, get_parameters, ecriture_fichier_sortie
from geopy.distance import great_circle


def first_function():
	"""User choice :Choix de l'utilisateur.
		1. 	Launch a search on the database (path defined in ./configuration/config.json)
			to update the list TYPE_BATEAUX (see ./configuration/config.json)
		2. 	See current configuration. For Windows users it is possible to launch
			the default text editor to modify the file ./configuration/config.json
		3. 	Search for possible transhipments by using all files containing AIS
			messages in the folder specified in INPUT_PATH 
			(defined in ./configuration/config.json)
	"""
	choix = 0
	SO = platform.system()
	# interface with the user
	while 1:
		if SO == "Windows":
			os.system("cls")
		elif SO in ("Linux", "Darwin"):
			os.system("clear")
		print("\nMarit IMT' Guard\n")
		possibles_choix = {	0:"Sortir du programme. ",
							1:"Mettre a jour les types de bateaux. ", 
							2:"Acceder au fichier de configuration. ",
							3:"Chercher les possibles transbordements. "}
		for q, a in possibles_choix.items():
			print('{0}. {1}'.format(q, a))
		print("")
		try:
			choix = int(input("Entrez votre décision: "))
			if choix not in [0, 1, 2, 3]:
				print ("Choix incorrect ! Appuyez la touche 'Enter' pour revenir au choix...")
				input()
				choix = 0  # discard any wrong input
			else:
				if SO == "Windows":
					os.system("cls")
				elif SO in ("Linux", "Darwin"):
					os.system("clear")
				print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
				print('Choix fait: {0}\n'.format(possibles_choix[choix]))
				if choix == 0:  # return the main menu
					break
				if choix == 1:
					# update ship types
					export_types_json(parametres['GENERAL'][0]['DATABASE'])
					print("Succes! Appuyez la touche 'Enter' pour revenir au menu principal...")
					input()

				if choix == 2:
					#Show the current configuration
					lecture_fichier_configuration(parametres['GENERAL'][0]['TEXT_EDITOR'], './configuration/config.json')
					print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
					
				if choix == 3:
					#Search for possible transhipments
					mensajes123 = []  # for AIS messages of type 1, 2 or 3
					mensajes5 = []  # for AIS messages of type 5
					input_path = parametres['GENERAL'][0]['INPUT_PATH']
					#for filename in glob.glob(os.path.join(path, '*.txt')): 
					# to read file ending in .txt
					for filename in os.listdir(input_path):
						real_filename = input_path + filename
						n_mensajes123, n_mensajes5, n_lineas_malas = decode(real_filename, mensajes123, mensajes5)
					print('Les fichiers avaient {0} messages de type 1, 2, ou 3 , {1} messages de type 5 et {2} messages undécodables.'.format(n_mensajes123, n_mensajes5, n_lineas_malas))
					# call the function searching for transhipments
					possibles_transbordements = find_transbordements(parametres, mensajes123)
					print("\nSucces ! {0} possibles transbordements trouvés.".format(len(possibles_transbordements)))
					# the results are written in a json file
					# the name of the file is the current date
					ecriture_fichier_sortie(parametres['GENERAL'][0]['OUTPUT_FILENAME'], parametres['GENERAL'][0]['OUTPUT_PATH'], possibles_transbordements)
					
					print("Appuyez la touche 'Enter' pour revenir au menu principal...")
					input()
					print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
					
		except ValueError :
			print("Choix incorrect ! Saisisez un numero aussi!")

################################################################################
################################################################################
if __name__ == '__main__':
	# extract configuration for the software
	parametres = {}
	parametres = get_parameters()
	# launch the interface to interact with the user
	if parametres != {}:
		first_function()
