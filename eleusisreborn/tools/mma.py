import numpy as np
# fonction à developper pour le calcul du MMA en n'importe quel point
def onepoint_mma(nom_action,date,nb_jour):
    pass

### #la fonction final doit pour une action donnée AN , un nombre de jour X de décalage donné
### calculer l'ensemble de mmaX(AN) au sein d'une Serie pour affichage en views

def moyenne_mobile(list, Ndays) :
    return [ 0*nj for nj in range(0,Ndays)]+[(np.sum(list[(jour-Ndays+1):jour+1]))/len(list[(jour-Ndays+1):jour+1]) for jour in range (Ndays-1, len(list)-1)]
    controle = len(list)
    #print("calul de la MMA sur",len(resu),"jours, [controle :",controle,"]")