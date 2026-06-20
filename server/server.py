import os

from fastmcp import FastMCP
from fastmcp.dependencies import CurrentContext
from fastmcp.server.auth import restrict_tag
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.context import Context
from fastmcp.server.middleware import AuthMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware


KEYCLOAK_JWKS_URI = os.environ["KEYCLOAK_JWKS_URI"]
KEYCLOAK_ISSUER = os.environ["KEYCLOAK_ISSUER"]

MCP_AUDIENCE = os.getenv("MCP_AUDIENCE", "mcp-server")
MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_PORT", "8000"))


auth = JWTVerifier(
    jwks_uri=KEYCLOAK_JWKS_URI,
    issuer=KEYCLOAK_ISSUER,
    audience=MCP_AUDIENCE,
)

mcp = FastMCP("demo-server", auth=auth)

mcp.add_middleware(LoggingMiddleware())
mcp.add_middleware(AuthMiddleware(auth=restrict_tag("basic", scopes=["mcp:basic"])))
mcp.add_middleware(AuthMiddleware(auth=restrict_tag("admin", scopes=["mcp:admin"])))


@mcp.tool(tags={"basic"})
async def addition(a: int, b: int, ctx: Context = CurrentContext()) -> int:
    await ctx.info(f"Appel addition avec a={a}, b={b}")
    return a + b

@mcp.tool(tags={"basic"})
async def bonjour(nom: str, ctx: Context = CurrentContext()) -> str:
    await ctx.info(f"Bonjour demandé pour {nom}")
    return f"Bonjour {nom} 👋"

@mcp.tool(tags={"admin"})
async def multiplication(a: int, b: int, ctx: Context = CurrentContext()) -> int:
    await ctx.info(f"Multiplication demandée : {a} * {b}")
    return a * b

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host=MCP_HOST,
        port=MCP_PORT,
    )