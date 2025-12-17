import uvicorn
import os
from fastmcp import FastMCP
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import telebot
from fastmcp.utilities.types import Image

from dotenv import load_dotenv

load_dotenv()

config = {
    "mcpServers": {
        "sqlite_server": {
            "command": "uvx",
            "args": [
              "mcp-server-sqlite",
              "--db-path",
              "superheroes.db"
            ]
        }
    }
}

composite_proxy = FastMCP.as_proxy(config, name="Composite Proxy")


@composite_proxy.tool
def get_image():
    """Get my last photo"""
    return Image(path='cat.png')


@composite_proxy.tool
def send_telegram_message(message: str):
    """Отправляет мне телеграм сообщение"""
    telegram_token = os.environ.get('TELEGRAM_TOKEN')
    telegram_user_id = os.environ.get('TELEGRAM_USER_ID')
    if not telegram_user_id or not telegram_token:
        raise Exception("Заполните ENV переменные для работы телеграм тула")
    bot = telebot.TeleBot(telegram_token)

    bot.send_message(telegram_user_id, message)


# Configure CORS for browser-based clients
middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins; use specific origins for security
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=[
            "mcp-protocol-version",
            "mcp-session-id",
            "Authorization",
            "Content-Type",
        ],
        expose_headers=["mcp-session-id"],
    )
]

app = composite_proxy.http_app(middleware=middleware)
uvicorn.run(app, port=6661)
