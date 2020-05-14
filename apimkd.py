import os
import sys

import mysql.connector
import pandas as pd

sys.path.append(os.getcwd()+"\\src\\eleusisreborn\\tools\\")
import tokened

from datetime import date

today = date.today()



def starting(plage,action_studied):
    #on se connecte au serveur
    #SELECT * FROM `market_indics` WHERE `act_name` = 'Michelin' ORDER BY `date`  ASC LIMIT 10

    datejour = today.strftime("%y/%m/%d")
    datejour = datejour.replace('/', '-')
    # print(datejour)
    if action_studied == "L'oreal":
        action_studiedSQL = "L''oreal"
    else:
        action_studiedSQL = action_studied
    connection = mysql.connector.connect(host=tokened.bddurl,
                                         database='market_datas',
                                         user=tokened.bdduserjuwl,
                                         password=tokened.bddpassjuwl)
    # on récupère la table qui contient les données sources
    cursor2 = connection.cursor()
    sql_select_Query2 = "SELECT * FROM `market_indics` WHERE `act_name` = '%s'" %(action_studiedSQL)
    cursor2.execute(sql_select_Query2)
    plage_max = (len(cursor2.fetchall()))
    sql_select_Query = "SELECT * FROM `market_indics` WHERE `act_name` = '%s' ORDER BY `market_indics`.`date` DESC LIMIT %s" %(action_studiedSQL, plage)
    cursor = connection.cursor()
    cursor.execute(sql_select_Query)
    records = cursor.fetchall()
    dfi = pd.DataFrame(records,columns=["Prim_key", "act_name", "act_isin", "date", "mk_value", "mma10", "mma20", "mma50", "mma100","mma200", "macd","bollinger_inf","bollinger_sup","signaleuh"])
    dfi.set_index(['act_name'], inplace=True)
    dfi = dfi[::-1]
    df_ex = dfi.loc[str(action_studied), :]
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


    ##macd et signal
    mmaglobal = [mma10,mma20,mma50,mma100,mma200,bol_inf,bol_sup]
    for elt in mmaglobal:
        for n, i in enumerate(elt):
            if i == 0:
                elt[n] = "NaN"
    #     #print(mma100)
    plage = 4000
    return mk_value, mk_time, mma10, mma20, mma50, mma100, mma200, bol_inf, bol_sup, plage_max

#

def get_mkd_eleusis():
    table_init = pd.read_csv('http://eleusis-ig.com/mkd.csv', sep=";")
    table_init.set_index(["ISIN"], inplace=True)
    table_init.sort_index(level=["ISIN"], ascending=[True], inplace=True)
    table_ex = table_init.loc["FR0000130007",:]
    table_init.to_csv('out_eleusis_mkd.csv', sep=";")
    table_ex.to_csv('out_eleusis_mkd_select.csv', sep=";")
    print(table_ex.head())
    mk_value = table_ex["CLOSING"].tolist()
    mk_time = table_ex["TIMING"].tolist()
    return mk_value,mk_time

if __name__ == '__main__':
    starting(10,'Total')