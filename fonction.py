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
    mot = mot.replace(" ", "_")
    mot = mot.replace("'", "")
    # Spécifier le chemin du dossier où vous voulez enregistrer les fichiers
    dossier = "src/txt/"
    
    if entrant:
        fileTxtName = dossier + mot.replace(" ", "_")
        if(rel == ""):
            fileTxtName += "_e.txt"
        else:
            fileTxtName += "_" + rel + "_e.txt"        
        fileTxtName = os.path.join(fileTxtName)
    else:
        fileTxtName = dossier + mot.replace(" ", "_")
        if(rel == ""):
            fileTxtName += "_s.txt"
        else:
            fileTxtName += "_" + rel + "_s.txt"
        fileTxtName = os.path.join(fileTxtName)

    try:
        filesize = os.path.getsize(fileTxtName)
    except OSError:
        filesize = 0

    if filesize == 0:
        if entrant:
            fileTxtName = dossier + mot.replace(" ", "_")
            if(rel == ""):
                fileTxtName += "_e.txt"
            else:
                fileTxtName += "_" + rel + "_e.txt"        
            fileTxtName = os.path.join(fileTxtName)
        else:
            fileTxtName = dossier + mot.replace(" ", "_")
            if(rel == ""):
                fileTxtName += "_s.txt"
            else:
                fileTxtName += "_" + rel + "_s.txt"
            fileTxtName = os.path.join(fileTxtName)

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
        fileJSONName = "src/json/" + mot
        if(rel == ""):
            fileJSONName += "_e.json"
        else:
            fileJSONName += "_" + rel + "_e.json"
    else:
        fileJSONName = "src/json/" + mot
        if(rel == ""):
            fileJSONName += "_s.json"
        else:
            fileJSONName += "_" + rel + "_s.json"
    
    try:
        # Vérification de l'existence du fichier JSON
        filesize = os.path.getsize(fileJSONName)
    except OSError:
        filesize = 0

    if True:
        # Ouverture du fichier texte en lecture
        if entrant:
            fileTxtName = "src/txt/" + mot
            if(rel == ""):
                fileTxtName += "_e.txt"
            else:
                fileTxtName += "_" + rel + "_e.txt"
            fileTxt = open(os.path.join(fileTxtName), "r", encoding="utf-8")
        else:
            fileTxtName = "src/txt/" + mot
            if(rel == ""):
                fileTxtName += "_s.txt"
            else:
                fileTxtName += "_" + rel + "_s.txt"
            fileTxt = open(os.path.join(fileTxtName), "r", encoding="utf-8")
        
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
    mot = mot.replace(" ", "_")
    mot = mot.replace("'", "")
    # Ouvrir le fichier  Json en lecture
    if entrant :
        fileJSONName = "src/json/" + mot
        if(rel == ""):
            fileJSONName += "_e.json"
        else:
            fileJSONName += "_" + rel + "_e.json"
    else:
        fileJSONName = "src/json/" + mot
        if(rel == ""):
            fileJSONName += "_s.json"
        else:
            fileJSONName += "_" + rel + "_s.json"
    fileJSON = open(fileJSONName, "r")
    data = json.load(fileJSON)
    fileJSON.close()
    return data



def getIdEnt(mot1, mot2, data):
    json_entities = data["e"]
    mot2_id = -1
    mot1_id = -1

    for entity_key in json_entities:
        entity_name = json_entities[entity_key]['name']
        cleaned_entity_name = entity_name.replace("'", "", 2)

        # Vérification si l'entité et le mot correspondent à ce qu'on veut
        if cleaned_entity_name == mot2 :
            mot2_id = entity_key
        if cleaned_entity_name == mot1:
            mot1_id = entity_key

    result = {"mot2_id": mot2_id, "mot1_id": mot1_id}
    return result


def getIdRel(rel, data):
    jsonDataRt = data["rt"]
    idRt = -1
    for entity in jsonDataRt:
        name = jsonDataRt[entity]['trname']
        x = name.replace("'", "", 2)
        if x == rel:
            idRt = entity
            break
    return idRt

def isRelEntrante(idMot1, idRel, data):
    jsonDataR = data["r"]
    resultat = False
    w = ""
    for entity in jsonDataR:
        x = jsonDataR[entity]['node1'].replace("'", "", 2)
        y = jsonDataR[entity]['type'].replace("'", "", 2)
        w = jsonDataR[entity]["w"]
        
        if x == idMot1 and y == idRel :
            resultat = True

            break
    return [resultat,w]


