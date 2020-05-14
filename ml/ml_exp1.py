import os
import sys

import mysql.connector
import pandas as pd
import numpy as np
import matplotlib
import tokened 

# from ana&alertes import sumupachat_oftheday, etude
from eleusisreborn.indicators_calculators.functions import intersection_hausse

### le but est d'analyser la force des signaux haussiers identifiés, savoir les croisements de mma et bollinger infèrieur

### on va creer une dataframe composé des signaux en booleen et une sorti correspondant à l'évolution des cours en pourcentage par pas de 10 jours

### on déterminera ainsi si les signaux haussiers (qui auront abouti à une ordre d'achat) on été des bons choix on pas et la pondération à appliquer

### def matos_action pour la récupértion des données stocké dans la BDD

def matos_action(action_studied):
    #on se connecte au serveur
    #SELECT * FROM `market_indics` WHERE `act_name` = 'Michelin' ORDER BY `date`  ASC LIMIT 10

    # datejour = today.strftime("%y/%m/%d")
    # datejour = datejour.replace('/', '-')
    # print(datejour)

    connection = mysql.connector.connect(host=tokened.bddurl,
                                         database='market_datas',
                                         user=tokened.bdduserjuwl,
                                         password=tokened.bddpassjuwl)

    # on récupère la table qui contient les données sources
    cursor = connection.cursor()
    sql_select_Query = "SELECT * FROM `market_indics` WHERE `act_name` = '%s'" %(action_studied)
    cursor.execute(sql_select_Query)
    records = cursor.fetchall()
    plage_max = (len(records))
    dfi = pd.DataFrame(records,columns=["Prim_key", "act_name", "act_isin", "date", "mk_value", "mma10", "mma20", "mma50", "mma100","mma200", "macd","bollinger_inf","bollinger_sup","signaleuh"])
    dfi.set_index(['act_name'], inplace=True)
    dfi = dfi[::-1]
    df_ex = dfi.loc[str(action_studied), :]
    mk_value = df_ex["mk_value"]
    mk_time = df_ex["date"]
    prim_key = df_ex["Prim_key"]
    act_isin = df_ex["act_isin"]
    mma10 = df_ex["mma10"]
    mma20 = df_ex["mma20"]
    mma50 = df_ex["mma50"]
    mma100 = df_ex["mma100"]
    mma200 = df_ex["mma200"]
    bol_inf = df_ex["bollinger_inf"]
    bol_sup = df_ex["bollinger_sup"]
    macd = df_ex["macd"]
    signaleuh = df_ex["signaleuh"]
    return mk_value, mk_time, mma10,mma20,mma50,mma100,mma200,bol_inf,bol_sup, plage_max

#on définit la matrice d'évolution (évolution en pourcentage sur 10 jours) : Sortie de l'algo de Ml : Y

mk_value, mk_time, mma10, mma20, mma50, mma100, mma200, bol_inf, bol_sup, plage_max = matos_action("Lvmh")
evolmatamoinsdix = np.array(mk_value.shift(-10).values)
evolmatat = np.array(mk_value.values)
evolmat = (evolmatat - evolmatamoinsdix) / evolmatamoinsdix
# print("a t",evolmatat,"à t moins dix",evolmatamoinsdix)
Yframe = {"date":mk_time, "evolution": evolmat}
Y = pd.DataFrame(Yframe)
Y.reset_index(drop=False, inplace=True)
del Y['act_name']
del Y['date']
# Y.set_index("date", inplace=True)
Y = (Y >= 0.04).astype(int)
Y_app = Y[:-10]

#on définit la dataframe des données d'entrées avec les signaux X

listdates_mma10vs20 = intersection_hausse(np.array(mma10), np.array(mma20), np.array(mk_time))
listdates_mma20vs50 = intersection_hausse(np.array(mma20), np.array(mma50), np.array(mk_time))
listdates_mma50vs100 = intersection_hausse(np.array(mma50), np.array(mma100), np.array(mk_time))
listdates_mma100vs200 = intersection_hausse(np.array(mma100), np.array(mma200), np.array(mk_time))
listdates_bolinf = intersection_hausse(np.array(mk_value), np.array(bol_inf), np.array(mk_time))

tap = pd.DataFrame(mk_time.values, columns=["date"])
cond1020 = tap["date"].isin(listdates_mma10vs20)
cond2050 = tap["date"].isin(listdates_mma20vs50)
cond50100 = tap["date"].isin(listdates_mma50vs100)
cond100200 = tap["date"].isin(listdates_mma100vs200)
condbolinf = tap["date"].isin(listdates_bolinf)

Xframe = {'date': mk_time.values, 'cond1020': cond1020, 'cond2050': cond2050, 'cond50100': cond50100, 'cond100200': cond100200, 'condbolinf': condbolinf}

X = pd.DataFrame(Xframe)
# X.set_index("date", inplace=True)
del X['date']
X_app = X[10:].astype(int)

# print(X_app," \n",Y_app)

#On découpe le dataset à 80/20 entre les données d'entrainement et les données de test

train_part = int(0.8 * len(X_app))
test_part = int(train_part + 1)

X_train = X_app.iloc[0:train_part,:].values
y_train = np.ravel(Y_app.iloc[0:train_part,:].values)

X_test = X_app.iloc[test_part:-10,:].values
y_test = np.ravel(Y_app.iloc[test_part:-10,:].values)

