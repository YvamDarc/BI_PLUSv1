import streamlit as st
import dropbox
import requests

# Fonction pour récupérer un access_token via le refresh_token
def get_fresh_access_token():
    token_url = "https://api.dropboxapi.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": st.secrets["DROPBOX_REFRESH_TOKEN"],
        "client_id": st.secrets["DROPBOX_CLIENT_ID"],
        "client_secret": st.secrets["DROPBOX_CLIENT_SECRET"],
    }
    response = requests.post(token_url, data=data)
    response.raise_for_status()  # Si l'API échoue, cela soulève une exception
    return response.json()["access_token"]

# Crée un client Dropbox
def get_dropbox_client():
    access_token = get_fresh_access_token()
    return dropbox.Dropbox(access_token)

# Tester la connexion
try:
    dbx = get_dropbox_client()

    # Test simple : obtenir des informations de compte
    account_info = dbx.users_get_current_account()
    
    # Afficher les infos de compte pour vérifier que la connexion fonctionne
    st.write("Connexion réussie ! Voici les infos de ton compte Dropbox :")
    st.write(account_info)

except dropbox.exceptions.AuthError as e:
    st.error(f"Échec de l'authentification Dropbox : {e}")
except Exception as e:
    st.error(f"Erreur inconnue lors de la connexion à Dropbox : {e}")
