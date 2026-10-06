# AI Prompt Record

## Problem 2 — Analyze the Databas

**Prompt I typed:**

> Yo look in the database data/campus_customs.db without changing anything, and find every table and its fields, including catalogue, inventory, users, and any others you find. For each field, tell me its name, its data type, and what kind of information it holds. Then create a file called output/harness.md, making the output folder if it doesn't exist, that lists each table and its fields with one short line explaining why each field matters for the shop or the chatbot. Don't include any real passwords or hashes from the users table, just explain what those fields are for. If you need to run Python, use py instead of python, and don't build anything else yet, like the website or the agent.

**What it did:**

The database was inspected without modifying it. The schema was documented in `output/harness.md`, including the catalogue, inventory, users, chat_messages, and SQLite internal sequence table, with field types and shop/chatbot relevance.

**Changes / follow-ups:**

The `output` folder was created because it did not exist. Passwords and password hashes were intentionally excluded, and no website or agent was built.

## Problem 3 — Build the Campus Customs Website

**Prompt I typed:**

> Yo build a website for campus merch shop Campus Customs, so make a new folder called frontend and set up a React, Vite, and TypeScript website in it. I want a menu bar at the top with links to Home, Products, About Us, Log in, and Create account, and each link should open its own page, with simple placeholders for Products, Log in, and Create account for now. For the Home page, use the heading "Campus Customs" with a short tagline about gear for everyone who calls campus home, a button to the Products page, three short highlights (hoodies and jackets, everyday tees, and hats and gifts), and a note that shoppers can use the chat in the bottom right corner to ask about colors, sizes, prices, and stock. For the About Us page, write friendly sections on who we are (a campus merch shop that makes school gear comfortable and easy to find), who we make it for (students, alumni, parents, and fans), what we care about (a clear selection, upfront prices, and honest stock information), and a "Come say hi" section with the shop address, 57 Broadway, New Haven, CT 06511. Don't change anything in my data or output folders, and use npm for the setup. When you're done, tell me how to start the site and see it in my browser.

> Yo make the Products page show every product from the catalogue table in data/campus_customs.db, with its picture, name, price, and short description. When I click a product, it should open its own page with a big picture on one side and the full description, price, and sizes and stock (from the inventory table) on the other. Also add a chat box in the bottom right corner of every page that just shows a pretend reply for now. Please make a small FastAPI app in backend/main.py that only reads the database and sends the products and pictures to the website. python doesn't work on my Windows laptop, use py, install what's needed, save the packages in a requirements.txt in my Homework 4 folder, and tell me the exact commands to start everything, but don't build the real chatbot yet.

**What it did:**

The first prompt created a React, Vite, and TypeScript Campus Customs site with Home, Products, About Us, Log in, and Create account navigation. The second prompt connected the Products page to a read-only FastAPI catalogue API and added product detail views with images, prices, descriptions, sizes, and inventory stock, plus a pretend chat box.

**Changes / follow-ups:**

The Products page was expanded from a placeholder into a database-backed catalogue, and `backend/main.py` plus the root `requirements.txt` were added. The data and output folders were left unchanged; the requested `py` installation could not run because the Windows `py` launcher was unavailable.

## Problem 4 — Create Account and Login

**Prompt I typed:**

