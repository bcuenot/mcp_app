import os

import jwt
from jwt import PyJWKClient
from jwt.exceptions import (
    ExpiredSignatureError,
    PyJWKClientConnectionError,
    PyJWTError,
)

class AuthenticationError(Exception):
    pass


class AuthenticationExpiredError(AuthenticationError):
    pass


class AuthenticationServerUnavailableError(Exception):
    pass

class AuthService:
    def __init__(self):
        self.jwks_client = PyJWKClient(os.environ["KEYCLOAK_JWKS_URI"])
        self.issuer = os.environ["KEYCLOAK_ISSUER"]
        self.audience = os.environ["MCP_CLIENT_AUDIENCE"]

    def get_user_id(self, access_token: str) -> str:
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(
                access_token
            )

            claims = jwt.decode(
                access_token,
                signing_key.key,
                algorithms=["RS256"],
                issuer=self.issuer,
                audience=self.audience,
            )

        except PyJWKClientConnectionError as error:
            raise AuthenticationServerUnavailableError(
                "Keycloak est temporairement indisponible."
            ) from error

        except ExpiredSignatureError as error:
            raise AuthenticationExpiredError(
                "Le token a expiré. Une reconnexion est nécessaire."
            ) from error

        except PyJWTError as error:
            raise AuthenticationError(
                "Le token est invalide."
            ) from error

        user_id = claims.get("sub")

        if not user_id:
            raise AuthenticationError(
                "Le token ne contient pas de claim sub."
            )

        return user_id