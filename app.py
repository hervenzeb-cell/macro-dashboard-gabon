import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(layout="wide")

st.title("📊 ANPI – Dashboard Macroéconomique & Attractivité Investissement")

# -------------------------
# CONFIGURATION
# -------------------------

countries = {
    "Gabon": "GAB",
    "Cameroun": "CMR",
    "Congo": "COG",
    "Tchad": "TCD",
    "Guinée Équatoriale": "GNQ",
    "RCA": "CAF"
}

indicators = {
    "Croissance PIB (%)": "NY.GDP.MKTP.KD.ZG",
    "Inflation (%)": "FP.CPI.TOTL.ZG",
    "Dette publique (% PIB)": "GC.DOD.TOTL.GD.ZS",
    "IDE (% PIB)": "BX.KLT.DINV.WD.GD.ZS"
}

# -------------------------
# SIDEBAR
# -------------------------

st.sidebar.header("Paramètres")

selected_countries = st.sidebar.multiselect(
    "Choisir pays CEMAC",
    list(countries.keys()),
    default=["Gabon", "Cameroun"]
)

selected_indicator = st.sidebar.selectbox(
    "Choisir indicateur",
    list(indicators.keys())
)

indicator_code = indicators[selected_indicator]

# -------------------------
# FONCTION RÉCUPÉRATION DONNÉES
# -------------------------

def get_data(country_code, indicator_code):
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}?format=json"
    response = requests.get(url)
    data = response.json()
    
    if len(data) > 1:
        df = pd.DataFrame(data[1])
        df = df[['date', 'value']].dropna()
        df['date'] = df['date'].astype(int)
        df = df.sort_values('date')
        return df
    else:
        return None

# -------------------------
# AFFICHAGE COMPARATIF
# -------------------------

df_all = pd.DataFrame()

for country in selected_countries:
    df = get_data(countries[country], indicator_code)
    if df is not None:
        df['Pays'] = country
        df_all = pd.concat([df_all, df])

if not df_all.empty:
    fig = px.line(df_all, x="date", y="value", color="Pays",
                  title=f"{selected_indicator} - Comparaison CEMAC")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Données non disponibles")

# -------------------------
# MODULE ATTRACTIVITÉ INVESTISSEMENT
# -------------------------

st.header("📊 Indice Stratégique ANPI")

def get_latest_value(country_code, indicator):
    df = get_data(country_code, indicator)
    if df is not None and not df.empty:
        return df.iloc[-1]["value"]
    return None

def strategic_index(country_code):
    gdp = get_latest_value(country_code, indicators["Croissance PIB (%)"])
    inflation = get_latest_value(country_code, indicators["Inflation (%)"])
    debt = get_latest_value(country_code, indicators["Dette publique (% PIB)"])
    fdi = get_latest_value(country_code, indicators["IDE (% PIB)"])
    
    if None in [gdp, inflation, debt, fdi]:
        return None
    
    score = (
        (gdp * 0.3) +
        ((10 - inflation) * 0.15) +
        ((100 - debt) * 0.3) +
        (fdi * 0.25)
    )
    
    return round(score, 2)

for country in selected_countries:
    index_score = strategic_index(countries[country])
    
    if index_score is not None:
        if index_score > 50:
            signal = "🟢 Investissement Favorable"
        elif index_score > 30:
            signal = "🟠 Environnement Sous Surveillance"
        else:
            signal = "🔴 Risque Macroéconomique Élevé"
        
        st.metric(label=f"{country} - Indice ANPI", value=index_score)
        st.write(signal)
    else:
        st.write(f"{country} : Données insuffisantes")
        
st.header("📉 Projection Croissance PIB (Tendance)")

import numpy as np

for country in selected_countries:
    df = get_data(countries[country], indicators["Croissance PIB (%)"])
    
    if df is not None and len(df) > 5:
        x = df['date'].values
        y = df['value'].values
        
        coeffs = np.polyfit(x, y, 1)
        trend = np.poly1d(coeffs)
        
        future_years = np.array([x[-1]+1, x[-1]+2, x[-1]+3])
        future_values = trend(future_years)
        
        projection_df = pd.DataFrame({
            "Année": future_years,
            "Projection Croissance (%)": future_values
        })
        
        st.subheader(f"{country}")
        st.dataframe(projection_df)