print("X_train \n",X_train,"\n y_train :\n",type(y_train),"\n X_test :\n",X_test,"\n y_test :\n",y_test)

from sklearn import preprocessing
std_scale = preprocessing.StandardScaler().fit(X_train)

X_train_std = std_scale.transform(X_train)
X_test_std = std_scale.transform(X_test)

# transformer en un problème de classification binaire
# y_class = np.where(y_test < 0.04, 0, 1)
# print(y_class)

# Créer une SVM avec un noyau gaussien de paramètre gamma=0.01
from sklearn import svm
classifier = svm.SVC(kernel='rbf', gamma=0.01)
#
# Entraîner la SVM sur le jeu d'entraînement
classifier.fit(X_train_std, y_train)
#
# prédire sur le jeu de test
y_test_pred = classifier.decision_function(X_test_std)

# construire la courbe ROC
from sklearn import metrics
fpr, tpr, thr = metrics.roc_curve(y_test, y_test_pred)
#
# calculer l'aire sous la courbe ROC
auc = metrics.auc(fpr, tpr)
#
# # créer une figure
from matplotlib import pyplot as plt
fig = plt.figure(figsize=(6, 6))
#
# # afficher la courbe ROC
plt.plot(fpr, tpr, '-', lw=2, label='gamma=0.01, AUC=%.2f' % auc)
#
# # donner un titre aux axes et au graphique
plt.xlabel('False Positive Rate', fontsize=16)
plt.ylabel('True Positive Rate', fontsize=16)
plt.title('SVM ROC Curve', fontsize=16)
#
# # afficher la légende
plt.legend(loc="lower right", fontsize=14)
#
# # afficher l'image
plt.show()

##########################################################

# Créer une SVM avec un noyau gaussien de paramètre gamma=0.01
from sklearn import svm
classifier = svm.SVC(kernel='rbf', gamma=0.01)

# Entraîner la SVM sur le jeu d'entraînement
classifier.fit(X_train_std, y_train)

# prédire sur le jeu de test
y_test_pred = classifier.decision_function(X_test_std)

# construire la courbe ROC
from sklearn import metrics
fpr, tpr, thr = metrics.roc_curve(y_test, y_test_pred)

# calculer l'aire sous la courbe ROC
auc = metrics.auc(fpr, tpr)

# créer une figure
from matplotlib import pyplot as plt
fig = plt.figure(figsize=(6, 6))

# afficher la courbe ROC
plt.plot(fpr, tpr, '-', lw=2, label='gamma=0.01, AUC=%.2f' % auc)

# donner un titre aux axes et au graphique
plt.xlabel('False Positive Rate', fontsize=16)
plt.ylabel('True Positive Rate', fontsize=16)
plt.title('SVM ROC Curve', fontsize=16)

# afficher la légende
plt.legend(loc="lower right", fontsize=14)

# afficher l'image
plt.show()

# choisir 6 valeurs pour C, entre 1e-2 et 1e3
C_range = np.logspace(-2, 3, 6)

# choisir 4 valeurs pour gamma, entre 1e-2 et 10
gamma_range = np.logspace(-2, 1, 4)

# grille de paramètres
param_grid = {'C': C_range, 'gamma': gamma_range}

# critère de sélection du meilleur modèle
score = 'roc_auc'

# initialiser une recherche sur grille
from sklearn import svm, model_selection

grid = model_selection.GridSearchCV(svm.SVC(kernel='rbf'),
                                    param_grid,
                                    cv=5, # 5 folds de validation croisée
                                    scoring=score)

# faire tourner la recherche sur grille
grid.fit(X_train_std, y_train)

# afficher les paramètres optimaux
print("The optimal parameters are {} with a score of {:.2f}".format(grid.best_params_, grid.best_score_))

# prédire sur le jeu de test avec le modèle optimisé
y_test_pred_cv = grid.decision_function(X_test_std)

# construire la courbe ROC du modèle optimisé
fpr_cv, tpr_cv, thr_cv = metrics.roc_curve(y_test, y_test_pred_cv)

# calculer l'aire sous la courbe ROC du modèle optimisé
auc_cv = metrics.auc(fpr_cv, tpr_cv)

# créer une figure
fig = plt.figure(figsize=(6, 6))

# afficher la courbe ROC précédente
plt.plot(fpr, tpr, '-', lw=2, label='gamma=0.01, AUC=%.2f' % auc)

# afficher la courbe ROC du modèle optimisé
plt.plot(fpr_cv, tpr_cv, '-', lw=2, label='gamma=%.1e, AUC=%.2f' % \
                                          (grid.best_params_['gamma'], auc_cv))

# donner un titre aux axes et au graphique
plt.xlabel('False Positive Rate', fontsize=16)
plt.ylabel('True Positive Rate', fontsize=16)
plt.title('SVM ROC Curve', fontsize=16)

# afficher la légende
plt.legend(loc="lower right", fontsize=14)

# afficher l'image
plt.show()

from sklearn import metrics
kmatrix = metrics.pairwise.rbf_kernel(X_train_std, gamma=0.01)

kmatrix100 = kmatrix[:100, :100]

# dessiner la matrice
plt.pcolor(kmatrix100, cmap=matplotlib.cm.PuRd)

# rajouter la légende
plt.colorbar()

# retourner l'axe des ordonnées
plt.gca().invert_yaxis()
plt.gca().xaxis.tick_top()

# afficher l'image
plt.show()

