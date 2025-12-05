import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Démo CAHT – Style RCA", layout="wide")

st.title("📊 Démo CA HT 2023 / 2024 – Style RCA")

st.markdown(
    """
    Exemple de données :

    - CA 2023 : **9 000 €**  
    - CA 2024 : **10 000 €**  
    - Détail 2023 : 5 000 € (7071), 4 000 € (7072)  
    - Détail 2024 : 6 000 € (7071), 4 000 € (7072)  

    Les 5 variantes ci-dessous mélangent :
    - résumé SIG  
    - variations N / N-1  
    - détail cliquable façon « comparatif N/N-1 ».
    """
)

# =========================
# 1. Données de base
# =========================

# Niveau "agrégat" (2 lignes de CA)
agg = pd.DataFrame([
    {"rubrique": "Chiffre d'affaires – 7071", "compte": "7071", "N": 6000, "N_1": 5000},
    {"rubrique": "Chiffre d'affaires – 7072", "compte": "7072", "N": 4000, "N_1": 4000},
])

agg["Var"] = agg["N"] - agg["N_1"]
agg["Var_%"] = (agg["Var"] / agg["N_1"]).replace([float("inf"), -float("inf")], 0) * 100

total_N = agg["N"].sum()
total_N_1 = agg["N_1"].sum()
total_Var = total_N - total_N_1
total_Var_pct = (total_Var / total_N_1) * 100

# Niveau "détail comptes" (façon image 3)
detail = pd.DataFrame([
    {"compte": "7071000000", "libellé": "Hébergement T1 20m2", "N": 1224664, "N_1": 1100000},
    {"compte": "7072000000", "libellé": "Prise en charge déplacement", "N": 30088, "N_1": 25000},
    {"compte": "7073000000", "libellé": "Hébergement T1 20m2 promo", "N": 103064, "N_1": 95000},
])

detail["Ecart"] = detail["N"] - detail["N_1"]
detail["Ecart_%"] = (detail["Ecart"] / detail["N_1"]).replace([float("inf"), -float("inf")], 0) * 100

fmt = lambda x: f"{x:,.0f} €".replace(",", " ")


# =====================================================================
# VARIANTE 1 – Liste SIG + % évolution + menu "Voir le détail"
# =====================================================================

st.header("1️⃣ Liste SIG + % évolution + menu « Voir le détail » (style écran 1)")

colN, colN1, colVar = st.columns(3)
colN.metric("CA N (2024)", fmt(total_N))
colN1.metric("CA N-1 (2023)", fmt(total_N_1))
colVar.metric("Variation globale", fmt(total_Var), f"{total_Var_pct:.1f} %")

st.markdown("---")

for i, row in agg.iterrows():
    c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 1])

    c1.markdown(f"**{row['rubrique']}**")
    c2.write(fmt(row["N"]))
    c3.write(fmt(row["N_1"]))
    c4.markdown(f"{fmt(row['Var'])}  \n`{row['Var_%']:.1f} %`")

    with c5:
        if st.button("⋮", key=f"btn_menu_{i}"):
            st.session_state["selected_rubrique"] = row["rubrique"]
            st.session_state["selected_compte"] = row["compte"]

# Zone de détail (façon « Voir le détail du compte »)
if "selected_rubrique" in st.session_state:
    st.markdown("### 🔍 Détail sélectionné")
    st.markdown(f"**{st.session_state['selected_rubrique']}**")
    st.dataframe(detail, use_container_width=True)


# =====================================================================
# VARIANTE 2 – Bloc « Détail des produits (comparatif N-1) »
# =====================================================================

st.header("2️⃣ Bloc synthèse type « Détail des produits (comparatif N-1) » (image 2)")

styled = agg.copy()
styled["N_fmt"] = styled["N"].map(fmt)
styled["N1_fmt"] = styled["N_1"].map(fmt)
styled["Var_txt"] = styled["Var_%"].map(lambda v: f"{v:+.1f}%")

cYearN, cYearN1, cEvol = st.columns([2, 2, 1])
cYearN.markdown("**2024**")
cYearN1.markdown("**2023**")
cEvol.markdown("**Évolution**")

for _, r in styled.iterrows():
    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
    c1.markdown(f"**{r['rubrique']}**")
    c2.markdown(f"{r['N_fmt']}")
    c3.markdown(f"{r['N1_fmt']}")
    c4.markdown(f"{r['Var_txt']}")

st.markdown("_Idée : ce bloc pourrait être cliquable pour ouvrir ensuite le tableau de comptes (voir variantes 3–4–5)._")

# =====================================================================
# VARIANTE 3 – Tabs : Synthèse / Détail du compte / Comparatif N-1
# =====================================================================

