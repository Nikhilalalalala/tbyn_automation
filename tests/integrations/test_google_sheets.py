import unittest

from tbyn_bot.integrations.google_sheets import read_sheet_values


class GoogleSheetsTest(unittest.TestCase):
    def test_reads_sheet_values_with_oauth_token_credentials(self):
        fake_google = FakeGoogleSheetsServices()

        rows = read_sheet_values(
            spreadsheet_id="sheet-id",
            cell_range="Events!A:D",
            oauth_token_file="google-oauth-token.json",
            credentials_factory=fake_google.credentials_factory,
            service_builder=fake_google.service_builder,
        )

        self.assertEqual(fake_google.oauth_token_file, "google-oauth-token.json")
        self.assertEqual(
            fake_google.scopes,
            ["https://www.googleapis.com/auth/spreadsheets.readonly"],
        )
        self.assertEqual(fake_google.service.credentials, "oauth-credentials")
        self.assertEqual(fake_google.service.get_call, {"spreadsheetId": "sheet-id", "range": "Events!A:D"})
        self.assertEqual(rows, [["S/N", "Event Title"], ["1", "Opening"]])


class FakeGoogleSheetsServices:
    def __init__(self):
        self.oauth_token_file = None
        self.scopes = None
        self.service = FakeSheetsService()

    def credentials_factory(self, oauth_token_file, scopes):
        self.oauth_token_file = oauth_token_file
        self.scopes = scopes
        return "oauth-credentials"

    def service_builder(self, service_name, version, credentials):
        self.service.credentials = credentials
        if (service_name, version) != ("sheets", "v4"):
            raise AssertionError(f"Unexpected service: {service_name} {version}")
        return self.service


class FakeSheetsService:
    def __init__(self):
        self.credentials = None
        self.get_call = None

    def spreadsheets(self):
        return self

    def values(self):
        return self

    def get(self, **kwargs):
        self.get_call = kwargs
        return FakeExecute({"values": [["S/N", "Event Title"], ["1", "Opening"]]})


class FakeExecute:
    def __init__(self, result):
        self.result = result

    def execute(self):
        return self.result


if __name__ == "__main__":
    unittest.main()
