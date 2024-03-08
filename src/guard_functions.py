# -*- coding: utf-8 -*-

"""This file contains the central function of the software

Go through all AIS messages to check whether a possible transhipment may be
found by using them. The algorithm has a high complexity so it is recommended
not to choose too many types of ships for the search (cf configuration file
config.json), nor too large values for the maximal distance, time difference
 or speed value allowed.
 In case of need, the last function of the file find_mmsi_in_message_type_5()
 can be used to extract the type of the ships from their AIS message of type 5
"""

__version__ = 1.0
__author__ = 'letesdev'


import time
from geopy.distance import great_circle
from src.database_functions import find_info_per_bateau

def check_in_all_possible_transbordements(all_possible_transbordements, mmsi_a, mmsi_b):
	"""check if there's already a possible transhipment found for the two ships
	represented by their mmsi.

	If it is the case, then this function returns True and the index (key) of
	the possible transhipment in all_possible_transbordements
	Else it return False and -1
	"""
	for x in range(0, len(all_possible_transbordements)):
		if (all_possible_transbordements[x]['Information bateau A']['MaritimeMobileServiceIdentityMMSINumber'] == mmsi_a and \
		    all_possible_transbordements[x]['Information bateau B']['MaritimeMobileServiceIdentityMMSINumber'] == mmsi_b) or \
		   (all_possible_transbordements[x]['Information bateau A']['MaritimeMobileServiceIdentityMMSINumber'] == mmsi_b and \
		    all_possible_transbordements[x]['Information bateau B']['MaritimeMobileServiceIdentityMMSINumber'] == mmsi_a):
		    # a previous meeting was found 
			return True, x
	# there wasn't any prior meeting foun between these two ships
	return False, -1


