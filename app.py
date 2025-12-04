import streamlit as st
import pandas as pd
import dropbox
from io import BytesIO

# -----------------------------
# CONFIG STREAMLIT
# -----------------------------
st.set_page_config(page_title="BI+ – Test Dropbox", layout="wide")


# -----------------------------
# PARAMÈTRES DROBOX (POC)
# -----------------------------
DROPBOX_TOKEN = "TON_TOKEN_DROPBOX_ICI"  # TODO: à remplacer par ton vrai token
CLIENT_FOLDER = "/BI_PLUS/clients/client_0001"
EXCEL_PATH = CLIENT_FOLDER + "/dossiers/2023/essai_fec.xlsx"
NOTES_PATH = CLIENT_FOLDER + "/notes.md"


@st.cache_resource
def get_dropbox_client():
    return dropbox.Dropbox(DROPBOX_TOKEN)


# -----------------------------
# AUTHENTIFICATION ULTRA SIMPLE
# -----------------------------
USERS = {
    "admin": {
        "password": "admin123",
        "can_edit": True,
    },
    "lecteur": {
        "password": "lecteur123",
        "can_edit": False,
    },
}


def login():
    st.sidebar.header("🔐 Connexion")

    if "auth_user" not in st.session_state:
        st.session_state["auth_user"] = None

    if st.session_state["auth_user"] is None:
        username = st.sidebar.text_input("Utilisateur")
        password = st.sidebar.text_input("Mot de passe", type="password")
        if st.sidebar.button("Se connecter"):
            if username in USERS and USERS[username]["password"] == password:
                st.session_state["auth_user"] = username
                st.sidebar.success(f"Connecté en tant que {username}")
            else:
                st.sidebar.error("Identifiants incorrects.")
        st.stop()
    else:
        user = st.session_state["auth_user"]
        st.sidebar.success(f"Connecté : {user}")
        if st.sidebar.button("Se déconnecter"):
            st.session_state["auth_user"] = None
            st.experimental_rerun()

    return st.session_state["auth_user"]


# -----------------------------
# FONCTIONS DROPBOX
# -----------------------------
def read_excel_from_dropbox(path: str) -> pd.DataFrame:
    dbx = get_dropbox_client()
    metadata, res = dbx.files_download(path)
    data = res.content
    return pd.read_excel(BytesIO(data))


def read_markdown_from_dropbox(path: str) -> str:
    dbx = get_dropbox_client()
    try:
        metadata, res = dbx.files_download(path)
        return res.content.decode("utf-8")
    except dropbox.exceptions.ApiError as e:
        return f"# Fichier introuvable\n\n{e}"


def write_markdown_to_dropbox(path: str, content: str):
    dbx = get_dropbox_client()
    dbx.files_upload(
        content.encode("utf-8"),
        path,
        mode=dropbox.files.WriteMode("overwrite"),
    )


# -----------------------------
# APP PRINCIPALE
# -----------------------------
def main():
    user = login()
    can_edit = USERS[user]["can_edit"]

    st.title("📊 BI+ – Test Dropbox (Excel + Notes)")

    # ----- 1. Lecture Excel -----
    st.subheader("1️⃣ Fichier Excel d'essai")
    try:
        df = read_excel_from_dropbox(EXCEL_PATH)
        st.success(f"Excel chargé depuis : `{EXCEL_PATH}`")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier Excel : {e}")

    st.markdown("---")

    # ----- 2. Notes Markdown -----
    st.subheader("2️⃣ Notes (Markdown) du client")

    notes_contenu = read_markdown_from_dropbox(NOTES_PATH)

    if can_edit:
        notes_edited = st.text_area(
            "Contenu des notes (modifiable) :", notes_contenu, height=300
        )
        if st.button("💾 Enregistrer les notes dans Dropbox"):
            try:
                write_markdown_to_dropbox(NOTES_PATH, notes_edited)
                st.success("Notes mises à jour dans Dropbox.")
            except Exception as e:
                st.error(f"Erreur lors de l'écriture des notes : {e}")
    else:
        st.info("Mode lecture seule (utilisateur sans droit d'édition).")
        st.text_area(
            "Contenu des notes (lecture seule) :",
            notes_contenu,
            height=300,
            disabled=True,
        )


if __name__ == "__main__":
    main()
