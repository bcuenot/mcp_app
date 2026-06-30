import streamlit as st
from src.services.mcp_client_api import AuthenticationExpiredError, McpClientApi, McpClientApiError

@st.dialog("Session expirée")
def render_session_expired_dialog() -> None:
    st.write("Ta session a expiré. Reconnecte-toi pour continuer.")
    if st.button("Se reconnecter", use_container_width=True):
        st.logout()

def render_chat(mcp_client : McpClientApi) -> None:
    st.title("Chatbot MCP", text_alignment="center")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    conversation_id = st.session_state.get("current_conversation_id", None)
        
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Le client MCP réfléchit..."):
                try:
                    response = mcp_client.send_message(prompt=prompt, conversation_id=conversation_id)
                    if conversation_id is None:
                        conversation_id = response["conversation_id"]
                        st.session_state.current_conversation_id = conversation_id
                    st.markdown(response["message"])

                    
                except AuthenticationExpiredError:
                    render_session_expired_dialog()
                    st.stop()

                except McpClientApiError as error:
                    response = str(error)
                    st.error(response)

                except Exception as error:
                    response = f"Erreur inattendue : {type(error).__name__}: {error}"
                    st.error(response)

        st.session_state.messages.append({"role": "assistant", "content": response["message"]})