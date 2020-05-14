import os
import sys

import mysql.connector
import pandas as pd

from eleusisreborn.indicators_calculators.functions import moyenne_mobile, bollinger_lowerband, bollinger_upperband, \
    macd

import tokened
sys.path.append(os.getcwd() + "\\src\\eleusisreborn\\tools\\")

from datetime import date

today = date.today()

def starting_from_begining():
    # on se connecte au serveur

    datejour = today.strftime("%y/%m/%d")
    datejour = datejour.replace('/', '-')

    connection = mysql.connector.connect(host=tokened.bddurl,
                                         database='market_datas',
                                         user=tokened.bdduserjuwl,
                                         password=tokened.bddpassjuwl)
    # on récupère la table qui contient les données sources
    sql_select_Query = "SELECT * FROM `market_histo`"  # WHERE `act_date` ='%s'" % datejour
    cursor = connection.cursor()
    cursor.execute(sql_select_Query)
    records = cursor.fetchall()
    if records == []:
        print('Nothing today')
    else:
        # on crée la dataframe correspondante
        dfi = pd.DataFrame(records, columns=["Prim_key", "Nom_Action", "Code_ABBR", "Code_ISIN", "Date", "Ouverture",
                                             "Fermeture", "Volume"])
        dfi.to_csv('out.csv', sep=";")
        act_name_unique = dfi.Nom_Action.unique()
        dfi.set_index(['Nom_Action'], inplace=True)
        for elt in act_name_unique:
            df_exe = dfi.loc[str(elt), :]
            nb_jour = df_exe.shape[0]
            df_ex = df_exe.iloc[:nb_jour, :]
            dfi.to_csv(os.getcwd() + f'\\eleusisreborn\\tools\\svg_csv\\{today} - out_juwl.csv', sep=";")
            df_ex.to_csv('out_juwl_mkd_select.csv', sep=";")
            mk_value = df_ex["Fermeture"].tolist()
            mk_time = df_ex["Date"].tolist()
            prim_key = df_ex["Prim_key"].tolist()
            act_isin = df_ex["Code_ISIN"].tolist()
            mma10 = moyenne_mobile(df_ex["Fermeture"], 10)
            mma20 = moyenne_mobile(df_ex["Fermeture"], 20)
            mma50 = moyenne_mobile(df_ex["Fermeture"], 50)
            mma100 = moyenne_mobile(df_ex["Fermeture"], 100)
            mma200 = moyenne_mobile(df_ex["Fermeture"], 200)
            bol_inf = bollinger_lowerband(df_ex["Fermeture"], 20, 2)
            bol_sup = bollinger_upperband(df_ex["Fermeture"], 20, 2)
            macdi = macd(df_ex["Fermeture"])[0]
            signal = macd(df_ex["Fermeture"])[1]
            for i in range(0, len(prim_key)):
                addsql_from_begining(prim_key[i], elt, act_isin[i], mk_time[i], mk_value[i], mma10[i], mma20[i],
                                     mma50[i], mma100[i], mma200[i], macdi[i], bol_inf[i], bol_sup[i], signal[i])
            # return mk_value, mk_time, mma10, mma20, mma50, mma100, mma200, bol_inf, bol_sup


totaladd = 0


def addsql_from_begining(a, b, c, d, e, f, g, h, i, j, k, l, m, n):
    global totaladd
    try:
        connection = mysql.connector.connect(host=tokened.bddurl,
                                             database='market_datas',
                                             user=tokened.bdduserfelvys,
                                             password=tokened.bddpassfelvys)
        records_to_insert = [(a, b, c, d, e, f, g, h, i, j, k, l, m, n, a, b, c, d, e, f, g, h, i, j, k, l, m, n)]
        sql_insert_query = """ INSERT INTO market_indics (Prim_key, act_name, act_isin, date, mk_value, mma10, mma20, mma50, mma100, mma200, macd, bollinger_inf, bollinger_sup, signaleuh) 
	                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s, %s) ON DUPLICATE KEY UPDATE Prim_key = %s, act_name=%s, act_isin=%s, date=%s, mk_value=%s, mma10=%s, mma20=%s, mma50=%s, mma100=%s,
	                       mma200=%s, macd=%s, bollinger_inf=%s, bollinger_sup=%s, signaleuh=%s"""""
        cursor = connection.cursor(prepared=True)
        result = cursor.executemany(sql_insert_query, records_to_insert)
        connection.commit()
        totaladd += cursor.rowcount
        print(cursor.rowcount, "Record inserted successfully into market_indics table")
    except mysql.connector.Error as error:
        print("Failed inserting record into market_indics table {}".format(error))
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            # print("connection is closed")
        print(str(totaladd) + " Record inserted successfully into market_indics table")


if __name__ == '__main__':
    starting_from_begining()
