from fonction import *

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

data = getData(mot1,True,"")

infos = getIdEnt(mot1, mot2,data)
idMot2 = infos["mot2_id"]
idMot1 = infos["mot1_id"]


idRel = getIdRel(relation,data)
#resultat = isRelEntrante(idMot1, idMot2, idRel, data)

resultatInductive = isRelInductive(idMot1, idMot2, idRel, data)

# liste relations : https://www.jeuxdemots.org/jdm-about-detail-relations.php