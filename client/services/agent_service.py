import os

from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient


class AgentServiceError(Exception):
    pass


class AgentService:
    def __init__(
        self,
        google_api_key: str | None = None,
        mcp_server_url: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        system_prompt: str = (
            "Tu es un assistant utile. "
            "Tu peux utiliser les outils MCP disponibles "
            "quand c'est pertinent. "
            "Réponds en français."
        ),
    ):
        google_api_key = google_api_key or os.environ["GOOGLE_API_KEY"]
        self.mcp_server_url = mcp_server_url or os.environ["MCP_SERVER_URL"]
        self.system_prompt = system_prompt
        model_name = model or os.getenv("LLM_MODEL","gemini-2.5-flash")
        model_temperature = (
            temperature
            if temperature is not None
            else float(os.getenv("LLM_TEMPERATURE", "0.7"))
        )

        self._llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=google_api_key,
            temperature=model_temperature,
        )

    def _build_mcp_client(self, mcp_access_token: str) -> MultiServerMCPClient:
        return MultiServerMCPClient(
            {
                "math": {
                    "url": self.mcp_server_url,
                    "transport": "streamable_http",
                    "headers": {
                        "Authorization": (
                            f"Bearer {mcp_access_token}"
                        ),
                    },
                }
            }
        )

    @staticmethod
    def _extract_response_text(response: dict) -> str:
        messages = response.get("messages")

        if not messages:
            raise AgentServiceError(
                "La réponse de l'agent ne contient aucun message."
            )

        content = messages[-1].content

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            texts: list[str] = []

            for item in content:
                if isinstance(item, dict) and "text" in item:
                    texts.append(str(item["text"]))
                else:
                    texts.append(str(item))

            return "\n".join(texts)

        return str(content)

    async def ask(self, message: str, mcp_access_token: str) -> str:
        try:
            client = self._build_mcp_client(mcp_access_token)
            tools = await client.get_tools()
            agent = create_agent(self._llm, tools=tools, system_prompt=self.system_prompt)
        
            response = await agent.ainvoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": message,
                        }
                    ]
                }
            )

            return self._extract_response_text(response)

        except AgentServiceError:
            raise

        except Exception as error:
            raise AgentServiceError(f"Erreur lors de l'appel de l'agent : "f"{type(error).__name__}: {error}") from error