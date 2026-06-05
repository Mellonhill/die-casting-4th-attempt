import streamlit as st
import pandas as pd
from datetime import date

# -------------------------------
# DATASET DEMO
# -------------------------------
def load_demo_patents():
    return [
        {
            "id": "EP1234567A1",
            "title": "Processo di pressofusione per leghe di Zama",
            "abstract": "Metodo per pressofusione di zinco con alta resistenza",
            "filing_date": date(2021,3,15),
            "inventors": ["Rossi M."],
            "applicant": "Fonderie S.p.A.",
            "applicant_country": "IT",
            "cpc_classes": ["B22D17/22"],
            "material_category": "Zama"
        },
        {
            "id": "US2022123456A1",
            "title": "Aluminium die casting method for automotive",
            "abstract": "High-pressure die casting of aluminium alloys",
            "filing_date": date(2020,6,20),
            "inventors": ["Johnson P."],
            "applicant": "AutoTech GmbH",
            "applicant_country": "DE",
            "cpc_classes": ["B22D17/20"],
            "material_category": "Alluminio"
        },
        {
            "id": "WO2023123456A1",
            "title": "Magnesium alloy die casting with reduced porosity",
            "abstract": "Process for magnesium alloys minimizing gas porosity",
            "filing_date": date(2022,9,1),
            "inventors": ["Chen W."],
            "applicant": "Magnesium Research Inst.",
            "applicant_country": "CN",
            "cpc_classes": ["B22D17/00"],
            "material_category": "Magnesio"
        },
        {
            "id": "EP9876543B1",
            "title": "Zinc alloy with improved fluidity for die casting",
            "abstract": "Composition and method for zamak alloys",
            "filing_date": date(2019,5,5),
            "inventors": ["Bianchi L."],
            "applicant": "Zamak Corp",
            "applicant_country": "IT",
            "cpc_classes": ["C22C18/00"],
            "material_category": "Zama"
        },
        {
            "id": "DE102021123456",
            "title": "Aluminium die casting tool with cooling channels",
            "abstract": "Tool design for high-pressure die casting",
            "filing_date": date(2021,11,11),
            "inventors": ["Schmidt H."],
            "applicant": "Bayerische Motoren Werke",
            "applicant_country": "DE",
            "cpc_classes": ["B22D17/22"],
            "material_category": "Alluminio"
        },
        {
            "id": "JP2023123456",
            "title": "Magnesium casting method for electronics",
            "abstract": "Thin-wall magnesium die casting",
            "filing_date": date(2023,1,15),
            "inventors": ["Tanaka K."],
            "applicant": "Toyota Jidosha",
            "applicant_country": "JP",
            "cpc_classes": ["B22D17/00"],
            "material_category": "Magnesio"
        }
    ]

# -------------------------------
# FUNZIONI DI ANALISI
# -------------------------------
def yearly_counts(patents):
    data = []
    for p in patents:
        if p["filing_date"]:
            data.append({"year": p["filing_date"].year, "material": p["material_category"]})
    df = pd.DataFrame(data)
    if df.empty:
        return pd.DataFrame(columns=["year","material","count"])
    return df.groupby(["year","material"]).size().reset_index(name="count")

def top_applicants(patents, n=10):
    apps = []
    for p in patents:
        apps.append({"name": p["applicant"], "material": p["material_category"]})
    df = pd.DataFrame(apps)
    if df.empty:
        return pd.DataFrame()
    top = df.groupby("name").size().reset_index(name="total").sort_values("total", ascending=False).head(n)
    return top

# -------------------------------
# INTERFACCIA STREAMLIT
# -------------------------------
st.set_page_config(page_title="Die Casting Patent Analytics", page_icon="🏭", layout="wide")

if "patents" not in st.session_state:
    st.session_state.patents = load_demo_patents()

patents = st.session_state.patents

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/patent.png", width=60)
    st.title("🔍 Filtri")
    materials = st.multiselect("Materiale", ["Zama","Alluminio","Magnesio"], default=["Zama","Alluminio","Magnesio"])
    years = st.slider("Anni", 2015, 2025, (2019, 2023), step=1)
    refresh = st.button("🔄 Reset")

if refresh:
    st.session_state.patents = load_demo_patents()
    st.rerun()

filtered = [p for p in patents if p["material_category"] in materials and p["filing_date"] and years[0] <= p["filing_date"].year <= years[1]]
st.sidebar.write(f"**Brevetti visualizzati:** {len(filtered)}")

menu = st.sidebar.radio("Vai a:", ["Dashboard", "Ricerca", "Trend", "Competitor"])

if menu == "Dashboard":
    st.title("📊 Dashboard Panoramica")
    if not filtered:
        st.warning("Nessun brevetto con i filtri selezionati.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Totale", len(filtered))
        col2.metric("Zama", sum(1 for p in filtered if p["material_category"]=="Zama"))
        col3.metric("Alluminio", sum(1 for p in filtered if p["material_category"]=="Alluminio"))
        st.metric("Magnesio", sum(1 for p in filtered if p["material_category"]=="Magnesio"))

        yearly = yearly_counts(filtered)
        if not yearly.empty:
            st.subheader("Andamento depositi per anno")
            pivot = yearly.pivot(index="year", columns="material", values="count").fillna(0)
            st.line_chart(pivot)

        top = top_applicants(filtered, n=8)
        if not top.empty:
            st.subheader("Top depositanti")
            st.bar_chart(top.set_index("name")["total"])

elif menu == "Ricerca":
    st.title("🔎 Ricerca Brevetti")
    if not filtered:
        st.warning("Nessun brevetto.")
    else:
        df = pd.DataFrame([{
            "ID": p["id"],
            "Titolo": p["title"],
            "Abstract": p["abstract"][:100] + "...",
            "Inventori": ", ".join(p["inventors"]),
            "Depositante": p["applicant"],
            "Anno": p["filing_date"].year if p["filing_date"] else "",
            "Materiale": p["material_category"]
        } for p in filtered])
        search = st.text_input("Cerca per parola chiave")
        if search:
            df = df[df["Titolo"].str.contains(search, case=False) | df["Abstract"].str.contains(search, case=False)]
        st.dataframe(df, use_container_width=True)

elif menu == "Trend":
    st.title("📈 Analisi Trend")
    yearly = yearly_counts(filtered)
    if yearly.empty:
        st.warning("Dati insufficienti.")
    else:
        pivot = yearly.pivot(index="year", columns="material", values="count").fillna(0)
        st.line_chart(pivot)

else:  # Competitor
    st.title("🏢 Competitor Intelligence")
    top = top_applicants(filtered, n=10)
    if top.empty:
        st.warning("Nessun depositante trovato.")
    else:
        st.subheader("Top depositanti")
        st.bar_chart(top.set_index("name")["total"])

        countries = [p["applicant_country"] for p in filtered if p["applicant_country"]]
        if countries:
            st.subheader("Distribuzione per paese")
            country_df = pd.Series(countries).value_counts().reset_index()
            country_df.columns = ["Paese", "Numero"]
            st.bar_chart(country_df.set_index("Paese")["Numero"])
