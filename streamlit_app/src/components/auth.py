import streamlit as st

def require_authentication() -> None:
    if st.user.is_logged_in:
        return

    st.title("Connexion requise")
    st.write("Connecte-toi avec Keycloak pour accéder au chatbot.")

    if st.button("Se connecter avec Keycloak"):
        st.login("keycloak")

    st.stop()

    
