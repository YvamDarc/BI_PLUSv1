import streamlit as st
import yaml
import streamlit_authenticator as stauth

st.set_page_config(page_title="Accueil – BI+", layout="wide")

# Charger la config
config = yaml.safe_load(st.secrets["auth"]["config"])

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

# Vérifier login
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.switch_page("app.py")

authenticator.logout("Déconnexion", "sidebar")

st.title("🏠 Accueil BI+")

st.write("Bienvenue ! Choisissez une page :")
st.write("- 📊 Excel")
st.write("- 📝 Notes Markdown")
