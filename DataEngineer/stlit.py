import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk


def loadData():
  df = pd.read_csv('data.csv')
  df['latitude'] = [float(i.split(',')[1]) for i in df['coords']]
  df['longitude'] = [float(i.split(',')[0]) for i in df['coords']]
  df = df.drop(columns=['coords'])
  return df

def refresh():
  loadData()
  st.rerun()

df = loadData()

@st.cache_data
def createGraph(df):
  Layer = pdk.Layer(
    "ScatterplotLayer",
    df,
    get_position=['longitude', 'latitude'],
    get_color=[0, 255, 0, 160],
    get_radius=500,
    opacity=0.8,
    pickable=True
  )
  View_state = pdk.ViewState(
    longitude=df.longitude.mean(),
    latitude=df.latitude.mean(),
    zoom = 10
  )
  return pdk.Deck(layers=[Layer], initial_view_state=View_state)

def p():
  print("HELLO")

map = createGraph(df)
st.write(df.shape[0])
st.pydeck_chart(map)
st.button(label="🔄 Refresh", on_click=loadData)

