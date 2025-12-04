import streamlit as st
import yaml
import streamlit_authenticator as stauth

st.set_page_config(page_title="BI+ – Connexion", layout="centered")

# Charger le fichier config depuis Streamlit Secrets
config = yaml.safe_load(st.secrets["auth"]["config"])

# Instantiate authenticator
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

st.title("🔐 BI+ – Connexion")

name, auth_status, username = authenticator.login("Se connecter", "main")


# ---------- LOGIQUE ----------
if auth_status is False:
    st.error("Identifiants incorrects.")

elif auth_status is None:
    st.warning("Veuillez entrer vos identifiants.")

elif auth_status:
    authenticator.logout("Se déconnecter", "sidebar")
    st.success(f"Bienvenue {name} !")
    st.switch_page("pages/1_Accueil.py")
