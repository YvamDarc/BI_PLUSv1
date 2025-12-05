import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Démo CAHT – Variantes d’affichage", layout="wide")

st.title("📊 Démo CA HT 2023 / 2024 – 5 variantes d’affichage")

st.markdown(
    """
    Données de test :

    - CA 2023 : **9 000 €**  
    - CA 2024 : **10 000 €**  
    - Détail 2023 : 5 000 € (7071), 4 000 € (7072)  
    - Détail 2024 : 6 000 € (7071), 4 000 € (7072)  

    🔎 Objectif : comparer plusieurs façons d'afficher **la synthèse + le détail cliquable**.
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
pivot["var_pourcent"] = (pivot["var_montant"] / pivot[2023]) * 100

total_2023 = data.loc[data["année"] == 2023, "CA"].sum()
total_2024 = data.loc[data["année"] == 2024, "CA"].sum()
total_var_montant = total_2024 - total_2023
total_var_pourcent = (total_var_montant / total_2023) * 100

pivot_aff = pivot.rename(columns={2023: "CA 2023", 2024: "CA 2024"})
pivot_aff["Var montant"] = pivot_aff["var_montant"]
pivot_aff["Var %"] = pivot_aff["var_pourcent"].round(1)

# Petite fonction utilitaire pour formater les montants
fmt = lambda x: f"{x:,.0f} €".replace(",", " ")


# =========================
# Variante 1 – KPI global + tableau + expander par compte
# =========================

st.header("1️⃣ KPI global + tableau récap + expander par compte")

col1, col2, col3 = st.columns(3)
col1.metric("CA 2023", fmt(total_2023))
col2.metric("CA 2024", fmt(total_2024))
col3.metric("Variation", fmt(total_var_montant), f"{total_var_pourcent:.1f} %")

st.subheader("Tableau récapitulatif par compte")
st.dataframe(
    pivot_aff[["compte", "CA 2023", "CA 2024", "Var montant", "Var %"]],
    use_container_width=True,
)

st.markdown("**Détail cliquable par compte :**")

for _, r in pivot_aff.iterrows():
    with st.expander(
        f"Compte {r['compte']} – CA 2023 : {r['CA 2023']:.0f} €, CA 2024 : {r['CA 2024']:.0f} €"
    ):
        c1, c2, c3 = st.columns(3)
        c1.metric("CA 2023", fmt(r["CA 2023"]))
        c2.metric("CA 2024", fmt(r["CA 2024"]))
        c3.metric("Variation", fmt(r["Var montant"]), f"{r['Var %']:.1f} %")

        df_compte = data[data["compte"] == r["compte"]]
        chart = alt.Chart(df_compte).mark_bar().encode(
            x="année:O",
            y="CA:Q",
            tooltip=["année", "CA"],
        )
        st.altair_chart(chart, use_container_width=True)


# =========================
# Variante 2 – KPI global + onglets (Synthèse / Détail / Graphique)
# =========================

st.header("2️⃣ KPI global + onglets synthèse / détail / graphique")

col1, col2, col3 = st.columns(3)
col1.metric("CA 2023", fmt(total_2023))
col2.metric("CA 2024", fmt(total_2024))
col3.metric("Variation", fmt(total_var_montant), f"{total_var_pourcent:.1f} %")

tab1, tab2, tab3 = st.tabs(["Synthèse", "Détail par compte", "Graphique global"])

with tab1:
    st.subheader("Vue synthèse")
    st.write("Variation globale du chiffre d'affaires.")
    chart_total = alt.Chart(
        pd.DataFrame({"Année": ["2023", "2024"], "CA": [total_2023, total_2024]})
    ).mark_bar().encode(
        x="Année:N",
        y="CA:Q",
        tooltip=["Année", "CA"],
    )
    st.altair_chart(chart_total, use_container_width=True)

with tab2:
    st.subheader("Détail par compte")
    st.dataframe(
        pivot_aff[["compte", "CA 2023", "CA 2024", "Var montant", "Var %"]],
        use_container_width=True,
    )

with tab3:
    st.subheader("Graphique empilé par compte")
    chart_detail = alt.Chart(data).mark_bar().encode(
        x="année:O",
        y="CA:Q",
        color="compte:N",
        tooltip=["année", "compte", "CA"],
    )
    st.altair_chart(chart_detail, use_container_width=True)


# =========================
# Variante 3 – KPI global + sélecteur de compte + expander de détail
# =========================

st.header("3️⃣ KPI global + sélecteur de compte + volet de détail")

col1, col2, col3 = st.columns(3)
col1.metric("CA 2023", fmt(total_2023))
col2.metric("CA 2024", fmt(total_2024))
col3.metric("Variation", fmt(total_var_montant), f"{total_var_pourcent:.1f} %")

compte_sel = st.selectbox(
    "Choisir un compte à analyser :", pivot_aff["compte"].unique()
)

row = pivot_aff[pivot_aff["compte"] == compte_sel].iloc[0]

c1, c2, c3 = st.columns(3)
c1.metric("CA 2023", fmt(row["CA 2023"]))
c2.metric("CA 2024", fmt(row["CA 2024"]))
c3.metric("Variation", fmt(row["Var montant"]), f"{row['Var %']:.1f} %")

with st.expander(f"Détail pour le compte {compte_sel}"):
    df_compte = data[data["compte"] == compte_sel]
    st.write("Historique par année :")
    st.dataframe(df_compte, use_container_width=True)

    chart = alt.Chart(df_compte).mark_bar().encode(
        x="année:O",
        y="CA:Q",
        tooltip=["année", "CA"],
    )
    st.altair_chart(chart, use_container_width=True)


# =========================
# Variante 4 – Deux colonnes : à gauche synthèse, à droite expanders
# =========================

st.header("4️⃣ Deux colonnes : synthèse à gauche, détail cliquable à droite")

colL, colR = st.columns([1, 2])

with colL:
    st.subheader("Synthèse globale")
    st.metric("CA 2023", fmt(total_2023))
    st.metric("CA 2024", fmt(total_2024))
    st.metric("Variation", fmt(total_var_montant), f"{total_var_pourcent:.1f} %")

    chart_total2 = alt.Chart(
        pd.DataFrame({"Année": ["2023", "2024"], "CA": [total_2023, total_2024]})
    ).mark_bar().encode(
        x="Année:N",
        y="CA:Q",
    )
    st.altair_chart(chart_total2, use_container_width=True)

with colR:
    st.subheader("Comptes – détail cliquable")
    for _, r in pivot_aff.iterrows():
        with st.expander(
            f"Compte {r['compte']} – Var {fmt(r['Var montant'])} ({r['Var %']:.1f} %)"
        ):
            c1, c2, c3 = st.columns(3)
            c1.metric("CA 2023", fmt(r["CA 2023"]))
            c2.metric("CA 2024", fmt(r["CA 2024"]))
            c3.metric("Variation", fmt(r["Var montant"]), f"{r['Var %']:.1f} %")

            df_compte = data[data["compte"] == r["compte"]]
            chart = alt.Chart(df_compte).mark_bar().encode(
                x="année:O",
                y="CA:Q",
                tooltip=["année", "CA"],
            )
            st.altair_chart(chart, use_container_width=True)


# =========================
# Variante 5 – Vue “liste interactive” : tableau + expander synchronisé
# =========================

st.header("5️⃣ Tableau interactif + expander synchronisé")

col1, col2, col3 = st.columns(3)
col1.metric("CA 2023", fmt(total_2023))
col2.metric("CA 2024", fmt(total_2024))
col3.metric("Variation", fmt(total_var_montant), f"{total_var_pourcent:.1f} %")

st.write("Sélectionne un compte dans le tableau, puis ouvre le volet de détail.")

st.dataframe(
    pivot_aff[["compte", "CA 2023", "CA 2024", "Var montant", "Var %"]],
    use_container_width=True,
)

compte_detail = st.selectbox(
    "Compte à détailler :", pivot_aff["compte"].unique(), key="detail_select"
)
row2 = pivot_aff[pivot_aff["compte"] == compte_detail].iloc[0]

with st.expander(f"Détail du compte {compte_detail}", expanded=True):
    c1, c2, c3 = st.columns(3)
    c1.metric("CA 2023", fmt(row2["CA 2023"]))
    c2.metric("CA 2024", fmt(row2["CA 2024"]))
    c3.metric("Variation", fmt(row2["Var montant"]), f"{row2['Var %']:.1f} %")

    df_compte = data[data["compte"] == compte_detail]
    chart = alt.Chart(df_compte).mark_bar().encode(
        x="année:O",
        y="CA:Q",
        tooltip=["année", "CA"],
    )
    st.altair_chart(chart, use_container_width=True)