def find_transbordements(parametres, messages):
	"""determine which ships may be doing a transhipment
	return the corresponding list of ships and a list of all failed cases

	The complexity of the algorithm used here is too big (O(n) = n!) :
	no better way but checking each message with all the other messages with
	whom it wasn't checked yet was found.
	As a consequence there is a lot of if interleaved

	"""
	# collect parameters for the search as specify in config.json 
	distance_maximale_km = parametres['TRANSBORDEMENTS'][0]['DISTANCE_MAXIMALE_KM']
	vitesse_maximale_noeuds = parametres['TRANSBORDEMENTS'][0]['VITESSE_MAXIMALE_NOEUDS']
	deltaTS_maximale = parametres['TRANSBORDEMENTS'][0]['DELTA_TIMESTAMP_ENTRE_MESSAGES_MAXIMALE']
	# collect all wanted information on ships from the database
	types_de_bateaux = []
	diccionaire = parametres['TYPE_BATEAUX']
	for n in diccionaire:
		if diccionaire[n] == 1:
			types_de_bateaux.append(n)
	print('Searching MMSI and some other information per TYPE...')

	t0 = time.time()
	bateaux_filtres = find_info_per_bateau(types_de_bateaux,parametres['GENERAL'][0]['DATABASE'], parametres['WANTED_INFO'])
	t1 = time.time()
	# print the time used to the user
	# with the test database of 80Mo we had, it took ~1 min 30 sec to run this
	print('Finished in {0:.2f} seconds.'.format(t1-t0))
	# beginning of the search for possible transhipments
	
	all_possible_transbordements = {}
	num_messages = len(messages)
	print('Checking possible transbordements...')
	dic_index = 0
	for x in range(0, num_messages):  # operate for every message
		possibles_transbordements_avec_LE_message = []
		for y in range(x+1, num_messages):  # only look for unmatched messages
			# stock the position data of the two ships
			valladolid = (messages[x]['lon'], messages[x]['lat'])
			salamanca = (messages[y]['lon'], messages[y]['lat'])
			try:
				# verify if the 2 mmsi are different and that we didn't already
				# found a possible transhipment between the 2 ships,
				# considering only the first message (i.e. message[x])
				# Let's consider 4 AIS messages in chronological order
				# message1 from ship A : ...
				# message1 from ship B : ...
				# message2 from ship A : ...
				# message2 from ship B : ...
				# if a possible transhipment was found thanks to message1 from ship A and B
				# then it's not a good idea to check a possible transhipment between ship A and B
				# by using message1 from ship A and message2 from ship B : the time between
				# both message will be greater.
				# What is done is to check a possible transhipment between them both
				# with message2 from ship A and B, 
				if ((messages[x]['mmsi'] != messages[y]['mmsi']) and \
				    (messages[y]['mmsi'] not in possibles_transbordements_avec_LE_message)):
					# calculate the distance between both ships in km
					distance = great_circle(valladolid, salamanca).km
					# and the elapsed time between both messages 
					deltaTS = abs(messages[x]['Timestamp']-messages[y]['Timestamp'])/60000
					if ((float(distance) <= float(distance_maximale_km)) and \
						(deltaTS < deltaTS_maximale)):
						# if those 2 data aren't too big, the speed is then checked
						if ((float(messages[x]['speed']) <= float(vitesse_maximale_noeuds)) and \
						    (float(messages[y]['speed']) <= float(vitesse_maximale_noeuds))):
							# if both ships have a reasonnable speed
							# then a a possible transhipment has been found
							possibles_transbordements_avec_LE_message.append((messages[y]['mmsi']))
							# verify whether a possible transhipment has already been found between those 2 ships
							check, index = check_in_all_possible_transbordements(all_possible_transbordements, messages[x]['mmsi'], messages[y]['mmsi'])
							if check == False:
								# if not, we had it to all_possible_transhipment
								# The next two variables enable the function to work properly
								# even when no mmsi is found in the database
								info_A_has_been_changed = False
								info_B_has_been_changed = False
								# search for the specific information of the ships from the database
								for t in bateaux_filtres:
									if messages[x]['mmsi'] == bateaux_filtres[t]['MaritimeMobileServiceIdentityMMSINumber']:
										info_A = bateaux_filtres[t]
										info_A_has_been_changed = True
									if messages[y]['mmsi'] == bateaux_filtres[t]['MaritimeMobileServiceIdentityMMSINumber']:
										info_B = bateaux_filtres[t]
										info_B_has_been_changed = True
								if not info_A_has_been_changed:
									# case where no mmsi for ship A exist in the database
									# first discard the information from the previous ship
									info_A = {}
									# then add the mmsi from the AIS message
									info_A['MaritimeMobileServiceIdentityMMSINumber'] = messages[x]['mmsi']
									# and add the information that the ship wasn't found in the database
									info_A['MMSI present dans la BDD'] = False
								if not info_B_has_been_changed:
									# case where no mmsi for ship B exist in the database
									# first discard the information from the previous ship
									info_B = {}
									# then add the mmsi from the AIS message
									info_B['MaritimeMobileServiceIdentityMMSINumber'] = messages[y]['mmsi']
									# and add the information that the ship wasn't found in the database
									info_B['MMSI present dans la BDD'] = False
								# finally the possible transhipment and
								# all relevant information are added to all_possible_transbordements
								all_possible_transbordements[len(all_possible_transbordements)] = {
									"Information bateau A": info_A, 
									"Information bateau B": info_B, 
								    "Rencontres":{
								    	0:{
								    		"Distance entre bateaux":distance, 
								    		"Timestamp 1e message":messages[x]['Timestamp'], 
								   			"Timestamp 2e message": messages[y]['Timestamp'], 
								   			"Longitude Bateau A": messages[x]['lon'],
											"Latitude Bateau A": messages[x]['lat'],
											"Longitude Bateau B": messages[y]['lon'],
											"Latitude Bateau B": messages[y]['lat'],
								    		"Temps entre messages:":deltaTS
								   		}
								    }
							    }
							else:
								# if information was already found on those two ships
								# then what has just been found is added to the rest
								lene = len(all_possible_transbordements[index]['Rencontres'])
								all_possible_transbordements[index]['Rencontres'][lene] = {
									"Distance entre les bateaux":distance,
									"Timestamp 1e message":messages[x]['Timestamp'],
									"Timestamp 2e message": messages[y]['Timestamp'], 
									"Longitude Bateau A": messages[x]['lon'],
									"Latitude Bateau A": messages[x]['lat'],
									"Longitude Bateau B": messages[y]['lon'],
									"Latitude Bateau B": messages[y]['lat'],
									"Temps entre messages":deltaTS
								}
			except:
				pass
	# print the time needed, a few minutes were taken with the data we had for testing purpose
	# if it takes too long a time to run this function, try changing the
	# parameters of the search (max distance, speed, time, and so on...)
	t1 = time.time()
	print('Finished in {0:.2f} seconds.'.format(t1-t0))
	return all_possible_transbordements


def find_mmsi_in_message_type_5(transbordement_couple, messages_type5):
	"""Add the ship types to a possible transhipment by using AIS message of
	type 5
	"""
	for x in messages_type5:  # message_types5 is a list of messages
		if x['mmsi'] == transbordement_couple[0][0]:
			transbordement_couple[0][0].append(x['shiptype'])
		if x['mmsi'] == transbordement_couple[1][0]:
			transbordement_couple[1][0].append(x['shiptype'])
	return None
