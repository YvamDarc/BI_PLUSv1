import streamlit as st
import yaml
import streamlit_authenticator as stauth

# Configuration de la page
st.set_page_config(page_title="BI+ – Connexion", layout="centered")

# Charger la config d'auth depuis les secrets (YAML embarqué)
config = yaml.safe_load(st.secrets["auth"]["config"])

# Initialiser l'authenticator
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

# Interface de connexion
st.title("🔐 BI+ – Connexion")
authenticator.login(location="main")

# Récupération de la session
name = st.session_state.get("name")
auth_status = st.session_state.get("authentication_status")
username = st.session_state.get("username")

# Gestion des états de connexion
if auth_status is False:
    st.error("Identifiants incorrects.")
elif auth_status is None:
    st.warning("Veuillez entrer vos identifiants.")
elif auth_status:
    authenticator.logout("Se déconnecter", "sidebar")
    st.success(f"Bienvenue {name} !")
    st.switch_page("pages/1_Accueil.py")
