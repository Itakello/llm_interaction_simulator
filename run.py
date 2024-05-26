from itakello_logging import ItakelloLogging

from app import create_app

app = create_app()

ItakelloLogging(
    debug=False,
    excluded_modules=[
        "docker.utils.config",
        "docker.auth",
        "httpx",
        "httpcore.connection",
        "httpcore.http11",
        "autogen.io.base",
        "asyncio",
        "openai._base_client",  # Remove to see API requests debug logs
    ],
)

if __name__ == "__main__":
    app.run(debug=True)