st.header("3️⃣ Onglets : Synthèse / Comparatif / Détail comptes (mix 1 + 3)")

tab1, tab2, tab3 = st.tabs(["Synthèse SIG", "Comparatif N/N-1", "Détail comptes"])

with tab1:
    st.subheader("Synthèse SIG (niveau CA)")
    st.dataframe(
        agg.assign(
            N=agg["N"].map(fmt),
            N_1=agg["N_1"].map(fmt),
            Var=agg["Var"].map(fmt),
            Var_pct=agg["Var_%"].map(lambda x: f"{x:.1f} %"),
        )[["rubrique", "N", "N_1", "Var", "Var_pct"]],
        use_container_width=True,
    )

with tab2:
    st.subheader("Graphique comparatif N / N-1")
    data_chart = agg.melt(id_vars=["rubrique"], value_vars=["N", "N_1"],
                          var_name="Exercice", value_name="Montant")
    data_chart["Exercice"] = data_chart["Exercice"].map({"N": "2024", "N_1": "2023"})
    chart = alt.Chart(data_chart).mark_bar().encode(
        x="rubrique:N",
        y="Montant:Q",
        color="Exercice:N",
        column="Exercice:N",
        tooltip=["rubrique", "Exercice", "Montant"],
    )
    st.altair_chart(chart, use_container_width=True)

with tab3:
    st.subheader("Détail comptes (façon vue 3)")
    st.dataframe(
        detail.assign(
            N_fmt=detail["N"].map(fmt),
            N1_fmt=detail["N_1"].map(fmt),
            Ecart_fmt=detail["Ecart"].map(fmt),
            Ecart_pct=detail["Ecart_%"].map(lambda x: f"{x:.1f} %"),
        )[["compte", "libellé", "N_fmt", "N1_fmt", "Ecart_fmt", "Ecart_pct"]],
        use_container_width=True,
    )


# =====================================================================
# VARIANTE 4 – Colonne SIG à gauche + panneau de détail à droite
# =====================================================================

st.header("4️⃣ Colonne SIG à gauche + panneau de détail à droite (mix 1 + 5)")

col_left, col_right = st.columns([1.5, 2])

with col_left:
    st.subheader("SIG – CA détaillé")
    selected_in_left = st.radio(
        "Rubrique à analyser :",
        options=agg["rubrique"].tolist(),
        index=0,
        label_visibility="collapsed",
    )

with col_right:
    st.subheader(f"Détail pour : {selected_in_left}")
    # On pourrait filtrer par compte, ici on montre tout pour la démo
    st.dataframe(detail, use_container_width=True)

    chart = alt.Chart(detail).mark_bar().encode(
        x="compte:N",
        y="N:Q",
        tooltip=["compte", "libellé", "N", "N_1", "Ecart", "Ecart_%"],
    )
    st.altair_chart(chart, use_container_width=True)


# =====================================================================
# VARIANTE 5 – Table comparatif + expander pour « zoom compte »
# =====================================================================

st.header("5️⃣ Tableau comparatif + expander “zoom compte” (mix 1 + 3 + 5)")

st.subheader("Comparatif N / N-1 par compte")

st.dataframe(
    detail.assign(
        N_fmt=detail["N"].map(fmt),
        N1_fmt=detail["N_1"].map(fmt),
        Ecart_fmt=detail["Ecart"].map(fmt),
        Ecart_pct=detail["Ecart_%"].map(lambda x: f"{x:.1f} %"),
    )[["compte", "libellé", "N_fmt", "N1_fmt", "Ecart_fmt", "Ecart_pct"]],
    use_container_width=True,
)

compte_zoom = st.selectbox(
    "Choisir un compte à zoomer :", detail["compte"].tolist()
)

row_zoom = detail[detail["compte"] == compte_zoom].iloc[0]

with st.expander(f"🔍 Zoom sur le compte {compte_zoom} – {row_zoom['libellé']}", expanded=True):
    c1, c2, c3 = st.columns(3)
    c1.metric("Exercice N", fmt(row_zoom["N"]))
    c2.metric("Exercice N-1", fmt(row_zoom["N_1"]))
    c3.metric("Écart N / N-1", fmt(row_zoom["Ecart"]), f"{row_zoom['Ecart_%']:.1f} %")

    # Mini série historique N / N-1
    hist = pd.DataFrame([
        {"exercice": "N-1 (2023)", "montant": row_zoom["N_1"]},
        {"exercice": "N (2024)", "montant": row_zoom["N"]},
    ])
    chart_zoom = alt.Chart(hist).mark_bar().encode(
        x="exercice:N",
        y="montant:Q",
        tooltip=["exercice", "montant"],
    )
    st.altair_chart(chart_zoom, use_container_width=True)
