import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import date
from typing import List, Optional
from pydantic import BaseModel

# -------------------------------
# MODELLI DATI SEMPLICI
# -------------------------------
class Applicant(BaseModel):
    name: str
    country: Optional[str] = None

class Patent(BaseModel):
    id: str
    title: str
    abstract: str
    filing_date: Optional[date] = None
    inventors: List[str] = []
    applicants: List[Applicant] = []
    cpc_classes: List[str] = []
    material_category: str

# -------------------------------
# DATASET DEMO (funziona subito)
# -------------------------------
def load_demo_patents():
    return [
        Patent(
            id="EP1234567A1",
            title="Processo di pressofusione per leghe di Zama",
            abstract="Metodo per pressofusione di zinco con alta resistenza",
            filing_date=date(2021,3,15),
            inventors=["Rossi M."],
            applicants=[Applicant(name="Fonderie S.p.A.", country="IT")],
            cpc_classes=["B22D17/22"],
            material_category="Zama"
        ),
        Patent(
            id="US2022123456A1",
            title="Aluminium die casting method for automotive",
            abstract="High-pressure die casting of aluminium alloys",
            filing_date=date(2020,6,20),
            inventors=["Johnson P."],
            applicants=[Applicant(name="AutoTech GmbH", country="DE")],
            cpc_classes=["B22D17/20"],
            material_category="Alluminio"
        ),
        Patent(
            id="WO2023123456A1",
            title="Magnesium alloy die casting with reduced porosity",
            abstract="Process for magnesium alloys minimizing gas porosity",
            filing_date=date(2022,9,1),
            inventors=["Chen W."],
            applicants=[Applicant(name="Magnesium Research Inst.", country="CN")],
            cpc_classes=["B22D17/00"],
            material_category="Magnesio"
        ),
        Patent(
            id="EP9876543B1",
            title="Zinc alloy with improved fluidity for die casting",
            abstract="Composition and method for zamak alloys",
            filing_date=date(2019,5,5),
            inventors=["Bianchi L."],
            applicants=[Applicant(name="Zamak Corp", country="IT")],
            cpc_classes=["C22C18/00"],
            material_category="Zama"
        ),
        Patent(
            id="DE102021123456",
            title="Aluminium die casting tool with cooling channels",
            abstract="Tool design for high-pressure die casting",
            filing_date=date(2021,11,11),
            inventors=["Schmidt H."],
            applicants=[Applicant(name="Bayerische Motoren Werke", country="DE")],
            cpc_classes=["B22D17/22"],
            material_category="Alluminio"
        ),
        Patent(
            id="JP2023123456",
            title="Magnesium casting method for electronics",
            abstract="Thin-wall magnesium die casting",
            filing_date=date(2023,1,15),
            inventors=["Tanaka K."],
            applicants=[Applicant(name="Toyota Jidosha", country="JP")],
            cpc_classes=["B22D17/00"],
            material_category="Magnesio"
        )
    ]

# -------------------------------
# FUNZIONI DI ANALISI
# -------------------------------
def yearly_counts(patents):
    data = []
    for p in patents:
        if p.filing_date:
            data.append({"year": p.filing_date.year, "material": p.material_category})
    df = pd.DataFrame(data)
    if df.empty:
        return pd.DataFrame(columns=["year","material","count"])
    return df.groupby(["year","material"]).size().reset_index(name="count")

def top_applicants(patents, n=10):
    apps = []
    for p in patents:
        for a in p.applicants:
            apps.append({"name": a.name, "material": p.material_category})
    df = pd.DataFrame(apps)
    if df.empty:
        return pd.DataFrame()
    top = df.groupby("name").size().reset_index(name="total").sort_values("total", ascending=False).head(n)
    return top

# -------------------------------
# CONFIGURAZIONE STREAMLIT
# -------------------------------
st.set_page_config(page_title="Die Casting Patent Analytics", page_icon="🏭", layout="wide")

