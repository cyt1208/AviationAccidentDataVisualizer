#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import json
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import folium
from folium.plugins import HeatMap
import os

# In[2]:


df1 = pd.read_csv('Book1.csv', encoding='ISO-8859-1')

# In[3]:


df1 = df1.loc[df1['Country'] == 'United States']
df2 = df1[['Location']].copy()
df2.dropna()
new = df2["Location"].str.split(",", n=1, expand=True)
df2.drop(['Location'], axis=1)
df2["City"] = new[0]
df2["State"] = new[1]
df2["State"] = df2.State.values.astype(str)

# In[4]:


df2['InvestigationType'] = df1['InvestigationType']
df2['TotalFatalInjuries'] = df1['TotalFatalInjuries']
df2['TotalSeriousInjuries'] = df1['TotalSeriousInjuries']
df2['TotalUninjured'] = df1['TotalUninjured']
df2['TotalMinorInjuries'] = df1['TotalMinorInjuries']
df2['EventDate'] = df1['EventDate']
df2['Latitude'] = df1['Latitude']
df2['Longitude'] = df1['Longitude']
df2['AirportCode'] = df1['AirportCode']
df2['AircraftCategory'] = df1['AircraftCategory']
df2['Model'] = df1['Model']
df2['Make'] = df1['Make']
df2['BroadPhaseOfFlight'] = df1['BroadPhaseOfFlight']

# In[5]:


df1

# In[6]:


states = {
    ' AK': 'Alaska',
    ' AL': 'Alabama',
    ' AR': 'Arkansas',
    ' AS': 'American Samoa',
    ' AZ': 'Arizona',
    ' CA': 'California',
    ' CO': 'Colorado',
    ' CT': 'Connecticut',
    ' DC': 'District of Columbia',
    ' DE': 'Delaware',
    ' FL': 'Florida',
    ' GA': 'Georgia',
    ' GU': 'Guam',
    ' HI': 'Hawaii',
    ' IA': 'Iowa',
    ' ID': 'Idaho',
    ' IL': 'Illinois',
    ' IN': 'Indiana',
    ' KS': 'Kansas',
    ' KY': 'Kentucky',
    ' LA': 'Louisiana',
    ' MA': 'Massachusetts',
    ' MD': 'Maryland',
    ' ME': 'Maine',
    ' MI': 'Michigan',
    ' MN': 'Minnesota',
    ' MO': 'Missouri',
    ' MP': 'Northern Mariana Islands',
    ' MS': 'Mississippi',
    ' MT': 'Montana',
    ' NA': 'National',
    ' NC': 'North Carolina',
    ' ND': 'North Dakota',
    ' NE': 'Nebraska',
    ' NH': 'New Hampshire',
    ' NJ': 'New Jersey',
    ' NM': 'New Mexico',
    ' NV': 'Nevada',
    ' NY': 'New York',
    ' OH': 'Ohio',
    ' OK': 'Oklahoma',
    ' OR': 'Oregon',
    ' PA': 'Pennsylvania',
    ' PR': 'Puerto Rico',
    ' RI': 'Rhode Island',
    ' SC': 'South Carolina',
    ' SD': 'South Dakota',
    ' TN': 'Tennessee',
    ' TX': 'Texas',
    ' UT': 'Utah',
    ' VA': 'Virginia',
    ' VI': 'Virgin Islands',
    ' VT': 'Vermont',
    ' WA': 'Washington',
    ' WI': 'Wisconsin',
    ' WV': 'West Virginia',
    ' WY': 'Wyoming'
}


# In[7]:


def date_input(info_for_s):
    s = input(info_for_s)
    flag = True
    badinput = True
    while badinput:
        flag = True
        if len(s) != 8:
            print("Date entered is not valid (check length).")
            flag = False
        if flag:
            for ele in s:
                if ord(ele) < ord('0') or ord(ele) > ord('9'):
                    print("Date contains unacceptable char.")
                    flag = False
                    break
        if flag:
            badinput = False
            break
        s = input(info_for_s)
    return s


# In[8]:


def user_query_input(info_for_i, lst):
    bad_input = True
    user_input = input(info_for_i)
    while user_input not in lst:
        print("Input token not found. Please retry.")
        user_input = input(info_for_i)
    return user_input


# In[9]:


def user_query_input_multiple(info_for_i, lst):
    bad_input = True
    user_c = []
    total = lst
    user = user_query_input(info_for_i, total)
    user_c.append(user)
    cont = user_query_input("Continue? ", ["Y", "y", "N", "n"])
    while cont == "Y" or cont == "y":
        total.pop(total.index(user))
        user = user_query_input(info_for_i, total)
        user_c.append(user)
        cont = user_query_input("Continue? ", ["Y", "y", "N", "n"])
    return user_c


# In[10]:


def df_integrity_check(df):
    length = df.shape[0] - 1
    if not df.shape[0] or not df.shape[1]:
        raise ValueError("None entry/empty dataframe.")
    for ele in df.columns:
        for i in range(length):
            if type(df[ele][i]) != type(df[ele][i + 1]):
                raise TypeError("Input dataframe has bad data type.")

    if df.shape[1] == 1:
        print("Only one column found in dataframe. Continue with default index?")
        user = input("N for NO, ANY KEY for YES.")
        if user == "N" or "n":
            print("Session is ended.")
            return None
        else:
            df["order"] = range(df.shape[0])
            cols = df.columns.tolist()
            cols.insert(0, cols.pop(cols.index('order')))
            df = df.reindex(columns=cols)
    return df


# In[11]:


def map_by_states(df):
    print("Process and plot user queried data by states in US...")
    user_select = user_query_input(
        "From:[TotalFatalInjuries, TotalSeriousInjuries, TotalMinorInjuries, TotalUninjured, TotalAccidentNumber]",
        ["TotalFatalInjuries", "TotalSeriousInjuries", "TotalMinorInjuries", "TotalUninjured", "TotalAccidentNumber"])
    col_for_df = ["State"] + [user_select]
    df["TotalAccidentNumber"] = 1
    df2 = df[col_for_df]
    df2 = df2.dropna()
    df2 = df2.groupby(['State']).sum()
    length = df2.shape[0] - 1
    df2.reset_index(level=0, inplace=True)
    for i in range(length + 1):
        if df2["State"][i] in states:
            df2["State"][i] = states[df2["State"][i]]
        else:
            df2 = df2.drop([i])
    state_geo = os.path.join('usstates.json')
    m = folium.Map(location=[52, -100], zoom_start=2)
    for ele in col_for_df:
        if ele not in ["State"]:
            tag = ele
    m.choropleth(
        geo_data=state_geo,
        name='choropleth',
        data=df2,
        columns=['State', tag],
        key_on='feature.properties.name',
        fill_color='YlGn',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=tag
    )
    folium.LayerControl().add_to(m)
    return m


# In[12]:


def time_ranged_heat_map(df):
    print("Process and plot user queried data by location within selected time range or default time range.")
    user_select = user_query_input(
        "From:[TotalFatalInjuries, TotalSeriousInjuries, TotalMinorInjuries, TotalUninjured]",
        ["TotalFatalInjuries", "TotalSeriousInjuries", "TotalMinorInjuries", "TotalUninjured"])
    col_for_df = ["Latitude", "Longitude", "EventDate"] + [user_select]
    df2 = df[col_for_df]
    df2.dropna()
    start_date = date_input("Enter start date as YYYYMMDD.")
    end_date = date_input("Enter end date as YYYYMMDD.")
    df2["EventDate"] = pd.to_datetime(df2["EventDate"])
    df2.sort_values(by=["EventDate"])
    start_date = pd.to_datetime(start_date, format='%Y%m%d', errors='ignore')
    end_date = pd.to_datetime(end_date, format='%Y%m%d', errors='ignore')
    mask = (df2['EventDate'] > start_date) & (df2['EventDate'] <= end_date)
    df2 = df2.loc[mask]
    df2['Latitude'] = df2['Latitude'].astype(float)
    df2['Longitude'] = df2['Longitude'].astype(float)
    for ele in df2.columns:
        if ele not in ["Latitude", "Longitude", "EventDate"]:
            tag = ele
    df2[tag] = df2[tag].astype(float)
    df2 = df2.dropna()
    heat_data = [[row['Latitude'], row['Longitude']] for index, row in df2.iterrows()]
    map_hooray = folium.Map(location=[52, -100], zoom_start=2)
    HeatMap(heat_data, min_opacity=0.6, radius=3, blur=3, ).add_to(map_hooray)
    return map_hooray


# In[13]:


def linear_plot(df):
    df = df[["EventDate", "TotalFatalInjuries", "TotalSeriousInjuries", "TotalMinorInjuries", "TotalUninjured"]]
    df["TotalAccidentNumber"] = 1
    user_choice = user_query_input_multiple("Enter One Y-axis Element: ",
                                            ["TotalFatalInjuries", "TotalSeriousInjuries", "TotalMinorInjuries",
                                             "TotalUninjured", "TotalAccidentNumber"])
    dfcol = user_choice + ["EventDate"]
    df = df[dfcol]
    df = df.dropna()
    df["EventDate"] = pd.to_datetime(df["EventDate"])
    df['Year'] = df.EventDate.dt.year
    df = df.groupby(['Year']).sum()
    df.reset_index(level=0, inplace=True)
    df = df[6:]
    df.reset_index()
    ax = plt.gca()
    for ele in user_choice:
        df.plot(kind='line', x='Year', y=ele, ax=ax)

    ax.legend()
    plt.show()


