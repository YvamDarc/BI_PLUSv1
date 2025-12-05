import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="Démo SIG – Marge commerciale", layout="wide")

# =========================
# 1. DATAFRAME D'ESSAI
# =========================

@st.cache_data
def make_sample_sig():
    """
    Données d'essai pour un mini-SIG :
    - Comptes CA : 7071, 7072, 7073
    - Comptes Achats : 6071, 6072
    - Variation de stock : 6031
    - 2 années : 2023 (N-1), 2024 (N)
    - Répartition mensuelle avec une petite saisonnalité
    """

    accounts = [
        {"compte": "7071", "type": "CA", "libelle": "Ventes négoce"},
        {"compte": "7072", "type": "CA", "libelle": "Ventes services"},
        {"compte": "7073", "type": "CA", "libelle": "Autres ventes"},
        {"compte": "6071", "type": "ACH", "libelle": "Achats marchandises"},
        {"compte": "6072", "type": "ACH", "libelle": "Achats négoce"},
        {"compte": "6031", "type": "STK", "libelle": "Variation stock marchandises"},
    ]

    # Totaux annuels par compte
    annual_totals = {
        (2023, "7071"): 4000,
        (2023, "7072"): 3000,
        (2023, "7073"): 2000,
        (2023, "6071"): 3500,
        (2023, "6072"): 1800,
        (2023, "6031"): -300,   # variation stock négative

        (2024, "7071"): 4500,
        (2024, "7072"): 3200,
        (2024, "7073"): 2300,
        (2024, "6071"): 3800,
        (2024, "6072"): 1900,
        (2024, "6031"): -250,
    }

    months = np.arange(1, 13)
    base_weights = 1 + 0.3 * np.sin(2 * np.pi * (months - 1) / 12)
    base_weights = base_weights / base_weights.sum()

    rows = []
    for (year, compte), total in annual_totals.items():
        for m, w in zip(months, base_weights):
            montant = float(total * w)
            rows.append(
                {
                    "annee": year,
                    "mois": m,
                    "periode": pd.Timestamp(year=year, month=m, day=1),
                    "compte": compte,
                    "montant": montant,
                }
            )

    df = pd.DataFrame(rows)
    df = df.merge(pd.DataFrame(accounts), on="compte", how="left")
    return df

df = make_sample_sig()

ANNEE_N = 2024
ANNEE_N_1 = 2023
fmt = lambda x: f"{x:,.0f} €".replace(",", " ")

# =========================
# 2. CALCUL DU MINI-SIG
# =========================

def sig_agg(df):
    agg_year = (
        df.groupby(["annee", "type"])["montant"]
        .sum()
        .reset_index()
        .pivot(index="type", columns="annee", values="montant")
        .fillna(0)
    )
    # S'assurer des colonnes
    for a in [ANNEE_N, ANNEE_N_1]:
        if a not in agg_year.columns:
            agg_year[a] = 0
    agg_year = agg_year.reset_index().rename(columns={ANNEE_N: "N", ANNEE_N_1: "N_1"})

    # Reconstitution des lignes SIG
    ca = agg_year.loc[agg_year["type"] == "CA", ["N", "N_1"]].sum()
    achats = agg_year.loc[agg_year["type"] == "ACH", ["N", "N_1"]].sum()
    var_stk = agg_year.loc[agg_year["type"] == "STK", ["N", "N_1"]].sum()

    sig_rows = []
    sig_rows.append({"poste": "Chiffre d'affaires", "N": ca["N"], "N_1": ca["N_1"]})
    sig_rows.append({"poste": "Achats consommés", "N": achats["N"], "N_1": achats["N_1"]})
    sig_rows.append({"poste": "Variation de stock", "N": var_stk["N"], "N_1": var_stk["N_1"]})

    marge_N = ca["N"] - achats["N"] - var_stk["N"]
    marge_N_1 = ca["N_1"] - achats["N_1"] - var_stk["N_1"]
    sig_rows.append({"poste": "Marge commerciale", "N": marge_N, "N_1": marge_N_1})

    sig_df = pd.DataFrame(sig_rows)
    sig_df["Var"] = sig_df["N"] - sig_df["N_1"]
    sig_df["Var_%"] = np.where(
        sig_df["N_1"] != 0, sig_df["Var"] / sig_df["N_1"] * 100, 0
    )
    return sig_df

sig_df = sig_agg(df)

total_row = sig_df.loc[sig_df["poste"] == "Marge commerciale"].iloc[0]
total_N = total_row["N"]
total_N_1 = total_row["N_1"]
total_Var = total_row["Var"]
total_Var_pct = total_row["Var_%"]

# =========================
# 3. ENTÊTE + BOUTONS DÉTAIL
# =========================

st.title("📊 Mini-SIG – jusqu’à la marge commerciale (démo)")

c1, c2, c3 = st.columns(3)
c1.metric(f"Marge N ({ANNEE_N})", fmt(total_N))
c2.metric(f"Marge N-1 ({ANNEE_N_1})", fmt(total_N_1))
c3.metric("Variation", fmt(total_Var), f"{total_Var_pct:.1f} %")

