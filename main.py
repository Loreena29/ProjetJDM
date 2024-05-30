from fonction import *

"""
entre = input("Entrez une relation : ")

#separer l'entrée en 3 mots 
mots = entre.split()
if len(mots) == 3:
    # Le premier mot est le premier mot
    mot1 = mots[0]
    # Le deuxième mot est la relation
    relation = mots[1]
    # Le reste de la phrase est le deuxième mot
    mot2 = mots[2]
else:
    print("Entrée invalide")
"""

# pour les tests : entre direct les mots
mot1 = "minou"
relation = "r_agent-1"
mot2 = "blesser"

data = getData(mot1,True,"")
dataEnt = getData(mot2,False,"")
infos = getIdEnt(mot1, mot2,data)
idMot2 = infos["mot2_id"]
idMot1 = infos["mot1_id"]
idRel = getIdRel(relation,data)

# on récupère les entités liés par des génériques / spécifiques (ex : mot1 r_isa XX, mot1 r_hypo XX)
genericEntites = []
idCommuns = getGenerique(data, idMot1,mot1,relation)
for idCommun in idCommuns:
    for entity in idCommuns[idCommun]:
        entity.append(idCommun)
        genericEntites.append(entity)
genericEntites  = sorted(genericEntites,key=poids,reverse = True)

specifiquesEntites = []
idCommuns = getSpecifique(data, idMot1,mot1,relation)
for idCommun in idCommuns:
    for entity in idCommuns[idCommun]:
        entity.append(idCommun)
        specifiquesEntites.append(entity)
specifiquesEntites  = sorted(specifiquesEntites,key=poids,reverse = True)

transEntities = getRelSortante(data, idRel)
for tr in transEntities:
    tr.append(relation)
transEntities = sorted(transEntities,key=poids,reverse = True)

def resteInference():
    # relation inductive
    induct = isRelDeductiveInductive(dataEnt, idRel, 20, specifiquesEntites)
    for infos in induct:
        allInferences.append([["| oui |", mot1, infos[0], infos[1], "&", infos[1], relation, mot2, "|", infos[2]], int(infos[2]), "inductive"])

    # relation déductive
    print("-----------------")
    deduct = isRelDeductiveInductive(dataEnt, idRel, 20, genericEntites)
    for infos in deduct:
        allInferences.append([["| oui |", mot1, infos[0], infos[1], "&", infos[1], relation, mot2, "|", infos[2]], int(infos[2]), "deductive"])

    # relation transitive
    trans = isRelDeductiveInductive(dataEnt, idRel, 20, transEntities)
    for infos in trans:
        allInferences.append([["| oui |", mot1, infos[0], infos[1], "&", infos[1], relation, mot2, "|", infos[2]], int(infos[2]), "transitive"])

    syn = relSynonyme(data, dataEnt, 100)
    for infos in syn:
        allInferences.append([["| oui |", mot1, "synonyme de ", infos[0], relation, infos[1], "synonyme de ",  mot2, "|", infos[2]], int(infos[2]), "synonyme"])

# format : [explication, poids, inférence]
allInferences = []

# Inférences + affichage :
# regarder si la relation existe de base + si poids négatif, skip la suite
relBase = isRelation(dataEnt, idMot1, idMot2, idRel)
if relBase[0] != "":
    if(int(relBase[1]) > -100):
        allInferences.append([["| oui |", mot1, relation, mot2, 5, "base"], int(relBase[1]), "base"])
        # suite des inférences
        resteInference()
    else:
        print("Relation de base négative, pas d'inférences possibles")
else:
    # si la relation de base n'existe pas : suite des inférences
    resteInference()
        

    


# tri par score et affichage des inférences
allInferences = sorted(allInferences,key=lambda x: x[1],reverse = True)
for inf in allInferences:
    print(inf[0])





# liste relations : https://www.jeuxdemots.org/jdm-about-detail-relations.php