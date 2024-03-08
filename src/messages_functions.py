# -*- coding: utf-8 -*-

"""Decode the AIS messages

The following function only keep the AIS messages usefull for the analysis of
the software, i.e. any message beginning with PAS ANALYSE isn't taken
"""

from pyAISm import pyAISm
from geopy.distance import great_circle
from datetime import datetime


lineas_malas = 0
#mensajes123 = []
#mensajes5 = []
def decode(filename, mensajes123, mensajes5):
    """look for the AIS messages that can be used by the software"""
    archivo_entrada_abierto = False
    cadena_vacia = ""
    cadena_salt0 = "\n"
    lineas_malas = 0
    #mensajes123 = []
    #mensajes5 = []
    timestampArray = [];

    if not archivo_entrada_abierto:
        try:
            archivo = open(filename, "r")
            archivo_entrada_abierto = True
            linea = archivo.readline()
            while (linea != cadena_vacia):
                linea = linea.rstrip("\n")
                if "PAS ANALYSE" not in linea:
                    if "!AIVDM" in linea:
                        if "c:" in linea:
                            indIni = linea.find("c:")
                            indFin = linea.find("*")
                            timestamp = int(linea[indIni+2:indFin])
                        else:
                            timestamp = "No Timestamp"
                        indIni = linea.find("!AIVDM")
                        linea = linea[indIni:]
                        try:
                            ais_data=pyAISm.decod_ais(linea)
                            ais_data=pyAISm.format_ais(ais_data)
                            ais_data['Timestamp'] = timestamp
                            #print(ais_data)
                            if str(ais_data['type']) == '1' or str(ais_data['type']) == '2' or str(ais_data['type']) == '3':
                                mensajes123.append(ais_data)
                            if str(ais_data['type']) == '5':
                                mensajes5.append(ais_data)
                        except:
                            lineas_malas = lineas_malas + 1
                            pass
                linea = archivo.readline()
            archivo.close()
        except IOError:
            print('Error en apertura de archivo ', filename)
    #print('Le fichier avait ', str(len(mensajes123)), ' messages de type 1, 2, ou 3 , ', str(len(mensajes5)), 'messages de type 5 et ', str(lineas_malas), ' messages undécodables.\n')
    return len(mensajes123), len(mensajes5), lineas_malas
