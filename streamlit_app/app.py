import streamlit as st
from src.components.auth import require_authentication
from src.components.chat import render_chat
from src.components.conversations_sidebar import render_user_sidebar
from src.services.mcp_client_api import McpClientApi

def main():
    st.set_page_config(
        page_title="Chatbot MCP",
        page_icon="🤖",
    )

    require_authentication()

    mcp_client = McpClientApi()
    render_user_sidebar(mcp_client=mcp_client)
    render_chat(mcp_client=mcp_client)


if __name__ == "__main__":
    main()