# checkout-app-clover

A local checkout page that creates and pays Clover sandbox orders

## Setup

- Install Python 3.12
- Install `uv`
- Go to https://sandbox.dev.clover.com/ (setup acc if you dont have one)
- Create a test merchant (or use the existing one), you should see the merchant id.
- Clover sandbox app (you will have APP ID and APP SECRET)
  - Select app type to as 'web'
  - Edit permissions - Merchant - read, for order and payments choose both read and write, also enable online payments
  - In REST Configuration - give site url as 'http://localhost:8000/oauth/callback', alternative - '/', CORS domain - 'http://localhost:8000', Default OAuth - Code.
- For ECOMM private and public token, settings - view all settings - Ecommerce - Ecom API tokens
- For URL refer clover docs.

```bash
uv sync
cp .env.example .env
```

Fill `.env` with Clover sandbox URLs, app credentials, redirect URI, and Ecommerce tokens

| Variable | Purpose |
| --- | --- |
| `CLOVER_BASE_URL` | Clover merchant REST API |
| `CLOVER_APP_ID` / `CLOVER_APP_SECRET` | OAuth app credentials |
| `CLOVER_REDIRECT_URI` | OAuth callback URL |
| `CLOVER_TOKEN_BASE_URL` | Ecommerce card-token API |
| `CLOVER_ECOMM_PUBLIC_TOKEN` | Creates sandbox card tokens |
| `CLOVER_ECOMM_PRIVATE_TOKEN` | Pays Ecommerce orders |
| `CLOVER_OAUTH_AUTHORIZE_URL` | Clover authorization page |
| `CLOVER_OAUTH_API_URL` | OAuth token and refresh API |


## Run

```bash
uv run uvicorn app.main:app --reload
python -m http.server 5500 --directory frontend
```

Run each command in a separate terminal and open `http://localhost:5500`

## OAuth

- Open `http://localhost:8000/oauth/start` and authorize the app
- Clover redirects to `/oauth/callback`
- The backend stores the token pair and merchant ID
- Merchant requests use the stored token and refresh it once when expired
- A failed refresh requires authorization through `/oauth/start` again

Tokens are stored in `app/oauth_tokens.json` (git-ignored) with owner-only permissions

## Payment Flow

The frontend sends amount and description to `POST /api/payments`

- Create an order with `POST /v3/merchants/{merchant_id}/orders`
- Add a line item with `POST /orders/{order_id}/line_items`
- Create a sandbox card token with `POST /v1/tokens`
- Pay the order with `POST /v1/orders/{order_id}/pay`

The response displays payment status and appends it to `app/transaction.log`

Successful responses include `"success": true`, payment status, order ID, amount
paid, and charge ID

Failed payments return `502` with Clover's error details, for example:

```json
{
  "detail": {
    "message": "Clover rejected the payment request",
    "clover_error": "{\"error\":{\"code\":\"card_declined\"}}"
  }
}
```

If Clover reports that the sale count per card is greater than the configured
amount, the sandbox test card has reached its transaction limit Use another
official Clover test card or reset the sandbox test data

## Tests

Run `python -m unittest discover -s tests -v` See `tests/README.md` for details