st.markdown("---")
st.subheader("Tableau SIG (N / N-1)")

sig_aff = sig_df.copy()
sig_aff["N_fmt"] = sig_aff["N"].map(fmt)
sig_aff["N1_fmt"] = sig_aff["N_1"].map(fmt)
sig_aff["Var_fmt"] = sig_aff["Var"].map(fmt)
sig_aff["Var_%_fmt"] = sig_aff["Var_%"].map(lambda v: f"{v:.1f} %")

st.table(
    sig_aff[["poste", "N_fmt", "N1_fmt", "Var_fmt", "Var_%_fmt"]]
    .rename(
        columns={
            "poste": "Poste",
            "N_fmt": f"N {ANNEE_N}",
            "N1_fmt": f"N-1 {ANNEE_N_1}",
            "Var_fmt": "Écart",
            "Var_%_fmt": "Écart %",
        }
    )
)

st.markdown("---")
st.subheader("Options d’affichage du détail *(à terme : réservées aux administrateurs)*")

col_opt1, col_opt2, col_opt3 = st.columns(3)
with col_opt1:
    show_ca_detail = st.toggle("Détail Chiffre d'affaires", value=True)
with col_opt2:
    show_achats_detail = st.toggle("Détail Achats consommés", value=True)
with col_opt3:
    show_stock_detail = st.toggle("Détail Variation de stock", value=False)

# =========================
# 4. DÉTAIL CA – 707x
# =========================

if show_ca_detail:
    st.markdown("## 🔹 Détail Chiffre d'affaires")

    df_ca = df[df["type"] == "CA"].copy()

    # Niveau 1 : par compte, N / N-1
    ca_totaux = (
        df_ca.groupby(["annee", "compte", "libelle"])["montant"]
        .sum()
        .reset_index()
        .pivot(index=["compte", "libelle"], columns="annee", values="montant")
        .fillna(0)
    )

    for a in [ANNEE_N, ANNEE_N_1]:
        if a not in ca_totaux.columns:
            ca_totaux[a] = 0

    ca_totaux = ca_totaux.reset_index().rename(
        columns={ANNEE_N: "N", ANNEE_N_1: "N_1"}
    )
    ca_totaux["Var"] = ca_totaux["N"] - ca_totaux["N_1"]
    ca_totaux["Var_%"] = np.where(
        ca_totaux["N_1"] != 0, ca_totaux["Var"] / ca_totaux["N_1"] * 100, 0
    )

    ca_totaux["N_fmt"] = ca_totaux["N"].map(fmt)
    ca_totaux["N1_fmt"] = ca_totaux["N_1"].map(fmt)
    ca_totaux["Var_fmt"] = ca_totaux["Var"].map(fmt)
    ca_totaux["Var_%_fmt"] = ca_totaux["Var_%"].map(lambda v: f"{v:.1f} %")

    st.markdown("### Niveau 1 – Comparatif par compte 707x")

    st.dataframe(
        ca_totaux[
            ["compte", "libelle", "N_fmt", "N1_fmt", "Var_fmt", "Var_%_fmt"]
        ].rename(
            columns={
                "compte": "Compte",
                "libelle": "Libellé",
                "N_fmt": f"N {ANNEE_N}",
                "N1_fmt": f"N-1 {ANNEE_N_1}",
                "Var_fmt": "Écart",
                "Var_%_fmt": "Écart %",
            }
        ),
        use_container_width=True,
    )

    st.markdown("### Niveau 2 – Graphiques Chiffre d'affaires")

    # Évolution mensuelle par compte & année
    st.markdown("**Évolution mensuelle par compte (N / N-1)**")
    df_ca_month = (
        df_ca.groupby(["annee", "periode", "compte"])["montant"]
        .sum()
        .reset_index()
    )

    chart_ca = (
        alt.Chart(df_ca_month)
        .mark_line(point=True)
        .encode(
            x=alt.X("periode:T", title="Mois"),
            y=alt.Y("montant:Q", title="CA HT"),
            color="compte:N",
            strokeDash="annee:N",
            tooltip=["annee", "compte", "periode", "montant"],
        )
        .properties(height=300)
    )

    st.altair_chart(chart_ca, use_container_width=True)

    # Double donut : structure du CA dans le total CA
    st.markdown("**Structure du CA par compte dans le total CA (N / N-1)**")

    tot_ca_by_year = (
        df_ca.groupby(["annee", "compte"])["montant"].sum().reset_index()
    )
    tot_ca_by_year["exercice"] = tot_ca_by_year["annee"].astype(str)

    donut_ca = (
        alt.Chart(tot_ca_by_year)
        .mark_arc(innerRadius=50)
        .encode(
            theta="montant:Q",
            color="compte:N",
            tooltip=["exercice", "compte", "montant"],
        )
        .properties(width=220, height=220)
        .facet(column="exercice:N")
    )

    st.altair_chart(donut_ca, use_container_width=True)

# =========================
# 5. DÉTAIL ACHATS – 607x
# =========================

