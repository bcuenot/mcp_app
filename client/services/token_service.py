import os

import httpx


class TokenExchangeError(Exception):
    pass


class TokenService:
    def __init__(
        self,
        keycloak_token_url: str | None = None,
        mcp_client_id: str | None = None,
        mcp_client_secret: str | None = None,
        mcp_server_audience: str | None = None,
        timeout: float = 10,
    ):
        self.keycloak_token_url = keycloak_token_url or os.environ["KEYCLOAK_TOKEN_URL"]
        self.mcp_client_id = mcp_client_id or os.getenv("MCP_CLIENT_ID", "mcp-client")
        self.mcp_client_secret = mcp_client_secret or os.environ["MCP_CLIENT_SECRET"]
        self.mcp_server_audience = mcp_server_audience or os.getenv("MCP_SERVER_AUDIENCE", "mcp-server")
        self.timeout = timeout

    async def exchange_token_for_mcp(self, user_access_token: str) -> str:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.keycloak_token_url,
                    data={
                        "grant_type": (
                            "urn:ietf:params:oauth:"
                            "grant-type:token-exchange"
                        ),
                        "client_id": self.mcp_client_id,
                        "client_secret": self.mcp_client_secret,
                        "subject_token": user_access_token,
                        "subject_token_type": (
                            "urn:ietf:params:oauth:"
                            "token-type:access_token"
                        ),
                        "requested_token_type": (
                            "urn:ietf:params:oauth:"
                            "token-type:access_token"
                        ),
                        "audience": self.mcp_server_audience,
                    },
                    timeout=self.timeout,
                )

        except httpx.TimeoutException as error:
            raise TokenExchangeError(
                "Keycloak met trop de temps à répondre."
            ) from error

        except httpx.RequestError as error:
            raise TokenExchangeError(
                f"Impossible de joindre Keycloak : {error}"
            ) from error

        if response.status_code >= 400:
            raise TokenExchangeError(
                "Token exchange échoué : "
                f"{response.status_code} - {response.text}"
            )

        try:
            data = response.json()
        except ValueError as error:
            raise TokenExchangeError(
                "Keycloak a retourné une réponse JSON invalide."
            ) from error

        access_token = data.get("access_token")

        if not access_token:
            raise TokenExchangeError(
                "Réponse Keycloak invalide : "
                "champ access_token manquant."
            )

        return access_token