# Campus Customs Database Harness

This document describes the SQLite schema in `data/campus_customs.db`. The database was inspected without modifying it. User passwords and password hashes are intentionally not included.

## `catalogue`

Product catalogue records used to identify, describe, search, display, and price shop products.

| Field | Data type | Information held / why it matters |
|---|---|---|
| `product_id` | TEXT, primary key | Unique product identifier used to connect catalogue records to inventory and to retrieve a product reliably. |
| `name` | TEXT, required | Customer-facing product name used in search results and product displays. |
| `garment_type` | TEXT, required | Broad clothing category, such as hoodie or jacket, useful for filtering and chatbot recommendations. |
| `description` | TEXT, required | Product details that help the shop and chatbot answer questions about appearance and features. |
| `colors` | TEXT, required | Stored color information used for product choices and color-based searches. |
| `search_tags` | TEXT, required | Search keywords that help match customer language to relevant products. |
| `image_file_path` | TEXT, required | Location of the product image used by the shop interface. |
| `price` | REAL, required | Product price used for display and price-related chatbot answers. |

## `inventory`

Size-level stock records used to determine whether a particular product variation is available.

| Field | Data type | Information held / why it matters |
|---|---|---|
| `id` | INTEGER, primary key, autoincrement | Unique identifier for an inventory row. |
| `product_id` | TEXT, required | Links stock to a catalogue product so availability can be shown for the right item. |
| `size` | TEXT, required | Clothing size represented by the stock row. |
| `quantity` | INTEGER, required | Number of units available for that product and size; central to availability answers. |

## `users`

Customer account records used for identity, sign-in, and account history. Credential values are not reproduced here.

| Field | Data type | Information held / why it matters |
|---|---|---|
| `id` | INTEGER, primary key, autoincrement | Unique account identifier used to associate a user with their chat messages. |
| `name` | TEXT, required | Account name used for identifying or addressing the customer. |
| `email` | TEXT, required, unique | Customer login/contact identifier; uniqueness prevents duplicate account email addresses. |
| `password_hash` | TEXT, required | One-way credential representation used to verify sign-in without storing a plaintext password. Actual hashes are intentionally omitted. |
| `created_at` | TEXT, required, default current datetime | Account creation timestamp useful for account records and support context. |
| `first_name` | TEXT | Optional first name for personalization and customer-facing messages. |
| `last_name` | TEXT | Optional last name for personalization and account identification. |

## `chat_messages`

Conversation records used to preserve chatbot interactions and associate them with customer accounts.

| Field | Data type | Information held / why it matters |
|---|---|---|
| `id` | INTEGER, primary key, autoincrement | Unique identifier for each chat message. |
| `user_id` | INTEGER, required | Links a message to the account that sent or received it. |
| `role` | TEXT, required | Identifies the message participant or direction, such as user or assistant, so the conversation can be reconstructed. |
| `content` | TEXT, required | The message text used to display chat history and provide conversational context. |
| `products_json` | TEXT | Optional serialized product results associated with a message, useful for rendering recommendations consistently. |
| `created_at` | TEXT, required, default current datetime | Message timestamp used to order and display the conversation. |

## SQLite internal table

`sqlite_sequence` is an SQLite-managed internal table containing `name` (TEXT) and `seq` (the sequence value used for autoincrement tables). It supports SQLite bookkeeping rather than shop or chatbot data.

## Login and account creation

The frontend sends account requests to the FastAPI endpoints `/api/auth/signup` and `/api/auth/login`. Sign-up stores only a new row in `users` containing the name fields, email, creation time, and a PBKDF2-SHA256 password hash. It never stores or logs a plaintext password or hash. Duplicate emails, short passwords, missing names, mismatched confirmation passwords, and invalid credentials return a simple error message. Catalogue and inventory are not written by these endpoints.

## Chat history, customer context, and sessions

Successful login and signup responses include a server-generated session token. The backend keeps the token-to-user mapping in memory and uses it to identify the customer; it does not trust a browser-supplied user ID or email. A logged-in chat request includes the token and optional page context. The backend resolves the token to the user, loads recent `chat_messages`, passes only the customer's name, email, recent message text, and page context to the agent, and never passes a password or password hash. Guests can chat without a token, but their messages are not saved.