> yo create account and login flow to my Campus Customs site, using the Create account and Log in pages that are already in the menu bar? For Create account, ask for first name, last name, email, password, and a confirm password box, and for Log in, just ask for email and password. Save new accounts in the users table in data/campus_customs.db (only add rows to that table, and don't change catalogue or inventory), and dont store plain passwords, so hash them the same way the existing test user's password was hashed and don't print any real hashes. Please make sure the test user (test@campuscustoms.yale.edu, password: password) can still log in and that a brand new account I create works too, and show a simple message if a login or sign-up fails. Add whatever the backend needs to requirements.txt, and use py instead of python since python doesn't work on my laptop. Last, update output/harness.md with a short section on how login works, including what's stored for each user and how passwords are protected, and tell me exactly how to test it.

**What it did:**

The prompt added Create account and Log in forms to the Campus Customs site and connected them to FastAPI authentication endpoints. New users are stored in the `users` table with PBKDF2-SHA256 password hashes, while catalogue and inventory remain unchanged.

**Changes / follow-ups:**

The backend requirements and `output/harness.md` were updated with authentication details and testing steps. The frontend build passed, but live backend testing could not be completed because the Windows `py` launcher was unavailable.

## Problem 5 — Pydantic Agent Backend

**Prompt I typed:**

> yo turn my chat box into a real chatbot using a PydanticAI agent behind my FastAPI backend, with a new chat route in backend/main.py that the chat box uses for replies. Keep the agent in four files in the backend folder: prompts/prompt.md (friendly Campus Customs voice, stay on merch, be honest about price and stock, never share passwords or private info), agent.py, tools.py with one simple read-only product and stock lookup, and models.py for the chat reply and product card types. Send the AI calls through Portkey and read my PORTKEY_API_KEY, model name, and provider name from a .env file in my Homework 4 folder, with no real keys in the code and a .env.example with placeholders only. Make it run from inside the backend folder with "uvicorn main:app --reload --port 8000" so the imports and database path work that way, add what's needed to requirements.txt, and use py instead of python. Add a short note to output/harness.md on how the front end talks to FastAPI and how the agent loads the prompt and model. When you're done, tell me what to put in my .env and how to test it.

**What it did:**

The prompt turned the pretend chat box into a FastAPI-backed PydanticAI chatbot. It added the agent, prompt, read-only product/stock tool, response models, Portkey environment configuration, `/api/chat`, and documentation in `output/harness.md`.

**Changes / follow-ups:**

The follow-up verification corrected the model value in `.env` from `5.6-terra-global` to `gpt-5.6-terra-global` and fixed the agent to load at startup and return `result.output`. The frontend build passed, but live testing was limited because the Windows `py` launcher was unavailable.

## Problem 6 — Tools: Product Info and Stock 

**Prompt I typed:**

> yo expand the tools in backend/tools.py so my chatbot can look up real info from data/campus_customs.db, with tools for a product's description, its price, and how many are in stock for each size, and only read from the database without changing anything? The agent should always use these tools for price and stock questions and never make up prices or quantities, and if a size is out of stock or a product can't be found, it should say so clearly. Update backend/prompts/prompt.md so the agent knows when to call each tool. Add or update the return types in backend/models.py for the lookup results, like product name, description, price, and sizes with their quantities. Add a section to output/harness.md that lists each tool and explains which model fields I chose for the lookup results and why. Use py instead of python since python doesn't work on my laptop, and when you're done, tell me how to test it.

**What it did:**

The prompt expanded the chatbot with read-only tools for product discovery, descriptions, exact prices, and size-level inventory. It also updated the agent instructions, structured lookup models, and `output/harness.md` documentation so the chatbot reports database-backed facts instead of guessing.

**Changes / follow-ups:**

The tools use SQLite read-only mode and include zero-quantity sizes so out-of-stock items can be reported clearly. The frontend build passed, but backend testing remained limited because the Windows `py` launcher was unavailable.

## Problem 7 — Chat Search that Updates the Page

**Prompt I typed:**

> yo make the chatbot's product search update the website, so when a customer asks about a type of item like "what hoodies do you have?", the agent searches the catalogue in data/campus_customs.db and sends back the matching products as structured data (product id, name, price, image, and a short description) along with its chat reply? Then have the front end read that and show the matching items as product cards on the page itself, not just text in the chat box, with the image, name, price, and short info on each card. Make sure each of those cards, and the regular ones on the Products page, still opens the single-item page with the large image and full details when I click it. If nothing matches, the chat should say so and show no cards, and the agent should only use real results from the database. Update backend/prompts/prompt.md so the agent knows when to return product matches, and update output/harness.md with a short note on how search results get from the agent to the page. Use py instead of python since python doesn't work on my laptop, and when you're done, tell me how to test it.

**What it did:**

The prompt connected chatbot product search to the website. Matching catalogue results now return as structured product cards with IDs, names, prices, images, and descriptions, and the frontend displays them on the page with links to the full product detail view.

**Changes / follow-ups:**

The agent prompt and harness documentation were updated to describe structured search results and empty-result behavior. The frontend build passed; backend live testing remained limited because the Windows `py` launcher was unavailable.

## Problem 8 — Sales Dashboard Webpage

**Prompt I typed:**

> yo make my chatbot remember logged-in customers by saving each chat message in the existing chat_messages table in data/campus_customs.db (only adding rows there) and loading their history back into the chat box when they log in again? Guests can still chat, but their messages shouldn't be saved. The agent should know who is chatting (name and email, never the password hash), so pass that in as agent deps or a tool, and have the backend work out the user from my login (adding a simple token or session if needed) instead of trusting the browser. Have the front end also send page context, like which product the shopper is viewing, so if they ask "do you have this in pink?" the agent knows which item they mean and checks it with the tools. Update output/harness.md (how chat history is stored, what customer fields the agent sees, and how page context is passed) and backend/prompts/prompt.md. Use py instead of python, and tell me how to test it when you're done.

**What it did:**

The prompt added server-issued sessions, logged-in chat history persistence, and page context for the PydanticAI agent. Logged-in user and assistant messages are saved to `chat_messages`, history is loaded after login, and guest messages remain unsaved.

**Changes / follow-ups:**

The agent receives only the customer’s name, email, recent history, and page context—never passwords or hashes. The backend identifies users from server-side session tokens, and `output/harness.md` plus `backend/prompts/prompt.md` were updated with the behavior and testing instructions.

## Problem 9 — Usability Improvements

**Prompt I typed:**

> Add a search bar on the Products page so users can quickly find items by name, type, or description instead of scrolling through everything. Also added a status indicator that shows whether the shop assistant is online or offline. On the backend, add a health check so the website can tell if the assistant is running, and improve product searches so the chatbot can understand shortened product names instead of requiring the exact full name, Make sure all improvements actually appear in the running app and clearly explain what files you changed. Also create or update output/usability.md and, for each improvement, write what was added and why it helps Campus Customs shoppers or the business. Keep the changes realistic.

**What it did:**

The prompt added a Products-page search bar, a visible assistant online/offline status indicator, a backend health endpoint, and partial product-name matching for chatbot searches. The changes were documented in `output/usability.md`, including how each improvement helps shoppers or the business.

**Changes / follow-ups:**

The frontend production build passed, confirming the improvements compile and appear in the running app. The database schema and product records were left unchanged.

## Problem 10 — Frontend Visual Redesign

**Prompt I typed:**

> Redesign the Campus Customs website so it looks like a real campus store, with better fonts, colors, layout, product cards, and a nicer chat box.
>
> Add some cool motion too, like hover effects on the product cards, smooth page changes, and a fun home page entrance, and make it creative and original instead of a plain template.
>
> Change how the front end looks, and make sure everything still works, like the menu links, the Products and single-item pages, the chat, login, and create account, and that it looks good on my phone. Don't touch the backend, my data folder, or my .env file. Then make output/design.md, a short file listing what you changed (fonts, colors, layout, motion, cards, chat) and why it should help customers stick around and buy. Tell me how to see it when you're done.

**What it did:**

The prompt redesigned the Campus Customs frontend with a campus-store visual identity, improved typography, colors, layout, responsive behavior, product cards, chat styling, and motion effects. It also created `output/design.md` documenting the design decisions and customer/business benefits.

**Changes / follow-ups:**

The frontend build passed, confirming the existing navigation, product details, chat, login, create account, and mobile layout still compile. The backend, data folder, and `.env` file were left unchanged.

## Problem 11 — Site Testing (App Check)

**Prompt I typed:**

> create output/app_check.html, a simple page I can double-click to open, that documents my testing of the live Campus Customs site? It needs a clear heading for each of three checks: the chatbot telling me the real stock level and price of an item from the database, the product cards that appear on the page after I ask a category question like "what hoodies do you have?", and one usability feature from Problem 9. Under each heading, show the screenshot and add one or two sentences about what it proves. I'll take the screenshots myself, so please make the folder output/app_check_images/ and link the images with relative paths like app_check_images/inventory.png, app_check_images/search_cards.png, and app_check_images/usability.png, with simple placeholder text where an image is missing instead of fake ones. don't change anything outside the output folder

**What it did:**

The prompt created `output/app_check.html` and the `output/app_check_images/` folder. The page documents the three live-app checks, uses relative screenshot links, and shows placeholder text when screenshots are missing.

**Changes / follow-ups:**

The usability check was labeled as the Problem 9 product search/filter feature. The three original screenshots were later saved with the exact requested filenames, and no files outside `output` were changed for this task.

## Problem 12 — Audit Trail, Safety, Finish Harnesses

**Prompt I typed:**

> Yo create an audit trail that saves each agent step (time, tool name, short inputs and result, and why it stopped) in output/audit_trail.json, only adding new entries and never wiping old ones, even after I restart the backend. Keep passwords, hashes, API keys, and emails out of it, and add simple safety rules to backend/prompts/prompt.md, like never sharing private info, never making up prices or stock, staying on Campus Customs merch. Then finish output/harness.md with the models.py fields and why, the tools, the safety rules, and the specs

**What it did:**

The prompt added a persistent audit trail in `output/audit_trail.json` that records agent steps, tool names, redacted inputs/results, timestamps, and stop reasons without exposing sensitive values. It also added safety rules to the agent prompt and completed `output/harness.md` with model fields, tools, safety rules, and operating specifications.

**Changes / follow-ups:**

The audit trail preserves older entries across backend restarts and redacts passwords, hashes, API keys, and emails. The data folder and `.env` file were left unchanged.
