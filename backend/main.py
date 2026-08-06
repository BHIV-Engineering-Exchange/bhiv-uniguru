from __future__ import annotations

import os
from pathlib import Path

import uvicorn
from dotenv import load_dotenv


def main() -> None:
    # Load .env file from backend directory
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded environment from: {env_path}")

    # Mount the ecosystem/sanskrit runtime API under /v2
    from service.api import app
    from service.uniguru_runtime_api import app as runtime_app
    app.mount("/v2", runtime_app)

    host = os.getenv("UNIGURU_HOST", "0.0.0.0")
    port = int(os.getenv("UNIGURU_PORT", "8000"))
    uvicorn.run(app, host=host, port=port, workers=1)


if __name__ == "__main__":
    main()