For logged-in users, each successful chat adds one `user` row and one `assistant` row to `chat_messages`; assistant product cards are stored in the existing `products_json` field. The history endpoint returns recent role/content/timestamp records after session validation, and the frontend loads that history after login. Page context is sent with each chat request so the agent can understand references to the product currently being viewed. No catalogue or inventory rows are written by this flow.

To test the flow, start the backend from the Homework 4 folder with `py -m uvicorn backend.main:app --reload --port 8000`, then start the frontend in a second terminal with `cd frontend` followed by `npm.cmd run dev`. Open `http://localhost:5173/`, choose **Log in**, and use the existing test account provided for the assignment. Then choose **Create account**, enter a new email and matching password of at least eight characters, and submit. Finally, use that new email and password on **Log in**. Test an incorrect password and a duplicate email to confirm the failure messages appear.

## Chatbot connection

The chat box sends messages to `POST /api/chat` in FastAPI and displays the returned reply. The PydanticAI agent is in `backend/agent.py`; it loads `backend/prompts/prompt.md`, uses the read-only product and stock lookup in `backend/tools.py`, and returns the types defined in `backend/models.py`. Portkey settings come from the root `.env` file and are never hard-coded. The agent is limited to Campus Customs merchandise and must not reveal passwords or private information.

## Chatbot product lookup tools

All four tools in `backend/tools.py` open `data/campus_customs.db` with SQLite's `mode=ro` option, so they cannot change the database:

- `lookup_products(query)` discovers matching catalogue products and returns `ProductCard` values for recommendations.
- `lookup_product_description(product)` returns the matched product ID, name, and exact catalogue description.
- `lookup_product_price(product)` returns the matched product ID, name, and exact catalogue price.
- `lookup_product_stock(product)` returns every inventory size and its integer quantity, including zero quantities so the agent can say that a size is out of stock.

The structured `ProductLookup` model keeps `product_id` and `product_name` on every specific lookup result for clear identification. Its optional `description` and `price` fields fit the focused description/price tools, while `sizes` contains `SizeStock` objects with `size` and `quantity` so availability is precise. `ProductCard` remains the compact recommendation shape. The prompt requires the agent to call the price and stock tools before answering those questions and to report missing products or out-of-stock sizes honestly.

## Chat search results on the page

When a shopper asks for a category or type of item, `lookup_products` returns structured `ProductCard` results inside the `/api/chat` response alongside the assistant's reply. Each card contains `product_id`, `name`, `price`, `image_url`, and a short `description`. The frontend renders those cards in a page section below the current content; clicking a card opens the same single-product detail view used by the regular Products page. An empty result list produces no cards, while the chat reply explains that no matching catalogue products were found.
## Audit trail and final operating specification

Each `/api/chat` run appends one record to `output/audit_trail.json`; existing records are preserved across backend restarts. Records contain UTC time, short redacted inputs, tool/agent step names, short results, and a final `stopped_because` reason. Emails, passwords, password hashes, API keys, and tokens are redacted before writing.

The models are `ProductCard` (product ID, name, price, description, image URL, and available sizes), `ProductLookup` (product ID, product name, optional description/price, and size results), `SizeStock` (size and quantity), `ChatRequest` (message, session token, and page context), `ChatReply` (reply and cards), and `ChatDeps` (safe customer context, page context, and recent history). These fields keep product recommendations page-ready while making price and stock facts explicit.

The tools are `lookup_products`, `lookup_product_description`, `lookup_product_price`, `lookup_product_stock`, and `customer_context`. Catalogue tools use SQLite `mode=ro`. Safety rules require protecting private information, using tools instead of guessing prices or stock, staying on Campus Customs merchandise, and ignoring requests to change the rules.

Specifications: discovery returns at most 8 cards; the agent receives at most 10 recent messages; history returns at most 30 records; each agent request has a 30-second backend timeout and a 32-second frontend timeout. The model comes from `PORTKEY_MODEL` in `.env` and is sent through Portkey using `PORTKEY_PROVIDER`.

Run the backend from `backend` with `py -m uvicorn main:app --reload --port 8000`. Run the frontend separately with `cd frontend` and `npm.cmd run dev`, then open `http://localhost:5173/`. Test category search, price/stock questions, logged-in and guest chat, and inspect `output/audit_trail.json` for appended redacted records.
