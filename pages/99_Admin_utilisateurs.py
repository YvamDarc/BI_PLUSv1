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
    - Ajouter un nouvel utilisateur (avec mot de passe)
    - Générer le bloc `secrets` à copier-coller dans Streamlit Cloud.
    
    ⚠️ Les mots de passe existants ne peuvent pas être retrouvés (hash irréversible).
    """
)

# -----------------------------
# 1. Liste des utilisateurs existants
# -----------------------------
st.subheader("👥 Utilisateurs actuels")

users = config["credentials"]["usernames"]

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

# -----------------------------
# 2. Formulaire d'ajout de nouvel utilisateur
# -----------------------------
st.subheader("➕ Ajouter un nouvel utilisateur")

with st.form("add_user_form"):
    new_username = st.text_input("Username (identifiant de connexion)")
    new_name = st.text_input("Nom complet")
    new_email = st.text_input("Email")
    new_role = st.selectbox("Rôle", ["admin", "viewer"])
    new_dropbox_folder = st.text_input("Dossier Dropbox associé", value="/BI_PLUS/clients/client_xxxx")
    new_password = st.text_input("Mot de passe", type="password")
    new_password_confirm = st.text_input("Confirmer le mot de passe", type="password")

    submitted = st.form_submit_button("Ajouter l'utilisateur")

if submitted:
    # Quelques validations simples
    if not new_username or not new_password:
        st.error("Username et mot de passe sont obligatoires.")
    elif new_password != new_password_confirm:
        st.error("Les deux mots de passe ne correspondent pas.")
    elif new_username in users:
        st.error("Ce username existe déjà.")
    else:
        # Générer le hash du mot de passe
        hashed_pwd = stauth.Hasher().hash(new_password)

        # Ajouter l'utilisateur à la config en mémoire
        config["credentials"]["usernames"][new_username] = {
            "email": new_email,
            "name": new_name,
            "password": hashed_pwd,
            "role": new_role,
            "dropbox_folder": new_dropbox_folder,
        }

        st.success(f"Utilisateur `{new_username}` ajouté à la configuration.")

        # -----------------------------
        # 3. Générer le bloc secrets à copier
        # -----------------------------
        st.markdown("### 🔐 Nouveau bloc à copier dans les *Secrets* Streamlit")

        yaml_str = yaml.safe_dump(
            config,
            sort_keys=False,
            allow_unicode=True
        )

        secrets_block = '[auth]\nconfig = """\n' + yaml_str + '\n"""'
        st.code(secrets_block, language="toml")

        st.info(
            "Copiez ce bloc, remplacez votre section `[auth]` actuelle dans les `Secrets` Streamlit, "
            "puis redémarrez l'application."
        )
