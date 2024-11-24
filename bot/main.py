from asyncio import run
from pathlib import Path
from sys import path


BASE_DIR = Path(__file__).resolve().parents[1]
path.append(str(BASE_DIR))

from bot.presentation.app.run import main  # noqa: E402


if __name__ == "__main__":
    print("Bot started")
    run(main())
