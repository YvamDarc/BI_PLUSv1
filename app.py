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
DROPBOX_TOKEN = "sl.u.AGKEzGp3_THAY3NpbIqujcRy9Tvah_6Ja0sDFbU0UGJsi7VN52AyI9Mf9sC8k3GNINmgrUqX2D91t6LugQe0dhQJaqLpAO3jXhXj9zL0VcB1c-ycaRXyhFhhkifSBr8MrMglevkUJE5TSMWbp0O6CcYzuuHCyT1_u5hBA9lUQwgI74K5nxgForiT4VcQdG_jhVmKouNaX2Qse6xJhWTPaH0G5lSJNqSomF73mJAYGzQq2EHxgny1gBDfz35FSidmr6LTI6IMOBXWxfexM5Qnb-KrRkHMWcPAKUZ2GsUGABjaCFJwUY_X7xEpfaJ50DhuXQeblXlfCsK7PU6GYJauNnFswSLN8trTsL8J_9HTjFRAOd9kDu9DfyvISnftSNV9oU3asMcM7-XPPg8BgK5Mp3Oo3V1Ka6ZMc-JDxGlEiz5JxeZ6_bA531mm-AgdWDKqPTTbUrgQFEr0A--6t1dUjDYoPwdURanGqos0PfURcjjhP5LrfWPzAl-l6fdKmLepQBBqUU0VUKkI5S7qMIk6z60zL4TgEtRnq_iLRejMATW8eNRQM7vGTPmNIpj0DVGKXoKarTmJly9XbsmQYFlhMzy8yNPNMn_JbUdWDH9q3ABrsaNi7a7TRlkTIHw5ovgU2nj_B3LdTc78dH7DXmRun6mhfhs6S6gfum2jnK15kUaLbzFRSd8vePvME8tTL8aFgJsVrK7LFWrVZIiyic7WqVncAmAQnUIznRoiRzYyiQaaOFyJLfb3IA7tvLihDa8G6kXyw8KNAmBqYab57efuvZ-LU7pRTPTq8pFGOCF8DVKPgswowL5ZwQ8_c3NvwcXf2wEdN0vTq18uv5kFE6MfkbZfyi_566p8UuBchK7g7lKiU1MrN16c1PaJNheQYhy1q6GuwYmUZlp6Q5eLa1fvXFyyXT7y6CvBabCG2BXf9I3hFevgjzjgyRMLA2iGCrmiuMLUvECpm6V1c2PdB-0kFSd08YKTUP1Mxmf7nEpnMEJcrkrUph_ZpmImQup618QlfJ-FmZMYeRNs1nHwBqi1HAKaOUqQEcgb83gsQLC396n99cEracQgmEz6OoxdebfKqt-gQAvRJxGo1kog_y3p6FGFAe6W6o76geeiqhnqLizYEe2bsbCApjRcpHQDvlDJOI9GESPDvijznQ8ZhwQXJBYe4WQpdDExe4A_F4iQQ9tnjUzlZG6i08KKywfO2s2XNDow9Uh_DFvVFyhsqNXckHLB1yeFISREkZ1tar133vLWmPiqVGcGYF9rB07SYIfgEZs"  # TODO: à remplacer par ton vrai token
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

    # Initialisation
    if "auth_user" not in st.session_state:
        st.session_state["auth_user"] = None
        st.session_state["auth_failed"] = False

    # Si déjà connecté → ne pas bloquer
    if st.session_state["auth_user"]:
        return st.session_state["auth_user"]

    # Formulaire de connexion
    username = st.sidebar.text_input("Utilisateur", key="user_input")
    password = st.sidebar.text_input("Mot de passe", type="password", key="pass_input")

    if st.sidebar.button("Se connecter"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state["auth_user"] = username
            st.session_state["auth_failed"] = False
            st.rerun()
        else:
            st.session_state["auth_failed"] = True

    # Message d'erreur en cas d'échec
    if st.session_state["auth_failed"]:
        st.sidebar.error("Identifiants incorrects.")

    # NE PAS STOPPER L'APP ! → on affiche un message et on laisse vivre
    st.write("Veuillez vous connecter depuis la barre latérale.")
    st.stop()



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
