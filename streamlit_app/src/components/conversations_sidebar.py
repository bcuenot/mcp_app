import streamlit as st
from src.services.mcp_client_api import McpClientApi, AuthenticationExpiredError, McpClientApiError
from src.components.chat import render_session_expired_dialog

def render_user_sidebar(mcp_client : McpClientApi) -> None:
    if st.session_state.get("session_expired", False):
        render_session_expired_dialog()
        st.stop()
    try:
        conversations = mcp_client.get_conversations()

    except AuthenticationExpiredError:
        render_session_expired_dialog()
        st.stop()

    except McpClientApiError as error:
        st.sidebar.error(str(error))

    with st.sidebar:
        st.sidebar.write(f"Connecté : {st.user.name}")
        st.header("Conversations", text_alignment="center")

        if st.button("Nouvelle conversation", use_container_width=True):
            st.session_state["current_conversation_id"] = None
            st.session_state["messages"] = []
            st.rerun()
        
        st.divider()
        for conversation in conversations:
            if st.button(label=conversation["title"], key=conversation["id"], use_container_width=True, type="tertiary"):
                try :
                    messages = mcp_client.get_messages_by_conversation_id(conversation_id=conversation["id"])
                    st.session_state["current_conversation_id"] = conversation["id"]
                    st.session_state["messages"] = messages
                    st.rerun()

                except AuthenticationExpiredError:
                    render_session_expired_dialog()
                    st.stop()

                except McpClientApiError as error:
                    st.sidebar.error(str(error))
        
        st.divider()
        if st.button("Se déconnecter", use_container_width=True):
            st.logout()
            st.rerun()