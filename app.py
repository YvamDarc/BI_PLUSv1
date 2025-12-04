import streamlit as st
import yaml
import streamlit_authenticator as stauth

st.set_page_config(page_title="BI+ – Connexion", layout="centered")

# Charger la config d'auth depuis les secrets
config = yaml.safe_load(st.secrets["auth"]["config"])

# (Tu peux commenter ces lignes une fois que tout marche)
st.write("CONFIG TROUVÉ :", "auth" in st.secrets)
st.write("UTILISATEURS CHARGÉS :", list(config["credentials"]["usernames"].keys()))

# Créer l'authenticator
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

st.title("🔐 BI+ – Connexion")

# Afficher le formulaire de connexion dans la zone principale
authenticator.login(location="main")

# Récupérer les infos de session
name = st.session_state.get("name")
auth_status = st.session_state.get("authentication_status")
username = st.session_state.get("username")

# Gestion des états de connexion
if auth_status is False:
    st.error("Identifiants incorrects.")
elif auth_status is None:
    st.warning("Veuillez entrer vos identifiants.")
elif auth_status:
    # Bouton de déconnexion dans la sidebar
    authenticator.logout("Se déconnecter", "sidebar")
    st.success(f"Bienvenue {name} !")
    st.switch_page("pages/1_Accueil.py")
