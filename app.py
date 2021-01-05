import streamlit as st
import pandas as pd
import lxml
import altair as alt

st.title ("How do Governments do?")

st.write ("In this page, we show how do different government styles perform in terms of provividing its people.")
url_democracy_index = "https://en.wikipedia.org/wiki/Democracy_Index"
url_socialprogress_index = "https://en.wikipedia.org/wiki/Social_Progress_Index"
url_population = "https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)"

# @st.cache
list_democracy_index = pd.read_html(url_democracy_index, header=0)
list_socialprogress_index = pd.read_html(url_socialprogress_index, header=1)
list_population = pd.read_html(url_population)

df_demo = list_democracy_index[2]
df_demo.drop(df_demo[df_demo['Rank']=='Rank'].index,inplace=True)
df_soc = list_socialprogress_index[0]
df_pop = list_population[3]

column_type = {'Rank': int,
               'Score': float,
               'Electoral processand pluralism': float,
               'Functio­ning ofgovern­ment': float,
               'Politicalpartici­pation': float,
               'Politicalculture': float,
               'Civilliberties': float
              }
df_demo = df_demo.astype(column_type)
df_demo = df_demo.rename(columns = {"Score": "Democracy_Score"})
df_soc['Country'] = df_soc['Country'].str.replace(r"\[.*\]","")
df_demo = df_demo.rename(columns = {"Region[n 1]": "Region"})
df_soc = df_soc.rename(columns = {"Score": "SocialProgress_Score"})
df_pop = df_pop.rename(columns = {"Country/Territory": "Country",
                                 "Population(1 July 2019)": "Population"})
df_pop = df_pop[['Country','Population']]
df_pop['Country'] = df_pop['Country'].str.replace(r"\[.*\]","")

df_combined = df_demo.merge(
    df_soc, on = 'Country', how = 'left')[[
    'Country','Democracy_Score','SocialProgress_Score', 'Regimetype', 'Region']]
df_combined.dropna(subset=['SocialProgress_Score'], inplace = True)
df_combined = df_combined.merge(df_pop, on = 'Country', how = 'left')

choice = st.multiselect('Select region', ("Asia & Australasia", "Eastern Europe", "Latin America", "Middle East and North Africa", "North America", "Sub-Saharan Africa", "Western Europe"), key = '1')


df_combined = df_combined[df_combined['Region'].isin(choice)]

# Configure the options common to all layers
brush = alt.selection(type='interval')
base = alt.Chart(df_combined).add_selection(brush)

points = alt.Chart(df_combined).mark_circle().encode(
    alt.X('Democracy_Score', title='Democracy Index'),
    alt.Y('SocialProgress_Score', title = 'Social Progress Index',
          scale=alt.Scale(domain = (30,100))),
    color=('Region:N'),size = 'Population')

# Configure the ticks
tick_axis = alt.Axis(labels=False, domain=False, ticks=False)

x_ticks = base.mark_tick().encode(
    alt.X('Democracy_Score', title = '', axis=tick_axis),
    alt.Y('Region', title = '', axis=tick_axis),
    color=alt.condition(brush, 'Region', alt.value('lightgrey'))
)

y_ticks = base.mark_tick().encode(
    alt.X('Region', title='', axis=tick_axis),
    alt.Y('SocialProgress_Score', title = '', axis=tick_axis),
    color=alt.condition(brush, 'Region', alt.value('lightgrey'))
)

out = y_ticks | (points & x_ticks)

st.write(out)