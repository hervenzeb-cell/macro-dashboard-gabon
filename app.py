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

st.header("📈 Score Attractivité Investissement")

def calculate_score(country_code):
    gdp = get_data(country_code, indicators["Croissance PIB (%)"])
    debt = get_data(country_code, indicators["Dette publique (% PIB)"])
    fdi = get_data(country_code, indicators["IDE (% PIB)"])
    
    try:
        latest_gdp = gdp.iloc[-1]["value"]
        latest_debt = debt.iloc[-1]["value"]
        latest_fdi = fdi.iloc[-1]["value"]
        
        score = (latest_gdp * 0.4) + (latest_fdi * 0.3) - (latest_debt * 0.3)
        return round(score, 2)
    except:
        return None

for country in selected_countries:
    score = calculate_score(countries[country])
    
    if score is not None:
        if score > 5:
            color = "green"
            status = "🟢 Attractivité Forte"
        elif score > 0:
            color = "orange"
            status = "🟠 Attractivité Modérée"
        else:
            color = "red"
            status = "🔴 Attractivité Faible"
        
        st.metric(label=f"{country}", value=score)
        st.write(status)
    else:
        st.write(f"{country} : Données insuffisantes")

