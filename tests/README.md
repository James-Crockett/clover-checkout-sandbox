# Tests

## `test_clover_service.py`

Tests Clover service behavior without making real network requests.

The current test simulates Clover rejecting a payment and verifies that
`pay_order()` raises an HTTP error instead of treating the payment as successful.

## `test_request_timeouts.py`

Verifies that Clover requests apply a timeout without contacting the real API.

The current tests cover `create_order()`, `add_line_item()`, `pay_order()`,
`create_card_token()`, and the OAuth token exchange.

## `test_oauth_storage.py`

Verifies that the OAuth callback stores the access token, refresh token, and
merchant ID locally with owner-only file permissions.
