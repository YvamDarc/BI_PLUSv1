import streamlit as st
import yaml
import streamlit_authenticator as stauth
import dropbox

st.set_page_config(page_title="Notes – BI+", layout="wide")

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

role = user_info["role"]
folder = user_info["dropbox_folder"]

NOTES_PATH = folder + "/notes.md"

dbx = dropbox.Dropbox(st.secrets["DROPBOX_TOKEN"])

st.title("📝 Notes")

# Lire notes
try:
    meta, res = dbx.files_download(NOTES_PATH)
    notes = res.content.decode("utf-8")
except:
    notes = ""

if role == "admin":
    edited = st.text_area("Éditer les notes", notes, height=300)
    if st.button("💾 Enregistrer"):
        dbx.files_upload(
            edited.encode("utf-8"),
            NOTES_PATH,
            mode=dropbox.files.WriteMode("overwrite")
        )
        st.success("Notes enregistrées.")
else:
    st.text_area("Notes (lecture seule)", notes, height=300, disabled=True)
    st.info("Vous n’avez pas les droits d’édition.")

