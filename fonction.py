import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

import os
from bs4 import BeautifulSoup as bs
import requests
import json




def getHtml(mot, entrant, rel):
    session = requests.Session()
    
    base_url = 'http://www.jeuxdemots.org/rezo-dump.php?'
    if entrant:
        params = {'gotermsubmit': 'Chercher', 'gotermrel': mot, 'rel': rel, 'relin': 'norelout'}
    else:
        params = {'gotermsubmit': 'Chercher', 'gotermrel': mot, 'rel': rel, 'relout': 'norelin'}

    response = session.get(base_url, params=params)
    soup = bs(response.text, 'html.parser')
    data = soup.find_all('code')

    # Vérification et gestion des erreurs
    while "MUTED_PLEASE_RESEND" in str(data):
        print("ERREUR")
        response = session.get(base_url, params=params)
        soup = bs(response.text, 'html.parser')
        data = soup.find_all('code')

    # Fermeture explicite de la session
    session.close()

    return data



def createTxt(mot, entrant, rel):
    prod = getHtml(mot, entrant, rel)
    
    # Spécifier le chemin du dossier où vous voulez enregistrer les fichiers
    dossier = "src/txt/"
    
    if entrant:
        fileTxtName = os.path.join(dossier, mot.replace(" ", "_") + rel + "_e.txt")
    else:
        fileTxtName = os.path.join(dossier, mot.replace(" ", "_") + rel + "_s.txt")

    try:
        filesize = os.path.getsize(fileTxtName)
        # print("Ce fichier existe ")
    except OSError:
        # print("Ce fichier n'existe pas")
        filesize = 0

    if filesize == 0:
        if entrant:
            fileTxtName = os.path.join(dossier, mot.replace(" ", "_") + rel + "_e.txt")
        else:
            fileTxtName = os.path.join(dossier, mot.replace(" ", "_") + rel + "_s.txt")

        with open(fileTxtName, "w", encoding="utf-8") as fileTxt:
            fileTxt.write(str(prod))

    return fileTxtName



def mySplit(expression):
    resultats = []
    temporaire = ""
    condition = False
    
    for i in range(len(expression)):
        if i + 1 == len(expression):
            temporaire += expression[i]
            resultats.append(temporaire)
        else:
            if expression[i] == "\'" and expression[i + 1] != ";":
                condition = True
            elif expression[i] == "\'" and expression[i + 1] == ";":
                condition = False
            if condition:
                temporaire += expression[i]
            if not condition and expression[i] != ";":
                temporaire += expression[i]
            elif not condition and expression[i] == ";":
                resultats.append(temporaire)
                temporaire = ""

    return resultats



def createJSON(mot, entrant, rel):
    # Remplacement des caractères spéciaux dans le mot
    mot = mot.replace(" ", "_")
    mot = mot.replace("'", "")
    
    # Construction du chemin complet du fichier JSON en fonction de l'entrée et de la relation
    if entrant:
        fileJSONName = "src/json/" + mot + rel + "_e.json"
    else:
        fileJSONName = "src/json/" + mot + rel + "_s.json"
    
    try:
        # Vérification de l'existence du fichier JSON
        filesize = os.path.getsize(fileJSONName)
        # print("Ce fichier existe ")
    except OSError:
        # print("Ce fichier n'existe pas")
        filesize = 0

    if True:
        # Ouverture du fichier texte en lecture
        if entrant:
            fileTxt = open(os.path.join("src/txt/", mot + rel + "_e.txt"), "r", encoding="utf-8")
        else:
            fileTxt = open(os.path.join("src/txt/", mot + rel + "_s.txt"), "r", encoding="utf-8")
        
        # Lecture des lignes du fichier texte
        lines = fileTxt.readlines()

        # Ouverture du fichier JSON en écriture
        fileJSON = open(fileJSONName, "w", encoding="utf-8")

        # Définition des champs pour les différentes parties du JSON
        fields_nt = ['ntname']
        fields_e = ["name", "type", "w", "formated name"]
        fields_rt = ['trname', 'trgpname', 'rthelp']
        fields_r = ["node1", "node2", "type", "w"]

        # Initialisation des dictionnaires pour stocker les données
        dict0 = {}
        dict_e = {}
        dict_rt = {}
        dict_r = {}
        dict_nt = {}

        # Parcours des lignes du fichier texte
        for i in range(len(lines)):
            description = list(mySplit(lines[i].strip()))
            
            if len(description) > 0:
                if description[0] == "nt":
                    dict2 = {}
                    id = description[1]
                    for i in range(1):
                        dict2[fields_nt[i]] = description[i + 2]
                    dict_nt[id] = dict2

                elif description[0] == "e":
                    dict2 = {}
                    id = description[1]
                    for i in range(3):
                        dict2[fields_e[i]] = description[i + 2]
                    if len(description) > 5:
                        dict2[fields_e[3]] = description[5]
                    dict_e[id] = dict2

                elif description[0] == "rt":
                    dict2 = {}
                    id = description[1]
                    for i in range(2):
                        dict2[fields_rt[i]] = description[i + 2]
                    if len(description) > 4:
                        dict2[fields_rt[2]] = description[4]
                    dict_rt[id] = dict2

                elif description[0] == "r":
                    dict2 = {}
                    id = description[1]
                    for i in range(4):
                        dict2[fields_r[i]] = description[i + 2]
                    dict_r[id] = dict2

        # Construction du dictionnaire principal
        dict0["nt"] = dict_nt
        dict0["e"] = dict_e
        dict0["r"] = dict_r
        dict0["rt"] = dict_rt
        
        # Écriture du JSON dans le fichier
        json.dump(dict0, fileJSON, indent=4)

        # Fermeture des fichiers
        fileJSON.close()
        fileTxt.close()

    return fileJSONName



def getData(mot,entrant,rel):
    createTxt(mot,entrant,rel)
    createJSON(mot,entrant,rel)
    
    # Ouvrir le fichier  Json en lecture
    if entrant :
        fileJSONName = "src/json/" + mot +rel+ "_e.json"
    else:
        fileJSONName = "src/json/" + mot +rel+ "_s.json"
    fileJSON = open(fileJSONName, "r")
    data = json.load(fileJSON)
    fileJSON.close()
    return data



def getIdEnt(mot1, mot2, data):
    # Extraction des données d'entités du fichier JSON
    json_entities = data["e"]

    # Initialisation des identifiants d'entité et de mot
    mot2_id = -1
    mot1_id = -1

    # Parcours de toutes les entités dans les données JSON
    for entity_key in json_entities:
        # Récupération du nom de l'entité
        entity_name = json_entities[entity_key]['name']
        
        # Suppression des deux premières occurrences de guillemets simples pour le nom
        cleaned_entity_name = entity_name.replace("'", "", 2)
        
        # Vérification si l'entité correspond à l'entité recherchée
        if cleaned_entity_name == mot2 :
            print(entity_key + ": ")
            print(json_entities[entity_key]['name'])
            # Attribution de l'identifiant de l'entité
            mot2_id = entity_key
        
        # Vérification si l'entité correspond au mot recherché
        if cleaned_entity_name == mot1:
            print(entity_key + ": ")
            print(json_entities[entity_key]['name'])
            # Attribution de l'identifiant du mot
            mot1_id = entity_key

    # Création du résultat contenant les identifiants d'entité et de mot
    result = {"mot2_id": mot2_id, "mot1_id": mot1_id}
    return result


