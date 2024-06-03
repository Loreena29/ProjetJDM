import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

import os
import requests
import json
from bs4 import BeautifulSoup as bs

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
        if rel == "":
            fileJSONName += "_e.json"
        else:
            fileJSONName += "_" + rel + "_e.json"
    else:
        fileJSONName = "src/json/" + mot
        if rel == "":
            fileJSONName += "_s.json"
        else:
            fileJSONName += "_" + rel + "_s.json"
    
    # Vérification de l'existence du fichier JSON
    if os.path.exists(fileJSONName):
        return fileJSONName

    # Récupération des données HTML
    data = getHtml(mot, entrant, rel)
    lines = str(data).splitlines()

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
    for line in lines:
        description = list(mySplit(line.strip()))
        
        if len(description) > 0:
            if description[0] == "nt":
                dict2 = {}
                id = description[1]
                if len(description) > 2:
                    dict2[fields_nt[0]] = description[2]
                dict_nt[id] = dict2

            elif description[0] == "e":
                dict2 = {}
                id = description[1]
                for i in range(3):
                    if len(description) > i + 2:
                        dict2[fields_e[i]] = description[i + 2]
                if len(description) > 5:
                    dict2[fields_e[3]] = description[5]
                dict_e[id] = dict2

            elif description[0] == "rt":
                dict2 = {}
                id = description[1]
                for i in range(2):
                    if len(description) > i + 2:
                        dict2[fields_rt[i]] = description[i + 2]
                if len(description) > 4:
                    dict2[fields_rt[2]] = description[4]
                dict_rt[id] = dict2

            elif description[0] == "r":
                dict2 = {}
                id = description[1]
                for i in range(4):
                    if len(description) > i + 2:
                        dict2[fields_r[i]] = description[i + 2]
                dict_r[id] = dict2

    # Construction du dictionnaire principal
    dict0["nt"] = dict_nt
    dict0["e"] = dict_e
    dict0["r"] = dict_r
    dict0["rt"] = dict_rt
    
    # Écriture du JSON dans le fichier
    with open(fileJSONName, "w", encoding="utf-8") as fileJSON:
        json.dump(dict0, fileJSON, indent=4)

    return fileJSONName

def getData(mot, entrant, rel):
    fileJSONName = createJSON(mot, entrant, rel)
    
    # Ouvrir le fichier JSON en lecture
    with open(fileJSONName, "r", encoding="utf-8") as fileJSON:
        data = json.load(fileJSON)
    return data


# Récupère id entité
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

# Récupère id relation
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


# Relation de base
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

