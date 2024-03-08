#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This fill contains all functions related to the database

In this version There are 3 relevant functions for the software
export_types_json() :
this function allows to update the existing types of ships in config.json
and thus allowed the software to work properly (given that the user has
selected the types he wanted for the search)
update_wanted_info() :
this function allows to update the column names from the database in the config
file. By default the new names are set to 0, which means the user must select
them by setting them to 1 manually to change the ouput of the next function
find_info_per_bateau() :
This function search for all the ships which correspond to one of the type
specified in config.json. It also extracts all their information from the
database as specified in config.json.

2 libraries are used :
- xlrd, to read the database which is a .xlsx file (Excel),
- json, for all treatments of config.json.
See the respective documentations if necessary.

There are 3 unused functions at the end of the file. They can be used to look
for the type of ships.
Use search_mmsi(message) to add the type of the ship to message
Use mmsi_in_database(mmsi) to get the type of a ship given its mmsi
Use find_name_of_ships to get the ship type corresponding to a list of mmsi
The last one can be used in conjonction with type 5 AIS message to verify if
the given names are correct.

>>> The following assumptions are made for the database <<<
it's a .xlsx file with one sheet
the first colonn contains the mmsi
the third one, the names
the fifth one, the types
If it's modified in the database, modifify the global variables in accordance
with those changes.
"""

__all__ = []
__version__ = 1.0
__author__ = 'snal, letesdev'

import xlrd, json

all_searched_mmsi = {}  # reduce memory programm complexity for search_mmsi()
						# by stocking all already searched mmsi
						# key : mmsi, value : type of the ship
_index_col_mmsi = 1
_index_col_name = 2
_index_col_type = 4


def export_types_json(path_of_the_database):
	"""export the types from the database into config.json

	Ask the user whether he wants to :
	- drop all registered types from the confiuration file which then add
	new ones from  the database;
	- or direcctly add all new types from the database.
	This second choice will only add the types of ship which don't already
	exist in the configuration file and left unchange all existing ones.
	
	Parameters :
	path_of_the_database: path of the database from which the types are
	extracted
	"""
	# open the configuration file
	json_file = open('./configuration/config.json','r')
	config = json.load(json_file)
	# ask the user of its intention
	choix = 0
	while 1:
		possibles_choix = { 0:"Effacer la liste des types de bateaux et " +
													"ajouter les nouveaux. ",
							1:"Mettre a jour les types de bateaux"}

		print("")
		for q, a in possibles_choix.items():
			print("{0}. {1}".format(q,a))
		print("")
		try:
			choix = int(input("Entrez votre decision: "))
			if choix not in [0,1]:
				print("Choix incorrect !")
				choix = 0
			else:
				print("Choix fait: {0}".format(possibles_choix[choix]))
				if choix == 1:
					break
				if choix == 0:  # drop all known types written in config.json
					config['TYPE_BATEAUX']={}
		except:
			pass
	# add all unknown types from the database in config.json
	types_u = set([t for t in xlrd.open_workbook(path_of_the_database).sheet_by_index(0).col_values(_index_col_type)])
	for t in types_u:
		if t in config['TYPE_BATEAUX'].keys():
			continue  # let existing types unchanged
		else:
			config['TYPE_BATEAUX'][t]=0
			# by default all new types won't be included in the relevant types
			# for the search of transhipments
	# close the config.json (it was in reading mode)
	json_file.close()
	# open config.json in writting mode
	with open('./configuration/config.json', 'w') as outfile:
		json.dump(config, outfile, indent = 4)
	return None

def update_wanted_info(path_of_the_database):
	"""
	update WANTED_INFO keys in the configuration file by using the column names
	from the database

	Parameters :
	path_of_the_database: path of the database
	 """
	# open the configuration file
	json_file = open('./configuration/config.json','r')
	config = json.load(json_file)
	# open the database
	excel = xlrd.open_workbook(path_of_the_database).sheet_by_index(0)
	column_name = []
	# extract the column names
	for i in range(excel.ncols):
		column_name.append(excel.col_values(i)[0])
	# add them as key in config['WANTED_INFO']
	for t in column_name:
		if t in config['WANTED_INFO'].keys():
			continue  # already existing keys are left untouched
		else:
			config['WANTED_INFO'][t]=0
	json_file.close()
	# write all new changes
	with open('./configuration/config.json', 'w') as outfile:
		json.dump(config, outfile, indent = 4)
	return None


def find_info_per_bateau(wanted_types,path_of_the_database, wanted_info):
	"""select the information of the database according to the specifications
	in config.json

	Parameters :
	wanted_info : a dictionnary whom keys are the name of the colums in
	the database and which values are 0 or 1 (add the info in the end result)
	path_of_the_database : path of the database
	wanted_types : contained all the types of ship that will be used to 
	find the possible transhipment
	return a dictionnary of dictionnaries containing all relevant ships and
	their information, according to the specification in wanted_info
	Example :	
	{
	"0" : {
			"LRIMOShipNo": 12345467,
			"ShipName": "ThisIsTheNameOfTheShip",
			...
		}
	"1" : {
			...
		}
	}
	...
	}
	"""
	#open the database
	db = xlrd.open_workbook(path_of_the_database).sheet_by_index(0)	
	#collect all needed columns from the database
	columns = {}
	n = 0;
	for i in wanted_info:
		if wanted_info[i] == 1:
			columns[i] = db.col_values(n)
		n = n + 1
	#memorize all index of ships we should check for transhipment
	for name, value in columns.items():
		n = [];
		index = 0;
		if name == "ShiptypeLevel5":  # focus on the column containing type
			for type_ in value:
				if type_ in wanted_types:  # keep types present in wanted_type
					n.append(index)
				index = index + 1;
	# stock in a dictionnary all ships that should be checked for transhipment
	# alongside their data that have been selected above
	bateaux = {}
	for t in n:
		lene = len(bateaux)  # first key of the dictionnary
		bateaux[lene] = {}  # bateaux is a dictionnary of dictionnaries
		for name,value in columns.items():
			# name is the same as the name of the columns in the database
			# it is used as the second key
			bateaux[lene][name] = value[t]
		bateaux[lene]["ligne dans la base de données"] = t
	return bateaux

###############################################################################
#unused functions, may be usefull in some particular cases
###############################################################################
def search_mmsi(message, path_of_the_database):
	"""add the type of the ship to the message if the mmsi is in the database
	return true if operation is successful, false otherwise
	"""
	# the global dictionnary all_searched_mmsi is used here
	#first we checked whether we've already searched for the current mmsi
	if (message['mmsi'] in all_searched_mmsi.keys()):
		message['type']=all_searched_mmsi[message['mmsi']]
		return True
	else:  # otherwise it's the first encounter with this mmsi
		# extract information from the database
		database_mmsi = [t for t in xlrd.open_workbook(path_of_the_database
							  ).sheet_by_index(0).col_values(_index_col_mmsi)]
		database_type = [t for t in xlrd.open_workbook(path_of_the_database
							  ).sheet_by_index(0).col_values(_index_col_type)]
		# search for the mmsi in the database
		try:
			type_of_the_ship = database_type[database_mmsi.index(mmsi)]
			all_searched_mmsi[message['mmsi']]=type_of_the_ship
			message['type']=type_of_the_ship
			return True
		except:  # if a ValueError exception is raised (i.e. no mmsi found)
			message['type']="None"
			return False


def mmsi_in_database(mmsi):
	"""look for the mmsi in the database and return the type of the ship
	If the search was unsuccessful, return False
	"""
	book = xlrd.open_workbook('../ShipData.xlsx')
	db = book.sheet_by_index(0)
	list_of_all_mmsi = db.col(_index_col_mmsi)
	try:
		i = list_of_all_mmsi.index(mmsi)  # an exception may rise : ValueError
		shiptype = db.col(_index_col_type)[i]
		return shiptype
	except:
		return False

def find_name_of_ships(list_of_mmsi, path_of_the_database):
	"""find the name of all corresponding ships by using there mmsi
	return a dictionnary with the mmsi as key and the name
	A list is also returned which contained all mmsi which aren't registred in
	the database.
	"""
	# only mmsi and names of ships are usefull here
	database_mmsi = [t for t in xlrd.open_workbook(path_of_the_database
							).sheet_by_index(0).col_values(_index_col_mmsi)]
	database_name = [t for t in xlrd.open_workbook(path_of_the_database
							).sheet_by_index(0).col_values(_index_col_name)]
	# create the dictionnary and the list returned
	names_of_the_ships = {}
	unknown_ships_mmsi = []
	# look for the names of the ships
	for mmsi in list_of_mmsi:
		try:
			names_of_the_ships[mmsi] = database_name[database_mmsi.index(
																		mmsi)]
			# index() raises a ValueError exception when no element
			# corresponding to mmsi is found
		except:
			unknown_ships_mmsi.append(mmsi)
	return names_of_the_ships,unknown_ships_mmsi
