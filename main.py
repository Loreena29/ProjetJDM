from fonction import *
import time


entre = input("Entrez une relation : ")
start_time = time.time()

#separer l'entrée en 3 mots : mot1 | relation | mot2
mots = entre.split()
if len(mots) == 3:
    mot1 = mots[0]
    relation = mots[1]
    mot2 = mots[2]

    mot1 = mot1.replace("_"," ")
else:
    print("Entrée invalide")

# Récupère les données Json
data = getData(mot1,True,"")
dataEnt = getData(mot2,False,"")
dataTrois = getData(mot2,True,"")

# Récupère les id des mots et de la relation
infos = getIdEnt(mot1, mot2,data)
idMot2 = infos["mot2_id"]
idMot1 = infos["mot1_id"]
idRel = getIdRel(relation,data)

def resteInference():
    # relation inductive / déductive / transitive
    relations = allRelations(data, dataEnt, dataTrois, idMot1, idMot2, idRel, mot1, mot2, relation)
    for infos in relations:
        allInferences.append([infos[0], infos[1]])

    # relation synonyme
    syn = relSynonyme(data, dataEnt, relation, 100)
    for infos in syn:
        # réduire le score comme il y a 3 poids cumulés au lieu de 2
        score = int(infos[2])*0.66
        allInferences.append(["| oui | " + mot1 + " synonyme de " + infos[0] + " & " + infos[0] + " " + relation + " " + infos[1] + " & " + infos[1]  + " synonyme de " + mot2, score])





allInferences = []

# regarder si la relation existe de base + si poids négatif, skip la suite
relBase = isRelation(dataEnt, idMot1, idMot2, idRel)
if relBase[0] != "":
    if(int(relBase[1]) > 0):
        # suite des inférences
        resteInference()
    else:
        print("1 | Non | Poids négatif : ", relBase[1])
else:
    # si la relation de base n'existe pas : suite des inférences
    resteInference()
        

elapsed_time = (time.time() - start_time)


# tri par score et affichage des inférences
allInferences = sorted(allInferences,key=lambda x: x[1],reverse = True)
for i in range (len(allInferences)):
    if i == 10:
        break
    print(str(i + 1) + " " + allInferences[i][0], "| ", allInferences[i][1])

print("\nTemps d'exécution : ", elapsed_time, "s")




# liste relations : https://www.jeuxdemots.org/jdm-about-detail-relations.php