import streamlit as st
import yaml
import streamlit_authenticator as stauth

st.set_page_config(page_title="BI+ – Admin utilisateurs", layout="wide")

# Charger la config actuelle depuis les secrets
config = yaml.safe_load(st.secrets["auth"]["config"])

# Recréer l'authenticator (comme dans les autres pages)
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

# Vérifier que quelqu'un est connecté, sinon retour login
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.switch_page("app.py")

username = st.session_state["username"]
user_info = config["credentials"]["usernames"][username]

# Vérifier le rôle : seulement admin
if user_info.get("role") != "admin":
    st.error("⛔ Cette page est réservée à l'administrateur.")
    st.stop()

# Bouton de déconnexion
authenticator.logout("Se déconnecter", "sidebar")

st.title("🛠 Administration des utilisateurs BI+")

st.markdown(
    """
    Cette page permet de :
    - Voir la liste des utilisateurs configurés
    - Ajouter un nouvel utilisateur
    - Modifier un utilisateur existant (dont le mot de passe)
    - Supprimer un utilisateur

    ⚠️ Après chaque modification, il faudra :
    1. Copier le bloc `[auth]` généré,
    2. Le coller dans les *Secrets* Streamlit,
    3. Sauvegarder pour redémarrer l'application.
    """
)

users = config["credentials"]["usernames"]

# ----------------------------------------------------
# 1. Liste des utilisateurs existants
# ----------------------------------------------------
st.subheader("👥 Utilisateurs actuels")

cols = st.columns([1, 2, 2, 1, 3])
cols[0].markdown("**Username**")
cols[1].markdown("**Nom**")
cols[2].markdown("**Email**")
cols[3].markdown("**Rôle**")
cols[4].markdown("**Dossier Dropbox**")

for u, data in users.items():
    cols = st.columns([1, 2, 2, 1, 3])
    cols[0].write(u)
    cols[1].write(data.get("name", ""))
    cols[2].write(data.get("email", ""))
    cols[3].write(data.get("role", ""))
    cols[4].write(data.get("dropbox_folder", ""))

st.markdown("---")

# Petite fonction utilitaire pour générer un bloc secrets
def afficher_bloc_secrets(config):
    yaml_str = yaml.safe_dump(
        config,
        sort_keys=False,
        allow_unicode=True
    )
    secrets_block = '[auth]\nconfig = """\n' + yaml_str + '\n"""'
    st.markdown("### 🔐 Nouveau bloc à copier dans les *Secrets* Streamlit")
    st.code(secrets_block, language="toml")
    st.info(
        "Copiez ce bloc, remplacez votre section `[auth]` actuelle dans les `Secrets` Streamlit, "
        "puis sauvegardez pour redémarrer l'application."
    )

# ----------------------------------------------------
# 2. Ajout d'un nouvel utilisateur
# ----------------------------------------------------
st.subheader("➕ Ajouter un nouvel utilisateur")

with st.form("add_user_form"):
    new_username = st.text_input("Username (identifiant de connexion)")
    new_name = st.text_input("Nom complet")
    new_email = st.text_input("Email")
    new_role = st.selectbox("Rôle", ["admin", "viewer"], key="add_role")
    new_dropbox_folder = st.text_input("Dossier Dropbox associé", value="/BI_PLUS/clients/client_xxxx")
    new_password = st.text_input("Mot de passe", type="password")
    new_password_confirm = st.text_input("Confirmer le mot de passe", type="password")

    submitted_add = st.form_submit_button("✅ Ajouter l'utilisateur")

if submitted_add:
    if not new_username or not new_password:
        st.error("Username et mot de passe sont obligatoires.")
    elif new_password != new_password_confirm:
        st.error("Les deux mots de passe ne correspondent pas.")
    elif new_username in users:
        st.error("Ce username existe déjà.")
    else:
        hashed_pwd = stauth.Hasher().hash(new_password)
        config["credentials"]["usernames"][new_username] = {
            "email": new_email,
            "name": new_name,
            "password": hashed_pwd,
            "role": new_role,
            "dropbox_folder": new_dropbox_folder,
        }
        st.success(f"Utilisateur `{new_username}` ajouté à la configuration.")
        afficher_bloc_secrets(config)

st.markdown("---")

# ----------------------------------------------------
# 3. Modification d'un utilisateur existant
# ----------------------------------------------------
st.subheader("✏️ Modifier un utilisateur existant")

usernames_list = list(users.keys())
selected_user = st.selectbox("Choisir l'utilisateur à modifier", usernames_list, key="edit_select")

if selected_user:
    u_data = users[selected_user]

    with st.form("edit_user_form"):
        edit_name = st.text_input("Nom complet", value=u_data.get("name", ""))
        edit_email = st.text_input("Email", value=u_data.get("email", ""))
        edit_role = st.selectbox("Rôle", ["admin", "viewer"], index=0 if u_data.get("role") == "admin" else 1, key="edit_role")
        edit_dropbox = st.text_input("Dossier Dropbox associé", value=u_data.get("dropbox_folder", ""))

        st.markdown("#### 🔑 Changer le mot de passe (optionnel)")
        edit_new_password = st.text_input("Nouveau mot de passe (laisser vide pour ne pas changer)", type="password")
        edit_new_password_confirm = st.text_input("Confirmer le nouveau mot de passe", type="password")

        submitted_edit = st.form_submit_button("💾 Enregistrer les modifications")

    if submitted_edit:
        if edit_new_password or edit_new_password_confirm:
            if edit_new_password != edit_new_password_confirm:
                st.error("Les deux nouveaux mots de passe ne correspondent pas.")
            else:
                new_hash = stauth.Hasher().hash(edit_new_password)
                u_data["password"] = new_hash

        u_data["name"] = edit_name
        u_data["email"] = edit_email
        u_data["role"] = edit_role
        u_data["dropbox_folder"] = edit_dropbox

        config["credentials"]["usernames"][selected_user] = u_data
        st.success(f"Utilisateur `{selected_user}` mis à jour.")
        afficher_bloc_secrets(config)

st.markdown("---")

# ----------------------------------------------------
# 4. Suppression d'un utilisateur
# ----------------------------------------------------
st.subheader("🗑 Supprimer un utilisateur")

user_to_delete = st.selectbox("Choisir l'utilisateur à supprimer", usernames_list, key="delete_select")

if user_to_delete:
    if user_to_delete == username:
        st.warning("Vous ne pouvez pas supprimer l'utilisateur actuellement connecté.")
    elif user_to_delete == "admin":
        st.warning("Par sécurité, la suppression de l'utilisateur 'admin' est bloquée.")
    else:
        if st.button(f"⚠️ Confirmer la suppression de `{user_to_delete}`"):
            users.pop(user_to_delete, None)
            config["credentials"]["usernames"] = users
            st.success(f"Utilisateur `{user_to_delete}` supprimé de la configuration.")
            afficher_bloc_secrets(config)
