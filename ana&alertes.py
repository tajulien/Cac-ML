import os
import sys

import mysql.connector
import numpy as np
import pandas as pd

from eleusisreborn.indicators_calculators.functions import intersection_hausse

sys.path.append(os.getcwd()+"\\src\\eleusisreborn\\tools\\")

from datetime import date
import tokened

today = date.today()

def etude(action_name):
    #on se connecte au serveur
    #SELECT * FROM `market_indics` WHERE `date` = '20-03-24'

    datejour = today.strftime("%y/%m/%d")
    datejour = datejour.replace('/', '-')
    # print(datejour)
    connection = mysql.connector.connect(host=tokened.bddurl,
                                         database='market_datas',
                                         user=tokened.bdduserjuwl,
                                         password=tokened.bddpassjuwl)

    # on récupère la table qui contient les données d'analyse
    sql_select_Query = "SELECT * FROM `market_indics`" # WHERE `act_date` ='%s'" % datejour
    cursor = connection.cursor()
    cursor.execute(sql_select_Query)
    raw_toana = cursor.fetchall()

    #on définit la dataframe des données à analyser

    dfi = pd.DataFrame(raw_toana,columns=["Prim_key", "act_name", "act_isin", "date", "mk_value", "mma10", "mma20", "mma50", "mma100","mma200", "macd","bollinger_inf","bollinger_sup","signaleuh"])
    dfi.set_index(['act_name'], inplace=True)
    df_ex = dfi.loc[str(action_name), :]
    mk_value = df_ex["mk_value"].tolist()
    mk_time = df_ex["date"].tolist()
    prim_key = df_ex["Prim_key"].tolist()
    act_isin = df_ex["act_isin"].tolist()
    mma10 = df_ex["mma10"].tolist()
    mma20 = df_ex["mma20"].tolist()
    mma50 = df_ex["mma50"].tolist()
    mma100 = df_ex["mma100"].tolist()
    mma200 = df_ex["mma200"].tolist()
    bol_inf = df_ex["bollinger_inf"].tolist()
    bol_sup = df_ex["bollinger_sup"].tolist()
    macd = df_ex["macd"].tolist()
    signaleuh = df_ex["signaleuh"].tolist()

    return mma10,mma20,mma50,mma100,mma200,bol_inf,bol_sup,macd,signaleuh,mk_time, mk_value

mma10,mma20,mma50,mma100,mma200,bol_inf,bol_sup,macd,signaleuh,mk_time,mk_value = etude("Total")

#signaux acheteurs mma10 / mma20

dates_achat_mma10_mma20 = intersection_hausse(np.array(mma10),np.array(mma20),np.array(mk_time))
dates_achat_mma20_mma50 = intersection_hausse(np.array(mma20),np.array(mma50),np.array(mk_time))
dates_achat_mma50_mma100 = intersection_hausse(np.array(mma50),np.array(mma100),np.array(mk_time))
dates_achat_mma100_mma200 = intersection_hausse(np.array(mma100),np.array(mma200),np.array(mk_time))
dates_achat_bol_inf = intersection_hausse(np.array(mk_value),np.array(bol_inf),np.array(mk_time))
# dates_achat_macd_signal = intersection_hausse(np.array(signaleuh),np.array(macd),np.array(mk_time))
print(dates_achat_bol_inf)
datedujour = today.strftime("%y/%m/%d").replace('/', '-')

dates_indicateurs = [dates_achat_mma10_mma20, dates_achat_mma20_mma50, dates_achat_mma50_mma100, dates_achat_mma100_mma200, dates_achat_bol_inf]

def sumupachat_oftheday(date):
    indicateur_hausse = []
    for element in dates_indicateurs:
        cond = date in element
        indicateur_hausse.append(cond)
    return indicateur_hausse, sum(indicateur_hausse)

    # if date in dates_achat_mma10_mma20:
    #     #     indicateur_hausse =+1
    #     #     print("signal haussier court terme")
    #     # elif date in dates_achat_mma20_mma50:
    #     #     indicateur_hausse =+1
    #     #     print("signal haussier court et moyen terme")
    #     # elif date in dates_achat_mma50_mma100:
    #     #     indicateur_hausse =+1
    #     #     print("signal haussier moyen terme")
    #     # elif date in dates_achat_mma100_mma200:
    #     #     indicateur_hausse =+1
    #     #     print("signal haussier long terme")
    #     # elif date in dates_achat_bol_inf:
    #     #     indicateur_hausse =+1
    #     #     print("signal haussier fort bollinger")
    #     # elif date in dates_achat_macd_signal:
    #     #     indicateur_hausse =+1
    #     #     print("signal haussier très court terme")


print(sumupachat_oftheday("20-03-06"))