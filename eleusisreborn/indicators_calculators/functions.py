import pandas as pd
import mysql.connector
import time
import math
import requests
import sys, os
import numpy as np

#separate func

def bollinger_lowerband(coursfermeture, Ndays, num_of_std):
    rolling_mean = coursfermeture.rolling(Ndays).mean()
    # print("rolling_mean :\n",rolling_mean)
    rolling_std = coursfermeture.rolling(Ndays).std()
    # print("rolling_std:\n",rolling_std)
    lower_band2 = rolling_mean - (rolling_std * num_of_std)
    # print("lower_band:\n",lower_band)
    l_lower_band = aplatliste(pd.DataFrame(lower_band2.values).fillna(0).values.tolist())
    return l_lower_band

def bollinger_upperband(coursfermeture,Ndays, num_of_std):

    rolling_mean = coursfermeture.rolling(Ndays).mean()
    #print("rolling_mean :\n",rolling_mean)
    rolling_std  = coursfermeture.rolling(Ndays).std()
    #print("rolling_std:\n",rolling_std)
    upper_band2 = rolling_mean + (rolling_std*num_of_std)
    #print("upper_band:\n",upper_band)
    l_upper_band = aplatliste(pd.DataFrame(upper_band2.values).fillna(0).values.tolist())
    return l_upper_band

def moyenne_mobile(list, Ndays) :
    return [ 0*nj for nj in range(0,Ndays)]+[(np.sum(list[(jour-Ndays+1):jour+1]))/len(list[(jour-Ndays+1):jour+1]) for jour in range (Ndays-1, len(list)-1)]


def macd(df):

    exp1 = df.ewm(span=12, adjust=False).mean()
    # print(exp1)
    exp2 = df.ewm(span=26, adjust=False).mean()
    macdvalue = exp1 - exp2
    signal = macdvalue.ewm(span=9, adjust=False).mean()
    return macdvalue,signal

def aplatliste(L):
    # transforme un arbre (liste de listes...) en une liste à 1 seul niveau
    R = []
    for elem in L:
        if isinstance(elem, (list, tuple)):
            R.extend(aplatliste(elem))
        else:
            R.append(elem)
    return R

#signal quand g passe au dessus de f, on met la mma basse en f et mma haute en g (signal haussier court terme)
def intersection_hausse(f_array,g_array,x_array):
    import numpy as np
    import matplotlib.pyplot as plt
    # plt.plot(x_array, f_array, '-')
    # plt.plot(x_array, g_array, '-')
    idx = np.argwhere(np.diff(np.sign(f_array - g_array)) < 0).reshape(-1)
    # plt.plot(x_array[idx], f_array[idx], 'ro')
    plt.show()
    return x_array[idx]

def intersection_baisse(f_array,g_array,x_array):
    import numpy as np
    import matplotlib.pyplot as plt
    # plt.plot(x_array, f_array, '-')
    # plt.plot(x_array, g_array, '-')
    idx = np.argwhere(np.diff(np.sign(f_array - g_array)) > 0).reshape(-1)
    # plt.plot(x_array[idx], f_array[idx], 'ro')
    plt.show()
    return x_array[idx]