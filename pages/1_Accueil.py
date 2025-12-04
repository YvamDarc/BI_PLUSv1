import streamlit as st
import yaml

st.set_page_config(page_title="Accueil BI+", layout="centered")

# Charger config utilisateurs
config = yaml.safe_load(st.secrets["auth"]["config"])

# Sécurité : vérifier authentification
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.switch_page("app.py")

username = st.session_state["username"]
user_info = config["credentials"]["usernames"][username]
role = user_info.get("role", "viewer")

st.title("🏠 Accueil BI+")

# ------------------------------------------
# DÉTERMINATION DES DOSSIERS ACCESSIBLES
# ------------------------------------------
if role == "admin":
    # Admin = accès à tous les dossiers de tous les utilisateurs
    all_folders = []
    for u, info in config["credentials"]["usernames"].items():
        all_folders.extend(info.get("dropbox_folders", []))

    folders = sorted(set(all_folders))
else:
    # Viewer = seulement ses dossiers autorisés
    folders = user_info.get("dropbox_folders", [])

if not folders:
    st.error("Aucun dossier Dropbox autorisé pour cet utilisateur.")
    st.stop()

# ------------------------------------------
# SELECTEUR DE DOSSIER
# ------------------------------------------
if "selected_folder" not in st.session_state:
    st.session_state["selected_folder"] = folders[0]

selected_folder = st.selectbox(
    "📁 Sélection du dossier client",
    folders,
    index=folders.index(st.session_state["selected_folder"])
)

st.session_state["selected_folder"] = selected_folder

st.success(f"📂 Dossier actif : `{selected_folder}`")

st.markdown("---")

# Menu / boutons pour accès rapide
st.subheader("📊 Accès aux modules")
st.write("Utilisez la barre latérale pour accéder aux analyses et imports.")
