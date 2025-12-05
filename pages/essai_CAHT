import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Démo CAHT – 5 affichages", layout="wide")

st.title("📊 Démo d'affichages pour le CA HT (2023 / 2024)")

st.markdown(
    """
    Données de test :

    - CA 2023 : **9 000 €**  
    - CA 2024 : **10 000 €**  
    - Détail 2023 : 5 000 € (7071), 4 000 € (7072)  
    - Détail 2024 : 6 000 € (7071), 4 000 € (7072)  

    Variation calculée en **montant** et en **%**, avec plusieurs idées de présentation.
    """
)

# =========================
# 1. Préparation des données
# =========================

data = pd.DataFrame([
    {"année": 2023, "compte": "7071", "libellé": "Ventes 7071", "CA": 5000},
    {"année": 2023, "compte": "7072", "libellé": "Ventes 7072", "CA": 4000},
    {"année": 2024, "compte": "7071", "libellé": "Ventes 7071", "CA": 6000},
    {"année": 2024, "compte": "7072", "libellé": "Ventes 7072", "CA": 4000},
])

pivot = data.pivot(index="compte", columns="année", values="CA").reset_index()
pivot["var_montant"] = pivot[2024] - pivot[2023]
pivot["var_pourcent"] = (pivot["var_montant"] / pivot[2023]).replace([float("inf"), -float("inf")], 0) * 100

total_2023 = data.loc[data["année"] == 2023, "CA"].sum()
total_2024 = data.loc[data["année"] == 2024, "CA"].sum()
total_var_montant = total_2024 - total_2023
total_var_pourcent = (total_var_montant / total_2023) * 100

pivot_affichage = pivot.copy()
pivot_affichage.rename(columns={2023: "CA 2023", 2024: "CA 2024"}, inplace=True)
pivot_affichage["Var montant"] = pivot_affichage["var_montant"]
pivot_affichage["Var %"] = pivot_affichage["var_pourcent"].round(1)

# =========================
# Proposition 1 – Tuiles KPI + détail en expander
# =========================

st.header("1️⃣ Tuiles KPI + détail en volet déroulant")

col1, col2, col3 = st.columns(3)

col1.metric("CA 2023", f"{total_2023:,.0f} €".replace(",", " "), "")
col2.metric("CA 2024", f"{total_2024:,.0f} €".replace(",", " "), "")
col3.metric(
    "Variation",
    f"{total_var_montant:,.0f} €".replace(",", " "),
    f"{total_var_pourcent:.1f} %",
)

with st.expander("👀 Voir le détail par compte (tableau)"):
    st.dataframe(
        pivot_affichage[["compte", "CA 2023", "CA 2024", "Var montant", "Var %"]],
        use_container_width=True,
    )

# =========================
# Proposition 2 – Barres comparatives + tableau qui se révèle
# =========================

st.header("2️⃣ Barres comparatives globales + détail en dessous")

chart_total = alt.Chart(
    pd.DataFrame(
        {
            "Année": ["2023", "2024"],
            "CA": [total_2023, total_2024],
        }
    )
).mark_bar().encode(
    x=alt.X("Année:N"),
    y=alt.Y("CA:Q"),
    tooltip=["Année", "CA"],
)

st.altair_chart(chart_total, use_container_width=True)

if st.toggle("📂 Afficher le détail par compte (tableau)"):
    st.dataframe(
        pivot_affichage[["compte", "CA 2023", "CA 2024", "Var montant", "Var %"]],
        use_container_width=True,
    )

# =========================
# Proposition 3 – Tabs : synthèse / détail / variations
# =========================

st.header("3️⃣ Onglets (tabs) : Synthèse / Détail / Variations")

tab1, tab2, tab3 = st.tabs(["Vue synthèse", "Détail comptes", "Variations"])

with tab1:
    st.subheader("Synthèse globale")
    col1, col2 = st.columns(2)
    col1.metric("CA 2023", f"{total_2023:,.0f} €".replace(",", " "))
    col2.metric("CA 2024", f"{total_2024:,.0f} €".replace(",", " "))
    st.metric(
        "Variation globale",
        f"{total_var_montant:,.0f} €".replace(",", " "),
        f"{total_var_pourcent:.1f} %",
    )

with tab2:
    st.subheader("Détail par compte (barres empilées)")
    chart_detail = alt.Chart(data).mark_bar().encode(
        x="année:O",
        y="CA:Q",
        color="compte:N",
        tooltip=["année", "compte", "CA"],
    )
    st.altair_chart(chart_detail, use_container_width=True)

with tab3:
    st.subheader("Variations par compte")
    st.dataframe(
        pivot_affichage[["compte", "CA 2023", "CA 2024", "Var montant", "Var %"]],
        use_container_width=True,
    )

# =========================
# Proposition 4 – Sélecteur de compte + drill-down instantané
# =========================

st.header("4️⃣ Sélecteur de compte + drill-down")

compte_sel = st.selectbox(
    "Choisir un compte à analyser",
    pivot_affichage["compte"].unique(),
)

row = pivot_affichage[pivot_affichage["compte"] == compte_sel].iloc[0]

c1, c2, c3 = st.columns(3)
c1.metric("CA 2023", f"{row['CA 2023']:,.0f} €".replace(",", " "))
c2.metric("CA 2024", f"{row['CA 2024']:,.0f} €".replace(",", " "))
c3.metric(
    "Variation",
    f"{row['Var montant']:,.0f} €".replace(",", " "),
    f"{row['Var %']:.1f} %",
)

df_compte = data[data["compte"] == compte_sel]
chart_compte = alt.Chart(df_compte).mark_bar().encode(
    x="année:O",
    y="CA:Q",
    tooltip=["année", "CA"],
)
st.altair_chart(chart_compte, use_container_width=True)

# =========================
# Proposition 5 – Vue “tableau + détail en expander par ligne”
# =========================

st.header("5️⃣ Tableau récap + expander par ligne")

st.markdown("Clique sur une ligne pour voir le détail du compte.")

for _, r in pivot_affichage.iterrows():
    with st.expander(
        f"Compte {r['compte']} – CA 2023 : {r['CA 2023']:.0f} €, CA 2024 : {r['CA 2024']:.0f} €"
    ):
        c1, c2, c3 = st.columns(3)
        c1.metric("CA 2023", f"{r['CA 2023']:,.0f} €".replace(",", " "))
        c2.metric("CA 2024", f"{r['CA 2024']:,.0f} €".replace(",", " "))
        c3.metric(
            "Variation",
            f"{r['Var montant']:,.0f} €".replace(",", " "),
            f"{r['Var %']:.1f} %",
        )

        df_compte = data[data["compte"] == r["compte"]]
        chart = alt.Chart(df_compte).mark_bar().encode(
            x="année:O",
            y="CA:Q",
            tooltip=["année", "CA"],
        )
        st.altair_chart(chart, use_container_width=True)
