import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tbyn_bot.config import load_config, load_dotenv


class DotenvTest(unittest.TestCase):
    def setUp(self):
        self.original_env = os.environ.copy()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_loads_env_file_values(self):
        with TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            env_file.write_text(
                "\n".join(
                    [
                        "# local config",
                        "TELEGRAM_BOT_TOKEN=abc123",
                        "VALIDATION_DELETE_AFTER_SECONDS=20",
                        'POLLING_TIMEOUT_SECONDS="30"',
                    ]
                ),
                encoding="utf-8",
            )

            os.environ.pop("TELEGRAM_BOT_TOKEN", None)
            os.environ.pop("VALIDATION_DELETE_AFTER_SECONDS", None)
            os.environ.pop("POLLING_TIMEOUT_SECONDS", None)

            load_dotenv(env_file)

            self.assertEqual(os.environ["TELEGRAM_BOT_TOKEN"], "abc123")
            self.assertEqual(os.environ["VALIDATION_DELETE_AFTER_SECONDS"], "20")
            self.assertEqual(os.environ["POLLING_TIMEOUT_SECONDS"], "30")

    def test_does_not_override_existing_environment_values(self):
        with TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            env_file.write_text("TELEGRAM_BOT_TOKEN=file-token", encoding="utf-8")
            os.environ["TELEGRAM_BOT_TOKEN"] = "shell-token"

            load_dotenv(env_file)

            self.assertEqual(os.environ["TELEGRAM_BOT_TOKEN"], "shell-token")

    def test_load_config_reads_default_dotenv_file(self):
        with TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            env_file.write_text(
                "\n".join(
                    [
                        "TELEGRAM_BOT_TOKEN=abc123",
                        "VALIDATION_DELETE_AFTER_SECONDS=25",
                        "POLLING_TIMEOUT_SECONDS=10",
                    ]
                ),
                encoding="utf-8",
            )

            old_cwd = Path.cwd()
            os.chdir(temp_dir)
            try:
                os.environ.pop("TELEGRAM_BOT_TOKEN", None)
                os.environ.pop("VALIDATION_DELETE_AFTER_SECONDS", None)
                os.environ.pop("POLLING_TIMEOUT_SECONDS", None)

                config = load_config()
            finally:
                os.chdir(old_cwd)

            self.assertEqual(config.telegram_bot_token, "abc123")
            self.assertEqual(config.validation_delete_after_seconds, 25)
            self.assertEqual(config.polling_timeout_seconds, 10)

    def test_load_config_reads_meeting_slides_settings(self):
        os.environ["TELEGRAM_BOT_TOKEN"] = "abc123"
        os.environ["GOOGLE_MEETING_SLIDES_TEMPLATE_ID"] = "template-id"
        os.environ["GOOGLE_MEETING_SLIDES_FOLDER_ID"] = "folder-id"

        config = load_config()

        self.assertEqual(config.google_meeting_slides_template_id, "template-id")
        self.assertEqual(config.google_meeting_slides_folder_id, "folder-id")

    def test_load_config_defaults_google_auth_mode_to_oauth_and_oauth_files(self):
        with TemporaryDirectory() as temp_dir:
            old_cwd = Path.cwd()
            os.chdir(temp_dir)
            try:
                os.environ["TELEGRAM_BOT_TOKEN"] = "abc123"

                config = load_config()
            finally:
                os.chdir(old_cwd)

        self.assertEqual(config.google_auth_mode, "oauth")
        self.assertEqual(config.google_oauth_client_secrets_file, "google-oauth-client.json")
        self.assertEqual(config.google_oauth_token_file, "google-oauth-token.json")

    def test_load_config_reads_google_oauth_settings(self):
        os.environ["TELEGRAM_BOT_TOKEN"] = "abc123"
        os.environ["GOOGLE_AUTH_MODE"] = " OAuth "
        os.environ["GOOGLE_OAUTH_CLIENT_SECRETS_FILE"] = "client.json"
        os.environ["GOOGLE_OAUTH_TOKEN_FILE"] = "token.json"

        config = load_config()

        self.assertEqual(config.google_auth_mode, "oauth")
        self.assertEqual(config.google_oauth_client_secrets_file, "client.json")
        self.assertEqual(config.google_oauth_token_file, "token.json")

    def test_load_config_rejects_invalid_google_auth_mode(self):
        os.environ["TELEGRAM_BOT_TOKEN"] = "abc123"
        os.environ["GOOGLE_AUTH_MODE"] = "api_key"

        with self.assertRaisesRegex(RuntimeError, "GOOGLE_AUTH_MODE"):
            load_config()


if __name__ == "__main__":
    unittest.main()