# In[14]:


def bar_plot(df):
    user_xlabel = user_query_input(
        "Enter One X-axis Element: ['AirportCode', 'AircraftCategory', 'Model', 'Make','BroadPhaseOfFlight']",
        ['AirportCode', 'AircraftCategory', 'Model', 'Make', 'BroadPhaseOfFlight'])
    user_ylabel = user_query_input_multiple("Enter Multi Y-axis Element: ",
                                            ["TotalFatalInjuries", "TotalSeriousInjuries", "TotalMinorInjuries",
                                             "TotalUninjured", "TotalAccidentNumber"])

    if "TotalAccidentNumber" in user_ylabel:
        user_ylabel2 = [ele for ele in user_ylabel if ele != "TotalAccidentNumber"]
        dfcol = [user_xlabel] + user_ylabel2
        df = df[dfcol]
        df["TotalAccidentNumber"] = 1
    else:
        dfcol = [user_xlabel] + user_ylabel
        df = df[dfcol]
        df["TotalAccidentNumber"] = 1
    df = df.dropna()
    df = df.reset_index(drop=True)
    df = df.groupby([user_xlabel]).sum()
    df.reset_index(level=0, inplace=True)
    y_pos = np.arange(len(df[user_xlabel]))
    offset = 1 / len(df[user_ylabel])
    fig, ax = plt.subplots()
    print(df)
    for i in range(len(user_ylabel)):
        plt.bar(y_pos + i * offset, df[user_ylabel[i]] / df["TotalAccidentNumber"], width=offset)
    plt.xticks(y_pos, df[user_xlabel])
    plt.xticks(rotation=90)
    plt.ylabel("Ratio of TotalAccidentNumber")
    plt.title(user_xlabel)
    plt.legend(user_ylabel, loc='center left', bbox_to_anchor=(1, 0.5))


# In[15]:


time_ranged_heat_map(df2)

# In[16]:


map_by_states(df2)

# In[17]:


linear_plot(df2)

# In[18]:


bar_plot(df2)


# In[19]:


def pie_plot(df):
    user_xlabel = user_query_input(
        "Enter One Element: ['AirportCode', 'AircraftCategory', 'Model', 'Make','BroadPhaseOfFlight']",
        ['AirportCode', 'AircraftCategory', 'Model', 'Make', 'BroadPhaseOfFlight'])
    user_ylabel = user_query_input("Enter Statistical target: ",
                                   ["TotalFatalInjuries", "TotalSeriousInjuries", "TotalMinorInjuries",
                                    "TotalUninjured", "TotalAccidentNumber"])
    if user_ylabel == "TotalAccidentNumber":
        dfcol = [user_xlabel]
        df = df[dfcol]
        df["TotalAccidentNumber"] = 1
    else:
        dfcol = [user_xlabel] + [user_ylabel]
        df = df[dfcol]
        df["TotalAccidentNumber"] = 1

    df = df.dropna()
    df = df.reset_index(drop=True)
    df = df.groupby([user_xlabel]).sum()
    df.reset_index(level=0, inplace=True)
    explode = [0.11 * i for i in range(len(df[user_xlabel]))]

    df = df.sort_values(by=[user_ylabel], ascending=False)
    print(df)
    df = df.reset_index(drop=True)
    if len(df[user_xlabel]) > 3:
        lb = ['' for i in range(len(df[user_xlabel]))]
        lb[0] = df[user_xlabel][0]
        lb[1] = df[user_xlabel][1]
        lb[2] = df[user_xlabel][2]
    else:
        lb = df[user_xlabel]
    fig, ax = plt.subplots()
    wedges, texts, _ = ax.pie(df[user_ylabel], explode=explode, labels=lb, autopct='%1.1f%%',
                              shadow=True, startangle=90)

    ax.legend(wedges, df[user_xlabel],
              title="Phase of Flight",
              bbox_to_anchor=(1, 0), loc="upper left", )


# In[26]:


pie_plot(df2)

# In[21]:


user_select = user_query_input(
    "From:[TotalFatalInjuries, TotalSeriousInjuries, TotalMinorInjuries, TotalUninjured, TotalAccidentNumber]",
    ["TotalFatalInjuries", "TotalSeriousInjuries", "TotalMinorInjuries", "TotalUninjured", "TotalAccidentNumber"])

# In[22]:


col_for_df = ["State"] + [user_select]

# In[23]:


df2["TotalAccidentNumber"] = 1

# In[24]:


df3 = df2[col_for_df]

# In[25]:


df3 = df3.groupby(['State']).sum()
df3[df3.State not in states]

# In[ ]:


df3 = df3.groupby(['State']).sum()
df3[df3.State not in states]

# In[ ]:


# In[ ]:
