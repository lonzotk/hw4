from pathlib import Path
import sqlite3
import asyncio
import hashlib
import hmac
import secrets
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from agent import answer
from models import ChatDeps, ChatHistoryItem, ChatRequest, ChatReply
from audit import begin_audit, finish_audit, record_step

ROOT = Path(__file__).resolve().parent.parent
DATABASE = ROOT / "data" / "campus_customs.db"
PRODUCTS = ROOT / "data" / "products"
SESSIONS: dict[str, int] = {}

app = FastAPI(title="Campus Customs Catalogue API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.mount("/media/products", StaticFiles(directory=PRODUCTS), name="product-images")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": "Campus Customs API"}


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DATABASE)


class SignUpRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    confirm_password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    SESSIONS[token] = user_id
    return token


def session_user(token: str | None) -> sqlite3.Row | None:
    if not token or token not in SESSIONS:
        return None
    with get_connection() as db:
        db.row_factory = sqlite3.Row
        return db.execute("SELECT id, first_name, last_name, name, email FROM users WHERE id = ?", (SESSIONS[token],)).fetchone()


def make_password_hash(password: str) -> str:
    iterations = 600000
    salt = secrets.token_hex(8)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations).hex()
    return f"pbkdf2_sha256${iterations}${salt}${digest}"


def password_matches(password: str, stored: str) -> bool:
    try:
        parts = stored.split("$")
        print(f"[AUTH DEBUG] hash segments: {len(parts)}")
        if len(parts) == 3:
            # Legacy records omit the work factor and use the assignment's
            # fixed PBKDF2-SHA256 settings.
            algorithm, salt, expected = parts
            counts = [120000]
        else:
            algorithm, count, salt, expected = parts
            counts = [int(count)]
        print(f"[AUTH DEBUG] algorithm: {algorithm}")
        if algorithm != "pbkdf2_sha256":
            print("[AUTH DEBUG] password_matches: false")
            return False
        for count in counts:
            digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), count).hex()
            if hmac.compare_digest(digest, expected):
                print("[AUTH DEBUG] password_matches: true")
                return True
        print("[AUTH DEBUG] password_matches: false")
        return False
    except (ValueError, TypeError):
        print("[AUTH DEBUG] password_matches: false")
        return False


def product_from_row(row: sqlite3.Row, inventory: list[dict]) -> dict:
    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "garment_type": row["garment_type"],
        "description": row["description"],
        "colors": row["colors"],
        "search_tags": row["search_tags"],
        "image_file_path": row["image_file_path"],
        "image_url": f"/media/products/{Path(row['image_file_path']).name}",
        "price": row["price"],
        "inventory": inventory,
    }


@app.get("/api/products")
def list_products() -> list[dict]:
    with get_connection() as db:
        db.row_factory = sqlite3.Row
        rows = db.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
        return [product_from_row(row, []) for row in rows]


@app.get("/api/products/{product_id}")
def get_product(product_id: str) -> dict:
    with get_connection() as db:
        db.row_factory = sqlite3.Row
        row = db.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Product not found")
        stock = db.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY id",
            (product_id,),
        ).fetchall()
        return product_from_row(row, [{"size": item["size"], "quantity": item["quantity"]} for item in stock])


@app.post("/api/auth/signup")
def signup(request: SignUpRequest) -> dict:
    if not request.first_name.strip() or not request.last_name.strip():
        raise HTTPException(status_code=400, detail="First and last name are required.")
    if len(request.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")
    if request.password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")
    email = str(request.email).lower()
    try:
        with get_connection() as db:
            db.execute(
                "INSERT INTO users (name, email, password_hash, created_at, first_name, last_name) VALUES (?, ?, ?, ?, ?, ?)",
                (f"{request.first_name.strip()} {request.last_name.strip()}", email, make_password_hash(request.password), datetime.now(timezone.utc).isoformat(), request.first_name.strip(), request.last_name.strip()),
            )
            user_id = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()[0]
            db.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="An account with that email already exists.")
    return {"message": "Account created successfully.", "first_name": request.first_name.strip(), "session_token": create_session(user_id)}


@app.post("/api/auth/login")
def login(request: LoginRequest) -> dict:
    with get_connection() as db:
        row = db.execute("SELECT id, first_name, email, password_hash FROM users WHERE lower(email) = ?", (str(request.email).lower(),)).fetchone()
    email = str(request.email).lower()
    print(f"[AUTH DEBUG] email lookup: {email}")
    print(f"[AUTH DEBUG] user record found: {row is not None}")
    password_valid = row is not None and password_matches(request.password, row[3])
    print(f"[AUTH DEBUG] login password result: {password_valid}")
    if not password_valid:
        raise HTTPException(status_code=401, detail="Email or password is incorrect.")
    return {"message": "Logged in successfully.", "first_name": row[1] or row[2].split("@")[0], "session_token": create_session(row[0])}


@app.get("/api/chat/history", response_model=list[ChatHistoryItem])
def chat_history(session_token: str) -> list[ChatHistoryItem]:
    user = session_user(session_token)
    if user is None:
        raise HTTPException(status_code=401, detail="Please log in to load chat history.")
    with get_connection() as db:
        rows = db.execute("SELECT role, content, created_at FROM chat_messages WHERE user_id = ? ORDER BY id DESC LIMIT 30", (user["id"],)).fetchall()
    return [ChatHistoryItem(role=row[0], content=row[1], created_at=row[2]) for row in reversed(rows)]


@app.post("/api/chat", response_model=ChatReply)
async def chat(request: ChatRequest) -> ChatReply:
    audit_record = begin_audit(request.message)
    try:
        user = session_user(request.session_token)
        history = chat_history(request.session_token) if user else []
        deps = ChatDeps(customer_name=user["name"] if user else None, customer_email=user["email"] if user else None, page_context=request.page_context, history=history)
        result = await asyncio.wait_for(answer(request.message, deps), timeout=30)
        if user:
            with get_connection() as db:
                db.execute("INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, ?, ?, ?)", (user["id"], "user", request.message, None))
                db.execute("INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, ?, ?, ?)", (user["id"], "assistant", result.reply, result.model_dump_json(include={"products"})))
                db.commit()
        record_step("agent", {"action": "complete"}, "structured chat reply returned")
        finish_audit(audit_record, "completed successfully")
        return result
    except asyncio.TimeoutError:
        finish_audit(audit_record, "agent timeout after 30 seconds")
        raise HTTPException(status_code=504, detail="The shop assistant took too long to respond. Please try again.")
    except RuntimeError as exc:
        finish_audit(audit_record, "configuration error")
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception:
        finish_audit(audit_record, "unexpected agent or database error")
        raise HTTPException(status_code=502, detail="The Campus Customs assistant is temporarily unavailable.")
