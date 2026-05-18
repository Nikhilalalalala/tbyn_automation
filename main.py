"""Entry point for the TBYN Telegram poll bot."""

from tbyn_bot.app import run
from tbyn_bot.config import load_config


if __name__ == "__main__":
    run(load_config())
