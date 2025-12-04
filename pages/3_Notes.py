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

# Chargement de la configuration
config = yaml.safe_load(st.secrets["auth"]["config"])

# Instancier l'authentificateur
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

# Authentification de l'utilisateur
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.warning("Vous devez vous connecter.")
    st.stop()

# Authentification réussie
authenticator.logout("Déconnexion", "sidebar")

# Récupérer l'utilisateur actuel
username = st.session_state["username"]

# Vérifier que l'utilisateur existe dans les credentials
if username not in config["credentials"]["usernames"]:
    st.error("Utilisateur non trouvé.")
    st.stop()

# Récupérer les informations de l'utilisateur
user_info = config["credentials"]["usernames"][username]

# Vérifier que 'dropbox_folders' existe dans l'info utilisateur
if "dropbox_folders" not in user_info:
    st.error(f"Les dossiers Dropbox ne sont pas définis pour l'utilisateur {username}.")
    st.stop()

# Récupérer le rôle et le dossier Dropbox de l'utilisateur
role = user_info["role"]
folders = user_info["dropbox_folders"]

# Sélectionner le premier dossier de la liste
folder = folders[0]

# Afficher les informations de l'utilisateur pour déboguer
st.write(f"Dossier Dropbox de l'utilisateur {username}: {folder}")

# Chemin vers le fichier des notes dans Dropbox
NOTES_PATH = folder + "/notes.md"

# Créer un client Dropbox
dbx = get_dropbox_client()

# Titre de la page
st.title("📝 Notes")

# Lire les notes depuis Dropbox
try:
    meta, res = dbx.files_download(NOTES_PATH)
    notes = res.content.decode("utf-8")
except dropbox.exceptions.ApiError as e:
    st.error(f"Erreur lors du téléchargement des notes : {e}")
    notes = ""  # Si l'erreur survient, on laisse les notes vides

# Affichage en fonction du rôle de l'utilisateur
if role == "admin":
    # L'administrateur peut modifier les notes
    edited = st.text_area("Éditer les notes", notes, height=300)
    if st.button("💾 Enregistrer"):
        try:
            dbx.files_upload(
                edited.encode("utf-8"),
                NOTES_PATH,
                mode=dropbox.files.WriteMode("overwrite")
            )
            st.success("Notes enregistrées.")
        except dropbox.exceptions.ApiError as e:
            st.error(f"Erreur lors de l'enregistrement des notes : {e}")
else:
    # Les lecteurs (utilisateurs avec rôle 'viewer') ne peuvent pas modifier les notes
    st.text_area("Notes (lecture seule)", notes, height=300, disabled=True)
    st.info("Vous n’avez pas les droits d’édition.")
