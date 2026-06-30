import streamlit as st
from src.services.mcp_client_api import McpClientApi, AuthenticationExpiredError, McpClientApiError
from src.components.chat import render_session_expired_dialog

st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] div[data-testid="stButton"] {
        margin-bottom: -0.35rem;
    }

    section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
        padding-top: 0.15rem;
        padding-bottom: 0.15rem;
        min-height: 1.8rem;
        line-height: 1.1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def submit_conversation_rename(mcp_client: McpClientApi, conversation_id: str, input_key: str) -> None:
    new_conversation_title : str = st.session_state[input_key].strip()

    if not new_conversation_title:
        st.session_state["rename_error"] = "Le titre ne peut pas être vide"
        return

    try:
        mcp_client.update_conversation_title(
            conversation_id=conversation_id,
            new_conversation_title=new_conversation_title,
        )

        st.session_state["renaming_conversation_id"] = None
        st.session_state["rename_error"] = None

    except AuthenticationExpiredError:
        render_session_expired_dialog()
        st.stop()

    except McpClientApiError as error:
        st.sidebar.error(str(error))

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
        st.header("Conversations", text_alignment="center")

        if st.button("Nouvelle conversation", use_container_width=True, icon=":material/add_comment:"):
            st.session_state["current_conversation_id"] = None
            st.session_state["messages"] = []
            st.rerun()
        
        st.divider()
        
        if "renaiming_conversation_id" not in st.session_state:
            st.session_state["renaiming_conversation_id"] = None

        for conversation in conversations:
            col_name, col_menu = st.columns([5,1])
            with col_name:
                is_renaiming = (st.session_state.get("renaiming_conversation_id") == conversation["id"])

                if is_renaiming:
                    st.text_input(
                        label="Nouveau titre", 
                        value=conversation["title"], 
                        key=f"rename_input_{conversation['id']}",
                        label_visibility="collapsed",
                        on_change=submit_conversation_rename,
                        args=(
                            mcp_client,
                            conversation["id"],
                            f"rename_input_{conversation['id']}",
                        ),
                    )
                    st.session_state["renaiming_conversation_id"] = None

                else:
                    if st.button(label=conversation["title"], key=conversation["id"], type="tertiary"):
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
            
            with col_menu:
                with st.popover("", width="content", type="tertiary"):
                    if st.button(label="Renommer", key=f"rename_{conversation['id']}", width="stretch", icon=":material/edit:"):
                        st.session_state["renaiming_conversation_id"] = conversation["id"]
                        st.rerun()
    
                    if st.button(label="Supprimer",key=f"delete_{conversation['id']}", width="stretch", icon=":material/delete:"):
                        st.markdown("Hello")
        
        st.divider()
        if st.button("Se déconnecter", use_container_width=True, icon=":material/logout:"):
            st.logout()
            st.rerun()