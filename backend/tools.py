from pathlib import Path
import sqlite3

from models import ProductCard, ProductLookup, SizeStock
from audit import record_step

ROOT = Path(__file__).resolve().parent.parent
DATABASE = ROOT / "data" / "campus_customs.db"


def _find_product(db: sqlite3.Connection, product: str) -> sqlite3.Row | None:
    db.row_factory = sqlite3.Row
    row = db.execute(
        "SELECT product_id, name, description, price FROM catalogue WHERE lower(product_id) = lower(?) OR lower(name) = lower(?) LIMIT 1",
        (product.strip(), product.strip()),
    ).fetchone()
    if row is not None:
        return row
    return db.execute(
        "SELECT product_id, name, description, price FROM catalogue WHERE lower(name) LIKE lower(?) OR lower(product_id) LIKE lower(?) ORDER BY name LIMIT 1",
        (f"%{product.strip()}%", f"%{product.strip()}%"),
    ).fetchone()


def lookup_product_description(product: str) -> ProductLookup | None:
    """Read the catalogue description for one product. Never writes to the database."""
    with sqlite3.connect(f"file:{DATABASE}?mode=ro", uri=True) as db:
        row = _find_product(db, product)
        result = None if row is None else ProductLookup(product_id=row["product_id"], product_name=row["name"], description=row["description"])
        record_step("lookup_product_description", {"product": product}, "match found" if result else "product not found")
        return result


def lookup_product_price(product: str) -> ProductLookup | None:
    """Read the exact catalogue price for one product. Never guesses or writes."""
    with sqlite3.connect(f"file:{DATABASE}?mode=ro", uri=True) as db:
        row = _find_product(db, product)
        result = None if row is None else ProductLookup(product_id=row["product_id"], product_name=row["name"], price=row["price"])
        record_step("lookup_product_price", {"product": product}, "match found" if result else "product not found")
        return result


def lookup_product_stock(product: str) -> ProductLookup | None:
    """Read every size quantity for one product, including zero-stock sizes."""
    with sqlite3.connect(f"file:{DATABASE}?mode=ro", uri=True) as db:
        row = _find_product(db, product)
        if row is None:
            record_step("lookup_product_stock", {"product": product}, "product not found")
            return None
        stock = db.execute("SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY id", (row["product_id"],)).fetchall()
        result = ProductLookup(product_id=row["product_id"], product_name=row["name"], sizes=[SizeStock(size=item[0], quantity=item[1]) for item in stock])
        record_step("lookup_product_stock", {"product": product}, f"returned {len(stock)} size rows")
        return result


def lookup_products(query: str) -> list[ProductCard]:
    """Read-only product discovery for recommendations; use the specific tools for price or stock facts."""
    def search_forms(term: str) -> set[str]:
        term = term.lower().strip(".,?!")
        forms = {term}
        if term.endswith("ies") and len(term) > 4:
            forms.add(term[:-3] + "y")
        if term.endswith("s") and len(term) > 3:
            forms.add(term[:-1])
        return forms

    terms = [search_forms(term) for term in query.split() if len(term.strip(".,?!")) > 2]
    with sqlite3.connect(f"file:{DATABASE}?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute("SELECT product_id, name, price, description, garment_type, colors, search_tags FROM catalogue ORDER BY name").fetchall()
        matches = []
        for row in rows:
            searchable = " ".join(str(row[key] or "") for key in ("name", "description", "garment_type", "colors", "search_tags")).lower()
            if terms and not any(any(form in searchable for form in term_forms) for term_forms in terms):
                continue
            stock = db.execute("SELECT size FROM inventory WHERE product_id = ? AND quantity > 0 ORDER BY id", (row["product_id"],)).fetchall()
            matches.append(ProductCard(product_id=row["product_id"], name=row["name"], price=row["price"], image_url=f"/media/products/{Path(row['product_id'] + '.jpg').name}", description=row["description"], sizes_in_stock=[item["size"] for item in stock]))
            if len(matches) >= 8:
                break
        record_step("lookup_products", {"query": query}, f"returned {len(matches)} product cards")
        return matches
