import streamlit as st
import pandas as pd
from pymongo import MongoClient
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import plotly.express as px

# Conexión a MongoDB
client = MongoClient("mongodb://mongodb:27017/")
db = client["ProjectETL"]

st.set_page_config(layout="wide")
st.title("Environmental Data Dashboard")

# --- COVID: Línea temporal ---
st.header("COVID-19 Global Trends (Processed Data)")
covid_data = list(db["processed_covid"].find())

if covid_data:
    covid_df = pd.DataFrame(covid_data)
    covid_df["date"] = pd.to_datetime(covid_df["date"])
    covid_df.sort_values("date", inplace=True)

    fig = px.line(
        covid_df,
        x="date",
        y=["cases", "deaths", "recovered"],
        title="COVID-19 Cases Over Time"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data available in processed_covid collection.")

# --- POLLUTION: Histograma ---
st.header("Air Pollution Levels")
pollution_data = list(db["processed_pollution"].find())

if pollution_data:
    pollution_df = pd.DataFrame(pollution_data)
    pollutant_selected = st.selectbox("Select pollutant type:", pollution_df["pollutant"].dropna().unique())

    filtered = pollution_df[pollution_df["pollutant"] == pollutant_selected]

    fig2 = px.histogram(
        filtered,
        x="value",
        nbins=30,
        title=f"Pollution Value Distribution for {pollutant_selected}"
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("No data available in processed_pollution collection.")

# --- WATER: Nube de palabras ---
st.header("Water Monitoring Site Mentions (Raw Data)")

water_data = list(db["raw_water"].find())
if water_data:
    site_names = []
    for feature in water_data:
        props = feature.get("properties", {})
        site = props.get("monitoring_location_id")
        if site:
            site_names.append(site)

    if site_names:
        text_blob = " ".join(site_names)
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_blob)

        st.subheader("Word Cloud of Water Monitoring Sites")
        fig3, ax3 = plt.subplots()
        ax3.imshow(wordcloud, interpolation="bilinear")
        ax3.axis("off")
        st.pyplot(fig3)
    else:
        st.warning("No station names found in raw_water data.")
else:
    st.warning("No data available in raw_water collection.")

