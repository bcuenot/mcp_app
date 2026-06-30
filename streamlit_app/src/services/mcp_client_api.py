import os
import requests
import streamlit as st

MCP_CLIENT_API_URL = os.getenv("MCP_CLIENT_API_URL")

class McpClientApiError(Exception):
    pass

class AuthenticationExpiredError(McpClientApiError):
    pass

class McpClientApi:
    def __init__(self, base_url: str = MCP_CLIENT_API_URL, timeout: int = 120):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def send_message(self, prompt: str, conversation_id) -> str:
        access_token = st.user.tokens["access"]
        response = requests.post(
            f"{self.base_url}/chat",
            json={"message": prompt, "conversation_id" : conversation_id},
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=self.timeout
        )

        if response.status_code == 401:
            raise AuthenticationExpiredError(
                "Ta session a expiré. Reconnecte-toi pour continuer."
            )

        if response.status_code >= 400:
            raise McpClientApiError(
                "Erreur HTTP backend client MCP : "
                f"{response.status_code} - {response.text}"
            )

        response = response.json()

        return response
    
    def get_conversations(self) -> list[dict]:
        access_token = st.user.tokens["access"]
        response = requests.get(
            f"{self.base_url}/conversations",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=self.timeout
        )

        if response.status_code == 401:
            raise AuthenticationExpiredError(
                f"Authentification refusée : {response.text}"
            )

        if response.status_code >= 400:
            raise McpClientApiError(
                "Erreur HTTP backend client MCP : "
                f"{response.status_code} - {response.text}"
            )
        
        conversations = response.json()
    
        return conversations
    
    def get_messages_by_conversation_id(self, conversation_id : int) -> list[dict]:
        access_token = st.user.tokens["access"]
        response = requests.get(
            f"{self.base_url}/conversations/{conversation_id}/messages",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=self.timeout
        )

        if response.status_code == 401:
            raise AuthenticationExpiredError(
                f"Authentification refusée : {response.text}"
            )

        if response.status_code >= 400:
            raise McpClientApiError(
                "Erreur HTTP backend client MCP : "
                f"{response.status_code} - {response.text}"
            )
        
        messages = response.json()
    
        return messages
    
    def update_conversation_title(self, conversation_id : str, new_conversation_title : str) -> dict:
        access_token = st.user.tokens["access"]
        response = requests.patch(
            f"{self.base_url}/conversations/{conversation_id}",
            json={"new_conversation_title" : new_conversation_title},
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=self.timeout
        )

        if response.status_code == 401:
            raise AuthenticationExpiredError(
                f"Authentification refusée : {response.text}"
            )

        if response.status_code >= 400:
            raise McpClientApiError(
                "Erreur HTTP backend client MCP : "
                f"{response.status_code} - {response.text}"
            )
        
        response = response.json()
    
        return response
    
    def delete_conversation(self, conversation_id : str) -> str:
        access_token = st.user.tokens["access"]
        response = requests.delete(
            f"{self.base_url}/conversations/{conversation_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=self.timeout
        )

        if response.status_code == 401:
            raise AuthenticationExpiredError(
                f"Authentification refusée : {response.text}"
            )

        if response.status_code >= 400:
            raise McpClientApiError(
                "Erreur HTTP backend client MCP : "
                f"{response.status_code} - {response.text}"
            )
        
        response = response.json()
    
        return response