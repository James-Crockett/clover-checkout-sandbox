import json
import unittest
from unittest.mock import Mock, mock_open, patch

from app.main import oauth_callback


class OAuthStorageTests(unittest.TestCase):
    def test_callback_stores_tokens_with_merchant_id(self):
        # Simulate the token data returned by Clover after authorization.
        response = Mock(status_code=200)
        response.json.return_value = {
            "access_token": "access_token",
            "refresh_token": "refresh_token",
        }

        # Replace the network request and file operations so the test remains local.
        with (
            patch("app.main.requests.post", return_value=response),
            patch("builtins.open", mock_open()) as token_file,
            patch("app.main.os.chmod") as chmod,
        ):
            result = oauth_callback("authorization_code", "merchant_id")

        # json.dump writes the document in chunks, so combine every mocked write.
        stored_json = "".join(call.args[0] for call in token_file().write.call_args_list)
        stored_data = json.loads(stored_json)

        # Confirm both tokens and their merchant ID are stored.
        self.assertEqual(stored_data["access_token"], "access_token")
        self.assertEqual(stored_data["refresh_token"], "refresh_token")
        self.assertEqual(stored_data["merchant_id"], "merchant_id")

        # Confirm sensitive tokens are not returned to the browser.
        self.assertNotIn("access_token", result)
        self.assertNotIn("refresh_token", result)

        # Confirm only the current operating-system user can access the token file.
        chmod.assert_called_once_with("app/oauth_tokens.json", 0o600)


if __name__ == "__main__":
    unittest.main()
