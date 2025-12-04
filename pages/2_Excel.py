import streamlit as st
import yaml
import streamlit_authenticator as stauth
import dropbox
import requests
import pandas as pd
from io import BytesIO

# Fonction pour récupérer un access token via le refresh token
def get_fresh_access_token():
    """
    Récupère un nouveau access_token via le refresh_token Dropbox.
    """
    token_url = "https://api.dropboxapi.com/oauth2/token"

    data = {
        "grant_type": "refresh_token",
        "refresh_token": st.secrets["DROPBOX_REFRESH_TOKEN"],
        "client_id": st.secrets["DROPBOX_CLIENT_ID"],
        "client_secret": st.secrets["DROPBOX_CLIENT_SECRET"],
    }

    response = requests.post(token_url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

# Crée un client Dropbox avec un access token valide
@st.cache_resource(show_spinner=False)
def get_dropbox_client():
    """
    Crée un client Dropbox toujours valide.
    """
    access_token = get_fresh_access_token()
    return dropbox.Dropbox(access_token)

# Assurer que l'utilisateur est connecté
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.warning("Vous devez vous connecter.")
    st.stop()

# Sélectionner le dossier à utiliser
if "selected_folder" not in st.session_state:
    st.error("Aucun dossier sélectionné. Retournez à l'accueil.")
    st.stop()

folder = st.session_state["selected_folder"]

# Affichage du titre
st.title("📊 Données Excel")

# Récupérer le client Dropbox
dbx = get_dropbox_client()

# Récupérer le chemin du fichier Excel dans Dropbox
excel_path = f"{folder}/dossier/2023/essai_fec.xlsx"  # Remplace ce chemin selon ton organisation

# Tentative de téléchargement du fichier depuis Dropbox
try:
    metadata, res = dbx.files_download(excel_path)
    # Lire le contenu Excel
    df = pd.read_excel(BytesIO(res.content))
    st.dataframe(df, use_container_width=True)
except dropbox.exceptions.ApiError as e:
    st.error(f"Erreur lors du téléchargement du fichier : {e}")
except Exception as e:
    st.error(f"Erreur inconnue : {e}")
