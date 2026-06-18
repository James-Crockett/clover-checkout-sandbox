import unittest
from unittest.mock import Mock, patch

import requests

from app.clover_service import pay_order


class PayOrderTests(unittest.TestCase):
    def test_rejected_payment_raises_http_error(self):
        # Create a fake Clover response that fails when pay_order checks
        # whether the HTTP request was successful.
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError()

        # Replace the real network request so this test never contacts Clover.
        with patch("app.clover_service.requests.post", return_value=response):
            # Confirm that pay_order reports Clover's rejected response instead
            # of continuing as if the payment succeeded.
            with self.assertRaises(requests.HTTPError):
                pay_order("order_id", "source_token")


if __name__ == "__main__":
    unittest.main()