if show_achats_detail:
    st.markdown("## 🔹 Détail Achats consommés")

    df_ach = df[df["type"] == "ACH"].copy()

    ach_totaux = (
        df_ach.groupby(["annee", "compte", "libelle"])["montant"]
        .sum()
        .reset_index()
        .pivot(index=["compte", "libelle"], columns="annee", values="montant")
        .fillna(0)
    )

    for a in [ANNEE_N, ANNEE_N_1]:
        if a not in ach_totaux.columns:
            ach_totaux[a] = 0

    ach_totaux = ach_totaux.reset_index().rename(
        columns={ANNEE_N: "N", ANNEE_N_1: "N_1"}
    )
    ach_totaux["Var"] = ach_totaux["N"] - ach_totaux["N_1"]
    ach_totaux["Var_%"] = np.where(
        ach_totaux["N_1"] != 0, ach_totaux["Var"] / ach_totaux["N_1"] * 100, 0
    )

    ach_totaux["N_fmt"] = ach_totaux["N"].map(fmt)
    ach_totaux["N1_fmt"] = ach_totaux["N_1"].map(fmt)
    ach_totaux["Var_fmt"] = ach_totaux["Var"].map(fmt)
    ach_totaux["Var_%_fmt"] = ach_totaux["Var_%"].map(lambda v: f"{v:.1f} %")

    st.markdown("### Niveau 1 – Comparatif par compte 607x")

    st.dataframe(
        ach_totaux[
            ["compte", "libelle", "N_fmt", "N1_fmt", "Var_fmt", "Var_%_fmt"]
        ].rename(
            columns={
                "compte": "Compte",
                "libelle": "Libellé",
                "N_fmt": f"N {ANNEE_N}",
                "N1_fmt": f"N-1 {ANNEE_N_1}",
                "Var_fmt": "Écart",
                "Var_%_fmt": "Écart %",
            }
        ),
        use_container_width=True,
    )

    st.markdown("### Niveau 2 – Évolution des achats")

    df_ach_month = (
        df_ach.groupby(["annee", "periode", "compte"])["montant"]
        .sum()
        .reset_index()
    )

    chart_ach = (
        alt.Chart(df_ach_month)
        .mark_line(point=True)
        .encode(
            x=alt.X("periode:T", title="Mois"),
            y=alt.Y("montant:Q", title="Achats"),
            color="compte:N",
            strokeDash="annee:N",
            tooltip=["annee", "compte", "periode", "montant"],
        )
        .properties(height=300)
    )

    st.altair_chart(chart_ach, use_container_width=True)

# =========================
# 6. DÉTAIL VARIATION DE STOCK – 603x
# =========================

if show_stock_detail:
    st.markdown("## 🔹 Détail Variation de stock")

    df_stk = df[df["type"] == "STK"].copy()

    stk_totaux = (
        df_stk.groupby(["annee", "compte", "libelle"])["montant"]
        .sum()
        .reset_index()
        .pivot(index=["compte", "libelle"], columns="annee", values="montant")
        .fillna(0)
    )

    for a in [ANNEE_N, ANNEE_N_1]:
        if a not in stk_totaux.columns:
            stk_totaux[a] = 0

    stk_totaux = stk_totaux.reset_index().rename(
        columns={ANNEE_N: "N", ANNEE_N_1: "N_1"}
    )
    stk_totaux["Var"] = stk_totaux["N"] - stk_totaux["N_1"]
    stk_totaux["Var_%"] = np.where(
        stk_totaux["N_1"] != 0, stk_totaux["Var"] / stk_totaux["N_1"] * 100, 0
    )

    stk_totaux["N_fmt"] = stk_totaux["N"].map(fmt)
    stk_totaux["N1_fmt"] = stk_totaux["N_1"].map(fmt)
    stk_totaux["Var_fmt"] = stk_totaux["Var"].map(fmt)
    stk_totaux["Var_%_fmt"] = stk_totaux["Var_%"].map(lambda v: f"{v:.1f} %")

    st.dataframe(
        stk_totaux[
            ["compte", "libelle", "N_fmt", "N1_fmt", "Var_fmt", "Var_%_fmt"]
        ].rename(
            columns={
                "compte": "Compte",
                "libelle": "Libellé",
                "N_fmt": f"N {ANNEE_N}",
                "N1_fmt": f"N-1 {ANNEE_N_1}",
                "Var_fmt": "Écart",
                "Var_%_fmt": "Écart %",
            }
        ),
        use_container_width=True,
    )

    df_stk_month = (
        df_stk.groupby(["annee", "periode", "compte"])["montant"]
        .sum()
        .reset_index()
    )

    chart_stk = (
        alt.Chart(df_stk_month)
        .mark_line(point=True)
        .encode(
            x=alt.X("periode:T", title="Mois"),
            y=alt.Y("montant:Q", title="Variation de stock"),
            color="annee:N",
            tooltip=["annee", "periode", "montant"],
        )
        .properties(height=300)
    )

    st.altair_chart(chart_stk, use_container_width=True)