# Carica dati
if "patents" not in st.session_state:
    st.session_state.patents = load_demo_patents()

patents = st.session_state.patents

# Sidebar filtri
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/patent.png", width=60)
    st.title("🔍 Filtri")
    materials = st.multiselect("Materiale", ["Zama","Alluminio","Magnesio"], default=["Zama","Alluminio","Magnesio"])
    years = st.slider("Anni", 2015, 2025, (2019, 2023), step=1)
    refresh = st.button("🔄 Reset")

if refresh:
    st.session_state.patents = load_demo_patents()
    st.rerun()

# Applica filtri
filtered = [p for p in patents if p.material_category in materials and p.filing_date and years[0] <= p.filing_date.year <= years[1]]
st.sidebar.write(f"**Brevetti visualizzati:** {len(filtered)}")

# Menu navigazione
menu = st.sidebar.radio("Vai a:", ["Dashboard", "Ricerca", "Trend", "Competitor"])

# -------------------------------
# DASHBOARD
# -------------------------------
if menu == "Dashboard":
    st.title("📊 Dashboard Panoramica")
    if not filtered:
        st.warning("Nessun brevetto con i filtri selezionati.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Totale", len(filtered))
        col2.metric("Zama", sum(1 for p in filtered if p.material_category=="Zama"))
        col3.metric("Alluminio", sum(1 for p in filtered if p.material_category=="Alluminio"))
        st.metric("Magnesio", sum(1 for p in filtered if p.material_category=="Magnesio"))

        yearly = yearly_counts(filtered)
        if not yearly.empty:
            fig = px.line(yearly, x="year", y="count", color="material", markers=True, title="Andamento depositi")
            st.plotly_chart(fig, use_container_width=True)

        top = top_applicants(filtered, n=8)
        if not top.empty:
            fig2 = px.bar(top, x="total", y="name", orientation="h", title="Top depositanti")
            st.plotly_chart(fig2, use_container_width=True)

# -------------------------------
# RICERCA
# -------------------------------
elif menu == "Ricerca":
    st.title("🔎 Ricerca Brevetti")
    if not filtered:
        st.warning("Nessun brevetto.")
    else:
        df = pd.DataFrame([{
            "ID": p.id,
            "Titolo": p.title,
            "Abstract": p.abstract[:100] + "...",
            "Inventori": ", ".join(p.inventors),
            "Depositante": p.applicants[0].name if p.applicants else "",
            "Anno": p.filing_date.year if p.filing_date else "",
            "Materiale": p.material_category
        } for p in filtered])
        search = st.text_input("Cerca per parola chiave")
        if search:
            df = df[df["Titolo"].str.contains(search, case=False) | df["Abstract"].str.contains(search, case=False)]
        st.dataframe(df, use_container_width=True)

# -------------------------------
# TREND
# -------------------------------
elif menu == "Trend":
    st.title("📈 Analisi Trend")
    yearly = yearly_counts(filtered)
    if yearly.empty:
        st.warning("Dati insufficienti.")
    else:
        fig = px.line(yearly, x="year", y="count", color="material", title="Depositi per anno")
        st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# COMPETITOR
# -------------------------------
else:
    st.title("🏢 Competitor Intelligence")
    top = top_applicants(filtered, n=10)
    if top.empty:
        st.warning("Nessun depositante trovato.")
    else:
        fig = px.bar(top, x="total", y="name", orientation="h", title="Top depositanti")
        st.plotly_chart(fig, use_container_width=True)

        # Mappa paesi (semplice)
        countries = [a.country for p in filtered for a in p.applicants if a.country]
        if countries:
            country_counts = pd.Series(countries).value_counts().reset_index()
            country_counts.columns = ["country", "count"]
            fig_map = px.choropleth(country_counts, locations="country", locationmode="country names", color="count", title="Distribuzione geografica")
            st.plotly_chart(fig_map, use_container_width=True)