# Relations inductives / déductives / transitives
def allRelations(data, dataEnt, dataTrois, mot1, mot2, rel, nomMot1, nomMot2, nomRel):
    jsonDataE = data["e"]
    jsonDataR = data["r"]
    jsonDataEntR = dataEnt["r"]
    jsonDataTroisR = dataTrois["r"]
    resultat = []
    resultatsBase = []
    allResults = []

    relationsNom = {6: "r_isa", 8: "r_hypo"}
    relationsTransitivesNom = {10: "r_holo", 9: "r_has_part", 15: "r_lieu", 28: "r_lieu-1"}

    # score selon la fiabilité de l'inférence
    scoreInductif = 1
    scoreDeductif = 1
    scoreTransitif = 1

    for relation in jsonDataR:
        
        # Si le poids est positif et que le mot est de type 1 (bon format)
        if int(jsonDataR[relation]['w']) > 0:
            relId = int(jsonDataR[relation]['type'])
            # relations déductives : r_isa / XXXX
            if relId == 6 or relId == 6:
                node2 = jsonDataR[relation]['node2'].replace("'", "", 2)
                resultat.append([node2, jsonDataE[node2]['name'], int(jsonDataR[relation]['w']) * scoreDeductif, relationsNom[relId]])
            # relations inductives : r_hypo / XXXX
            if relId == 8 or relId == 8:
                node2 = jsonDataR[relation]['node2'].replace("'", "", 2)
                resultat.append([node2, jsonDataE[node2]['name'], int(jsonDataR[relation]['w']) * scoreInductif, relationsNom[relId]])
                # relation de base
            if int(relId) == int(rel):
                node2 = jsonDataR[relation]['node2'].replace("'", "", 2)
                resultatsBase.append([node2, jsonDataE[node2]['name'], int(jsonDataR[relation]['w']), nomRel])
    
    resultat = sorted(resultat,key=poids,reverse = True)
    # création de dico pour accéder + facilement aux données sans double boucle
    dictionnaire = {int(item[0]): int(item[2]) for item in resultat}
    dicoNoms = {int(item[0]): item[1] for item in resultat}
    dicoRelations = {int(item[0]): item[3] for item in resultat}
    dictionnaireBase = {int(item[0]): int(item[2]) for item in resultatsBase}
    dicoNomsBase = {int(item[0]): item[1] for item in resultatsBase}

    # -> inférences inductives + déductives dans le premier sens
    # ensuite : on regarde pour chaque elt de resultats s'il y a une relation | elt rel mot2 |
    for relation in jsonDataEntR:
        if int(jsonDataEntR[relation]['w']) > 0:
            relId = int(jsonDataEntR[relation]['type'])
            node1 = jsonDataEntR[relation]['node1'].replace("'", "", 2)
            node2 = jsonDataEntR[relation]['node2'].replace("'", "", 2)
            if int(node1) in dictionnaire and int(relId) == int(rel):
                explication = "| oui |" + nomMot1 + " " + dicoRelations[int(node1)] + " " + dicoNoms[int(node1)] + " & " + dicoNoms[int(node1)] + " " + nomRel + " " + nomMot2
                score = int(jsonDataEntR[relation]['w']) + dictionnaire[int(node1)]
                allResults.append([explication, score])

        # relations transitives
            # autoriser seulement les relations de relationsTranstivesNom (r_lieu, etc...)
            if int(rel) in relationsTransitivesNom:
                if int(node1) in dictionnaireBase and int(relId) == int(rel):
                    explication = "| oui |" + nomMot1 + " " + nomRel + " " + dicoNomsBase[int(node1)] + " & " + dicoNomsBase[int(node1)] + " " + nomRel + " " + nomMot2
                    score = (int(jsonDataEntR[relation]['w']) * scoreTransitif) + dictionnaireBase[int(node1)]
                    allResults.append([explication, score])

    # -> inférences inductives + déductives dans le deuxième sens
    for relation in jsonDataTroisR:
        if int(jsonDataTroisR[relation]['w']) > 0:
            relId = int(jsonDataTroisR[relation]['type'])
            node1 = jsonDataTroisR[relation]['node1'].replace("'", "", 2)
            node2 = jsonDataTroisR[relation]['node2'].replace("'", "", 2)
            # relations déductives : r_isa / XXXX
            if relId == 6 or relId == 6:
                if int(node2) in dictionnaire and int(node1) == int(mot2):
                    explication = "| oui |" + nomMot1 + " " + nomRel + " " + dicoNoms[int(node2)] + " & " + nomMot2 + " " + relationsNom[relId] + " " + dicoNoms[int(node2)]
                    score = (int(jsonDataTroisR[relation]['w']) * scoreDeductif) + dictionnaire[int(node2)]
                    allResults.append([explication, score])
            # relations inductives : r_hypo / XXXX
            if relId == 8 or relId == 8:
                if int(node2) in dictionnaire and int(node1) == int(mot1):
                    explication = "| oui |" + nomMot1 + " " + nomRel + " " + dicoNoms[int(node2)] + " & " + nomMot2 + " " + relationsNom[relId] + " " + dicoNoms[int(node2)]
                    score = (int(jsonDataTroisR[relation]['w'] * scoreInductif)) + dictionnaire[int(node2)]
                    allResults.append([explication, score])    

        allResults = sorted(allResults, key=lambda x: x[1], reverse=True)
        return allResults

# Relation synonyme
def relSynonyme(data, dataEnt, relation, limit):
    idRelSyn = getIdRel("r_syn", data)
    syn1 = getRelSortante(data, idRelSyn)
    syn2 = getRelEntrante(dataEnt, idRelSyn)
    # limite de données/fichiers créés
    if len(syn2) < limit:
        limit = len(syn2)
    limitFiles = 5
    if len(syn1) < limitFiles:
        limitFiles = len(syn1)
    resultat = []
    w = ""
    for i in range(limitFiles):
        s1 = syn1[i]
        dataEntree = getData(s1[1].replace("'", ""),True, relation)
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
    return resultat

def poids(M):
    return int(M[2])