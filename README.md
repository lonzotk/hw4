# Campus Customs

Campus Customs is a campus merchandise storefront with a React/Vite/TypeScript frontend and a FastAPI/PydanticAI backend. The site supports catalogue browsing, product detail pages, account login/signup, database-backed product and stock lookups, structured chatbot product cards, chat history for logged-in users, and a Portkey-routed assistant.

## Local setup

### 1. Add the data pack

The data pack is intentionally excluded from Git. Place these local files in the project root:

```text
data/campus_customs.db
data/products/
```

`products/` should contain the product images referenced by the database.

### 2. Configure the backend

Copy `.env.example` to `.env` and replace the placeholders with your local Portkey configuration. The backend reads:

```env
PORTKEY_API_KEY=your-real-portkey-key
PORTKEY_MODEL=your-model-id
PORTKEY_PROVIDER=your-provider-name
```

Keep `.env` private. Never commit it or paste the key into source files.

Install the backend packages from the project root:

```powershell
py -m pip install -r requirements.txt
```

Start the backend from inside the `backend` folder as requested:

```powershell
cd backend
py -m uvicorn main:app --reload --port 8000
```

### 3. Start the frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL, normally `http://localhost:5173/`.

## Important local files

- `backend/main.py` — FastAPI routes, authentication, catalogue APIs, chat, sessions, and audit integration.
- `backend/agent.py` — PydanticAI agent and Portkey model setup.
- `backend/tools.py` — read-only product, description, price, and inventory tools.
- `backend/prompts/prompt.md` — assistant behavior and safety rules.
- `output/harness.md` — database, tool, safety, and operating documentation.
- `output/audit_trail.json` — generated after agent runs; it is intentionally kept trackable and redacted by the application.

## Before publishing

Confirm that `.env` and `data/` are ignored, `.env.example` contains placeholders only, and no real credentials or private customer data have been added to output files. The screenshots in `output/app_check_images/` and documentation in `output/` are intended to remain included.