def isRelDeductiveInductive(dataEnt, idRelation, limit, allEntities):
    results = []
    compteur = 0

    for entity in allEntities:
            teste = isRelEntrante(entity[0], idRelation, dataEnt)
            isRelE = teste[0]
            if isRelE:
                if "-" not in teste[1]:
                    results.append([entity[3].replace("'", ""), entity[1].replace("'", ""), entity[2].replace("'", "")])
            compteur += 1
            if compteur >= limit:
                break
    return results

def getRelEntrante(data, idRt):
    jsonDataE = data["e"]
    jsonDataR = data["r"]
    resultat = []

    for relation in jsonDataR:
        # S'il y a une relation de type idRt et que le poids est positif
        if (jsonDataR[relation]['type'] == idRt and int(jsonDataR[relation]['w']) > 0):
            node2 = jsonDataR[relation]['node1'].replace("'", "", 2)
            # on vérifie également que le mot est de type 1 (bon format)
            if (jsonDataE[node2]['type'] == '1'):
                resultat.append([node2, jsonDataE[node2]['name'],jsonDataR[relation]['w']])
    resultat = sorted(resultat,key=poids,reverse = True)
    return resultat


def getRelSortante(data, idRt):
    jsonDataE = data["e"]
    jsonDataR = data["r"]
    resultat = []

    for relation in jsonDataR:
        # S'il y a une relation de type idRt et que le poids est positif
        if (jsonDataR[relation]['type'] == idRt and int(jsonDataR[relation]['w']) > 0):
            node2 = jsonDataR[relation]['node2'].replace("'", "", 2)
            # on vérifie également que le mot est de type 1 (bon format)
            if (jsonDataE[node2]['type'] == '1'):
                resultat.append([node2, jsonDataE[node2]['name'],jsonDataR[relation]['w']])
    resultat = sorted(resultat,key=poids,reverse = True)
    return resultat




# retourne les relations génériques (revoir lesquelles)
def getGenerique(data, idMot,mot,rel):
    dico_generalisation = {"r_isa": "6", "r_holo": "10"}
    if rel in dico_generalisation:
        del dico_generalisation[rel]
    resultat = {}
    for key in dico_generalisation:
        resultat[key] = getRelSortante(data, dico_generalisation[key])

    return resultat


# retourne les relations spécifiques (revoir lesquelles)
def getSpecifique(data, idMot,mot,rel):
    dico_specialisation = {"r_hypo": "8", "r_has_part": "9"}
    if rel in dico_specialisation:
        del dico_specialisation[rel]
    resultat = {}
    for key in dico_specialisation:
        resultat[key] = getRelSortante(data, dico_specialisation[key])
    return resultat




def poids(M):
    return int(M[2])

def isRelation(data, idMot1, idMot2, idRel):
    jsonDataR = data["r"]
    resultat = False
    w = ""
    for entity in jsonDataR:
        x = jsonDataR[entity]['node1'].replace("'", "", 2)
        y = jsonDataR[entity]['type'].replace("'", "", 2)
        z = jsonDataR[entity]['node2'].replace("'", "", 2)
        w = jsonDataR[entity]["w"]

        
        if x == idMot1 and y == idRel and z == idMot2 :
            resultat = True

            break
    return [resultat,w]

def relSynonyme(data, dataEnt, limit):
    idRelSyn = getIdRel("r_syn", data)
    #synonymes = isRelSynonyme(dataEnt, idMot1, idMot2, idRelSyn, 20)
    syn1 = getRelSortante(data, idRelSyn)
    syn2 = getRelEntrante(dataEnt, idRelSyn)
    # TODO : on itère le plus petit des deux pour gagner du temps
    limitFiles = 5
    resultat = []
    w = ""
    for i in range(limitFiles):
        s1 = syn1[i]
        dataEntree = getData(s1[1].replace("'", ""),True, "r_agent-1")
        relations = dataEntree["r"]
        for entity in relations:
            node1 = relations[entity]['node1'].replace("'", "", 2)
            type = relations[entity]['type'].replace("'", "", 2)
            node2 = relations[entity]['node2'].replace("'", "", 2)
            w = relations[entity]["w"]
            
            for j in range(limit):
                if node2 == syn2[j][0].replace("'", ""):
                    poids = int(s1[2]) + int(syn2[j][2]) + int(w)
                    resultat.append([syn1[i][1], syn2[j][1], poids])
                    break
    #resultat = sorted(resultat,key=poids,reverse = True)
    return resultat