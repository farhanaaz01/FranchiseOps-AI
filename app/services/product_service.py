from sqlalchemy.orm import Session

from app.models import Product
from app.schemas import ProductCreate, ProductResponse


def get_all(db: Session) -> list[Product]:
    return db.query(Product).all()


def get_by_id(db: Session, product_id: int) -> Product:
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise ValueError(f"Product not found with id: {product_id}")
    return product


def create(db: Session, product: ProductCreate) -> Product:
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update(db: Session, product_id: int, product_update: ProductCreate) -> Product:
    product = get_by_id(db, product_id)
    for key, value in product_update.model_dump().items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


def delete(db: Session, product_id: int) -> None:
    product = get_by_id(db, product_id)
    db.delete(product)
    db.commit()
