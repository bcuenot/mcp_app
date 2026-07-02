import streamlit as st


def require_authentication() -> None:
    if st.user.is_logged_in:
        return

    st.markdown(
        """
        <style>
        .login-container {
            min-height: 70vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .login-card {
            width: 100%;
            max-width: 460px;
            padding: 2.2rem 2rem;
            border: 1px solid var(--border-color);
            border-radius: 1rem;
            background-color: var(--secondary-background-color);
            box-shadow: 0 18px 45px rgba(0, 0, 0, 0.18);
            text-align: center;
        }

        .login-icon {
            width: 58px;
            height: 58px;
            margin: 0 auto 1.2rem auto;
            border-radius: 999px;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: color-mix(
                in srgb,
                var(--primary-color) 18%,
                transparent
            );
            color: var(--primary-color);
            font-size: 1.8rem;
        }

        .login-title {
            font-size: 1.8rem;
            font-weight: 750;
            margin-bottom: 0.5rem;
        }

        .login-subtitle {
            color: rgba(250, 250, 250, 0.72);
            font-size: 0.98rem;
            line-height: 1.5;
            margin-bottom: 1.7rem;
        }

        .login-footer {
            margin-top: 1.4rem;
            font-size: 0.82rem;
            color: rgba(250, 250, 250, 0.48);
        }

        div[data-testid="stButton"] > button {
            font-weight: 650;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="login-container">
            <div class="login-card">
                <div class="login-icon">🔐</div>
                <div class="login-title">Connexion requise</div>
                <div class="login-subtitle">
                    Connecte-toi avec ton compte Keycloak pour accéder
                    à ton chatbot MCP sécurisé.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, col_button, _ = st.columns([1, 2, 1])

    with col_button:
        if st.button(
            "Se connecter avec Keycloak",
            icon=":material/login:",
            width="stretch",
            type="primary",
        ):
            st.login("keycloak")

    st.markdown(
        """
        <p style="
            text-align: center;
            margin-top: 1rem;
            font-size: 0.82rem;
            opacity: 0.55;
        ">
            Authentification sécurisée via OpenID Connect
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.stop()