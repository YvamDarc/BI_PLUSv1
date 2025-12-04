import streamlit as st
import yaml
import streamlit_authenticator as stauth

st.set_page_config(page_title="BI+ – Admin utilisateurs", layout="wide")

# Charger la config depuis les secrets
config = yaml.safe_load(st.secrets["auth"]["config"])

# Authenticator
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

# Sécurité : accès seulement si connecté
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.switch_page("app.py")

username = st.session_state["username"]
user_info = config["credentials"]["usernames"][username]

# Sécurité : accès réservé admin
if user_info.get("role") != "admin":
    st.error("⛔ Accès réservé à l'administrateur.")
    st.stop()

authenticator.logout("Se déconnecter", "sidebar")

st.title("🛠 Administration des utilisateurs BI+")

st.markdown(
    """
    Cette page permet de :
    - Gérer la liste des utilisateurs
    - Ajouter un utilisateur (avec dossiers autorisés)
    - Modifier un utilisateur existant
    - Changer les mots de passe
    - Supprimer des utilisateurs
    - Générer automatiquement le bloc `[auth]` pour les Secrets Streamlit
    """
)

users = config["credentials"]["usernames"]

# -------------------------------------------------------
#  UTILITAIRE : Génération du bloc secrets
# -------------------------------------------------------
def afficher_bloc_secrets(config):
    yaml_str = yaml.safe_dump(
        config,
        sort_keys=False,
        allow_unicode=True
    )
    secrets_block = '[auth]\nconfig = """\n' + yaml_str + '\n"""'
    st.markdown("### 🔐 Nouveau bloc à copier dans Streamlit Secrets")
    st.code(secrets_block, language="toml")
    st.info("Copiez ce bloc dans les Secrets Streamlit et sauvegardez pour redémarrer l'application.")


# -------------------------------------------------------
# 1. Liste des utilisateurs
# -------------------------------------------------------
st.subheader("👥 Utilisateurs existants")

cols = st.columns([1, 2, 2, 1, 3])
cols[0].markdown("**Username**")
cols[1].markdown("**Nom**")
cols[2].markdown("**Email**")
cols[3].markdown("**Rôle**")
cols[4].markdown("**Dossiers Dropbox**")

for u, data in users.items():
    folders = ", ".join(data.get("dropbox_folders", []))
    row = st.columns([1, 2, 2, 1, 3])
    row[0].write(u)
    row[1].write(data.get("name", ""))
    row[2].write(data.get("email", ""))
    row[3].write(data.get("role", ""))
    row[4].write(folders)

st.markdown("---")

# -------------------------------------------------------
# 2. Ajouter un utilisateur
# -------------------------------------------------------
st.subheader("➕ Ajouter un utilisateur")

with st.form("add_user"):
    new_username = st.text_input("Username")
    new_name = st.text_input("Nom complet")
    new_email = st.text_input("Email")
    new_role = st.selectbox("Rôle", ["admin", "viewer"])
    new_folders = st.text_area(
        "Dossiers Dropbox autorisés (un par ligne)",
        placeholder="/BI_PLUS/clients/client_0001\n/BI_PLUS/clients/client_0002"
    )
    new_password = st.text_input("Mot de passe", type="password")
    new_password_confirm = st.text_input("Confirmer le mot de passe", type="password")
    add_submit = st.form_submit_button("Créer utilisateur")

if add_submit:
    if not new_username or not new_password:
        st.error("Username et mot de passe obligatoires.")
    elif new_password != new_password_confirm:
        st.error("Les mots de passe ne correspondent pas.")
    elif new_username in users:
        st.error("Ce username existe déjà.")
    else:
        folder_list = [f.strip() for f in new_folders.split("\n") if f.strip()]
        hash_pwd = stauth.Hasher().hash(new_password)

        config["credentials"]["usernames"][new_username] = {
            "email": new_email,
            "name": new_name,
            "password": hash_pwd,
            "role": new_role,
            "dropbox_folders": folder_list,
        }

        st.success(f"Utilisateur `{new_username}` ajouté.")
        afficher_bloc_secrets(config)

st.markdown("---")

# -------------------------------------------------------
# 3. Modifier un utilisateur
# -------------------------------------------------------
st.subheader("✏️ Modifier un utilisateur")

selected_user = st.selectbox("Choisir un utilisateur", list(users.keys()))

if selected_user:
    u = users[selected_user]

    with st.form("edit_user"):
        edit_name = st.text_input("Nom", value=u.get("name", ""))
        edit_email = st.text_input("Email", value=u.get("email", ""))
        edit_role = st.selectbox("Rôle", ["admin", "viewer"], index=0 if u.get("role") == "admin" else 1)
        edit_folders = st.text_area(
            "Dossiers Dropbox autorisés",
            value="\n".join(u.get("dropbox_folders", []))
        )

        st.markdown("#### 🔑 Modifier le mot de passe (optionnel)")
        edit_pwd = st.text_input("Nouveau mot de passe", type="password")
        edit_pwd2 = st.text_input("Confirmer le mot de passe", type="password")

        edit_submit = st.form_submit_button("Enregistrer")

    if edit_submit:
        if edit_pwd or edit_pwd2:
            if edit_pwd != edit_pwd2:
                st.error("Les nouveaux mots de passe ne correspondent pas.")
                st.stop()
            else:
                u["password"] = stauth.Hasher().hash(edit_pwd)

        u["name"] = edit_name
        u["email"] = edit_email
        u["role"] = edit_role
        u["dropbox_folders"] = [f.strip() for f in edit_folders.split("\n") if f.strip()]

        config["credentials"]["usernames"][selected_user] = u

        st.success(f"Utilisateur `{selected_user}` mis à jour.")
        afficher_bloc_secrets(config)

st.markdown("---")

# -------------------------------------------------------
# 4. Suppression d’un utilisateur
# -------------------------------------------------------
st.subheader("🗑 Supprimer un utilisateur")

delete_user = st.selectbox("Sélectionner l’utilisateur à supprimer", list(users.keys()), key="delete_user")

if delete_user == "admin":
    st.warning("Impossible de supprimer l'utilisateur admin.")
else:
    if st.button(f"⚠️ Supprimer {delete_user}"):
        users.pop(delete_user)
        config["credentials"]["usernames"] = users
        st.success(f"Utilisateur `{delete_user}` supprimé.")
        afficher_bloc_secrets(config)
        
