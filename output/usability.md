# Campus Customs usability improvements

## Frontend improvements

1. **Product search/filter** — `frontend/src/App.tsx` and `frontend/src/App.css` now include a search box on the Products page. It filters by product name, garment type, and description and gives a clear no-match message. This helps shoppers quickly narrow a large catalogue without scrolling through every item.

2. **Visible assistant status** — `frontend/src/App.tsx` calls the new `/api/health` endpoint and shows “Shop assistant online” or “Assistant offline” in the footer. This helps shoppers understand whether chat and live catalogue features are available, and helps the business spot a stopped backend quickly.

## Agent/backend improvements

3. **Health endpoint** — `backend/main.py` adds `GET /api/health`, a small non-sensitive status check used by the site. It gives the frontend and an operator a fast way to distinguish an unavailable backend from a product-search problem.

4. **Forgiving product lookup** — `backend/tools.py` now tries exact product ID/name matching first, then safe partial matching. A shopper can ask about a shortened product name instead of reproducing the catalogue title exactly, while the agent still receives only real database results.

These changes do not alter the database schema or product records.
