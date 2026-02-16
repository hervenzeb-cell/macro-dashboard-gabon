import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(layout="wide")

st.title("📊 Dashboard Macroéconomique - Gabon & CEMAC")

# Liste pays CEMAC
countries = {
    "Gabon": "GAB",
    "Cameroun": "CMR",
    "Congo": "COG",
    "Tchad": "TCD",
    "Guinée Équatoriale": "GNQ",
    "RCA": "CAF"
}

# Indicateurs Banque mondiale
indicators = {
    "Croissance PIB (%)": "NY.GDP.MKTP.KD.ZG",
    "Inflation (%)": "FP.CPI.TOTL.ZG",
    "Dette publique (% PIB)": "GC.DOD.TOTL.GD.ZS",
    "IDE (% PIB)": "BX.KLT.DINV.WD.GD.ZS"
}

country_name = st.selectbox("Sélectionnez un pays", list(countries.keys()))
indicator_name = st.selectbox("Sélectionnez un indicateur", list(indicators.keys()))

country_code = countries[country_name]
indicator_code = indicators[indicator_name]

url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}?format=json"

response = requests.get(url)
data = response.json()

if len(data) > 1:
    df = pd.DataFrame(data[1])
    df = df[['date', 'value']].dropna()
    df['date'] = df['date'].astype(int)
    df = df.sort_values('date')

    fig = px.line(df, x="date", y="value", title=f"{indicator_name} - {country_name}")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df.tail(10))

else:
    st.error("Données non disponibles.")
