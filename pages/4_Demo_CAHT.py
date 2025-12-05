import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="Démo CAHT – 2 niveaux de détail", layout="wide")

# ========= 1. DATAFRAME D'ESSAI =========
@st.cache_data
def make_sample_ca():
    """
    CAHT d'essai :
    - 2 comptes : 7071 / 7072
    - 2 années : 2023 / 2024
    - Répartition mois par mois, avec une petite saisonnalité
    - Totaux annuels :
        2023 : 5 000 (7071) + 4 000 (7072)
        2024 : 6 000 (7071) + 4 000 (7072)
    """
    rows = []
    months = np.arange(1, 13)

    # saisonnalité douce sur 12 mois
    base_weights = 1 + 0.3 * np.sin(2 * np.pi * (months - 1) / 12)
    base_weights = base_weights / base_weights.sum()  # somme = 1

    annual_totals = {
        (2023, "7071"): 5000,
        (2023, "7072"): 4000,
        (2024, "7071"): 6000,
        (2024, "7072"): 4000,
    }

    for (year, compte), total in annual_totals.items():
        for m, w in zip(months, base_weights):
            montant = total * float(w)
            rows.append(
                {
                    "annee": year,
                    "mois": m,
                    "periode": pd.Timestamp(year=year, month=m, day=1),
                    "compte": compte,
                    "ca_ht": montant,
                }
            )

    df = pd.DataFrame(rows)
    return df

df_ca = make_sample_ca()

# ========= 2. AGRÉGATS N / N-1 =========
ANNEE_N = 2024
ANNEE_N_1 = 2023

totaux = (
    df_ca.groupby(["annee", "compte"])["ca_ht"]
    .sum()
    .reset_index()
    .pivot(index="compte", columns="annee", values="ca_ht")
    .fillna(0)
)

# On s'assure que les colonnes existent
for a in [ANNEE_N, ANNEE_N_1]:
    if a not in totaux.columns:
        totaux[a] = 0

totaux = totaux.reset_index()
totaux.rename(columns={ANNEE_N: "CA_N", ANNEE_N_1: "CA_N_1"}, inplace=True)
totaux["Var"] = totaux["CA_N"] - totaux["CA_N_1"]
totaux["Var_%"] = np.where(
    totaux["CA_N_1"] != 0, totaux["Var"] / totaux["CA_N_1"] * 100, 0
)

total_N = totaux["CA_N"].sum()
total_N_1 = totaux["CA_N_1"].sum()
total_Var = total_N - total_N_1
total_Var_pct = total_Var / total_N_1 * 100 if total_N_1 else 0

fmt = lambda x: f"{x:,.0f} €".replace(",", " ")

# ========= 3. MISE EN PAGE =========

st.title("📊 Chiffre d'affaires – 2 niveaux de détail (démo)")

col_left, col_right = st.columns([1, 2])

# --- Colonne gauche : tuiles + bouton détail ---
with col_left:
    st.subheader("Vue synthèse CA")

    m1, m2, m3 = st.columns(3)
    m1.metric(f"CA N ({ANNEE_N})", fmt(total_N))
    m2.metric(f"CA N-1 ({ANNEE_N_1})", fmt(total_N_1))
    m3.metric("Variation", fmt(total_Var), f"{total_Var_pct:.1f} %")

    st.markdown("### Chiffre d'affaires")
    st.markdown(
        "- **7071** : Ventes type 1  \n"
        "- **7072** : Ventes type 2"
    )

    if "show_ca_detail" not in st.session_state:
        st.session_state["show_ca_detail"] = False

    if st.button("🔎 Voir le détail du CA"):
        st.session_state["show_ca_detail"] = True

    st.markdown(
        "<small>Cette zone sera réutilisée plus tard pour d'autres rubriques du SIG.</small>",
        unsafe_allow_html=True,
    )

# --- Colonne droite : 2 niveaux de détail ---
with col_right:
    st.subheader("Détail du chiffre d'affaires")

    if not st.session_state.get("show_ca_detail", False):
        st.info("Clique sur **« Voir le détail du CA »** à gauche pour afficher les détails.")
        st.stop()

    # ===== Niveau 1 : tableau N / N-1 par compte =====
    st.markdown("#### Niveau 1 – Comparatif par compte (N / N-1)")

    df_aff = totaux.copy()
    df_aff["CA_N_fmt"] = df_aff["CA_N"].map(fmt)
    df_aff["CA_N1_fmt"] = df_aff["CA_N_1"].map(fmt)
    df_aff["Var_fmt"] = df_aff["Var"].map(fmt)
    df_aff["Var_%_fmt"] = df_aff["Var_%"].map(lambda v: f"{v:.1f} %")

    st.dataframe(
        df_aff[["compte", "CA_N_fmt", "CA_N1_fmt", "Var_fmt", "Var_%_fmt"]]
        .rename(
            columns={
                "compte": "Compte",
                "CA_N_fmt": f"CA {ANNEE_N}",
                "CA_N1_fmt": f"CA {ANNEE_N_1}",
                "Var_fmt": "Écart",
                "Var_%_fmt": "Écart %",
            }
        ),
        use_container_width=True,
    )

    # ===== Niveau 2 : graphiques =====
    st.markdown("#### Niveau 2 – Graphiques de détail")

    g1, g2 = st.columns(2)

    # --- Graphique 1 : évolution mensuelle (groupé par compte) ---
    with g1:
        st.markdown("**Évolution mensuelle N / N-1**")

        df_month = (
            df_ca.groupby(["annee", "periode", "compte"])["ca_ht"]
            .sum()
            .reset_index()
        )

        chart_month = (
            alt.Chart(df_month)
            .mark_line(point=True)
            .encode(
                x=alt.X("periode:T", title="Période"),
                y=alt.Y("ca_ht:Q", title="CA HT"),
                color="compte:N",
                strokeDash="annee:N",
                tooltip=["annee", "compte", "periode", "ca_ht"],
            )
            .properties(height=300)
        )

        st.altair_chart(chart_month, use_container_width=True)

    # --- Graphique 2 : double donut N / N-1 ---
    with g2:
        st.markdown(f"**Structure du CA – {ANNEE_N} vs {ANNEE_N_1}**")

        df_pie = pd.melt(
            totaux[["compte", "CA_N", "CA_N_1"]],
            id_vars="compte",
            var_name="exercice",
            value_name="ca_ht",
        )
        df_pie["exercice"] = df_pie["exercice"].map(
            {"CA_N": str(ANNEE_N), "CA_N_1": str(ANNEE_N_1)}
        )

        donut = (
            alt.Chart(df_pie)
            .mark_arc(innerRadius=50)
            .encode(
                theta="ca_ht:Q",
                color="compte:N",
                tooltip=["exercice", "compte", "ca_ht"],
            )
            .properties(width=200, height=200)
            .facet(column="exercice:N")
        )

        st.altair_chart(donut, use_container_width=True)

    st.markdown(
        "<small>Idée : plus tard, on pourra filtrer ces graphiques par client, dossier, famille de produits, etc.</small>",
        unsafe_allow_html=True,
    )
