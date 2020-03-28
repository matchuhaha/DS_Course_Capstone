#!/usr/bin/env python
# coding: utf-8

# In[12]:


get_ipython().system('pip install bs4')
get_ipython().system('pip install beautifulsoup4 ')
get_ipython().system('python3 -m pip install lxml')
get_ipython().system('pip install lxml')

import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import os
from sklearn.cluster import KMeans
import folium  
import matplotlib.cm as cm
import matplotlib.colors as colors


print('Libraries imported.')


# In[13]:


List_url='https://en.wikipedia.org/w/index.php?title=List_of_postal_codes_of_Canada:_M&oldid=890001695'
source = requests.get(List_url).text


# In[18]:


soup = BeautifulSoup(source, 'html.parser')
table=soup.find('table')
column_names=['Postalcode','Borough','Neighborhood']
df = pd.DataFrame(columns=column_names)


# In[19]:


for tr_cell in table.find_all('tr'):
    row_data=[]
    for td_cell in tr_cell.find_all('td'):
        row_data.append(td_cell.text.strip())
    if len(row_data)==3:
        df.loc[len(df)] = row_data
        df.head()


# In[20]:


df=df[df['Borough']!='Not assigned']


# In[21]:


df[df['Neighborhood']=='Not assigned']=df['Borough']


# In[22]:


df.head()


# In[23]:


temp_df=df.groupby('Postalcode')['Neighborhood'].apply(lambda x: "%s" % ', '.join(x))
temp_df=temp_df.reset_index(drop=False)
temp_df.rename(columns={'Neighborhood':'Neighborhood_joined'},inplace=True)


# In[24]:


df_merge = pd.merge(df, temp_df, on='Postalcode')


# In[25]:


df_merge.drop(['Neighborhood'],axis=1,inplace=True)


# In[26]:


df_merge.drop_duplicates(inplace=True)


# In[27]:


df_merge.rename(columns={'Neighborhood_joined':'Neighborhood'},inplace=True)


# In[28]:


df_merge.head()


# In[29]:


df_merge.shape


# In[30]:


def get_geocode(postal_code):
    # initialize your variable to None
    lat_lng_coords = None
    while(lat_lng_coords is None):
        g = geocoder.google('{}, Toronto, Ontario'.format(postal_code))
        lat_lng_coords = g.latlng
    latitude = lat_lng_coords[0]
    longitude = lat_lng_coords[1]
    return latitude,longitude


# In[31]:


geo_df=pd.read_csv('http://cocl.us/Geospatial_data')


# In[32]:


geo_df.head()


# In[33]:


geo_df.rename(columns={'Postal Code':'Postalcode'},inplace=True)
geo_merged = pd.merge(geo_df, df_merge, on='Postalcode')


# In[34]:


geo_merged.head()


# In[35]:


geo_data=geo_merged[['Postalcode','Borough','Neighborhood','Latitude','Longitude']]
geo_data.head()


# In[42]:


toronto_data=geo_data[geo_data['Borough'].str.contains("Toronto")]
toronto_data.head()


# In[37]:


CLIENT_ID = 'IPP0TMLXT15LWBBPZGLW2X5V4VNDPDQTNECXQXTAWABPKJYF' # your Foursquare ID
CLIENT_SECRET = 'KBWDEYC43BZWBHGDB2ODGOPCL5O3LDGXT4MKOWLQCAV4K3RE' # your Foursquare Secret
VERSION = '20180604'


# In[38]:


def getNearbyVenues(names, latitudes, longitudes):
    radius=500
    LIMIT=100
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)
            
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighborhood', 
                  'Neighborhood Latitude', 
                  'Neighborhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)


# In[39]:


toronto_venues = getNearbyVenues(names=toronto_data['Neighborhood'],
                                   latitudes=toronto_data['Latitude'],
                                   longitudes=toronto_data['Longitude']
                                  )


# In[40]:


toronto_venues.head()


# In[ ]:




