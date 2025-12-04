import streamlit as st
import yaml
import streamlit_authenticator as stauth
import dropbox
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Excel – BI+", layout="wide")

config = yaml.safe_load(st.secrets["auth"]["config"])

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

# Auth
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.switch_page("app.py")

authenticator.logout("Déconnexion", "sidebar")

username = st.session_state["username"]
user_info = config["credentials"]["usernames"][username]

folder = user_info["dropbox_folder"]
EXCEL_PATH = folder + "/dossiers/2023/essai_fec.xlsx"

dbx = dropbox.Dropbox(st.secrets["DROPBOX_TOKEN"])

st.title("📊 Excel – Données test")

try:
    meta, res = dbx.files_download(EXCEL_PATH)
    df = pd.read_excel(BytesIO(res.content))
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error(f"Erreur : {e}")
