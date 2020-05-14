def bollinger_lowerband(coursfermeture, Ndays, num_of_std):
    rolling_mean = coursfermeture.rolling(Ndays).mean()
    # print("rolling_mean :\n",rolling_mean)
    rolling_std = coursfermeture.rolling(Ndays).std()
    # print("rolling_std:\n",rolling_std)
    lower_band2 = rolling_mean - (rolling_std * num_of_std)
    # print("lower_band:\n",lower_band)
    l_lower_band = lower_band2.values.tolist()
    return l_lower_band

def bollinger_upperband(coursfermeture,Ndays, num_of_std):

    rolling_mean = coursfermeture.rolling(Ndays).mean()
    #print("rolling_mean :\n",rolling_mean)
    rolling_std  = coursfermeture.rolling(Ndays).std()
    #print("rolling_std:\n",rolling_std)
    upper_band2 = rolling_mean + (rolling_std*num_of_std)
    #print("upper_band:\n",upper_band)
    l_upper_band = upper_band2.values.tolist()
    return l_upper_band