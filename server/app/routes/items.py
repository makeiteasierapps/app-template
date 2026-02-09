"""
Sample CRUD routes using MongoDB.

This module is opt-in. To enable:
1. Uncomment `motor>=3.3.0` in server/requirements.txt
2. Import this router in server/app/main.py:

    from app.routes.items import router as items_router
    app.include_router(items_router, prefix="/api")
"""

from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId

from ..db import get_db

router = APIRouter(tags=["items"])


def serialize_doc(doc: dict) -> dict:
    """Convert MongoDB document to JSON-serializable dict."""
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc


@router.get("/items")
async def list_items(skip: int = 0, limit: int = 20, db=Depends(get_db)):
    """List items with pagination."""
    items = []
    cursor = db.items.find().skip(skip).limit(limit)
    async for doc in cursor:
        items.append(serialize_doc(doc))
    return {"items": items, "skip": skip, "limit": limit}


@router.get("/items/{item_id}")
async def get_item(item_id: str, db=Depends(get_db)):
    """Get a single item by ID."""
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid item ID")

    doc = await db.items.find_one({"_id": ObjectId(item_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Item not found")
    return serialize_doc(doc)


@router.post("/items", status_code=201)
async def create_item(item: dict, db=Depends(get_db)):
    """Create a new item."""
    result = await db.items.insert_one(item)
    return {"id": str(result.inserted_id)}


@router.put("/items/{item_id}")
async def update_item(item_id: str, item: dict, db=Depends(get_db)):
    """Update an existing item."""
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid item ID")

    result = await db.items.update_one(
        {"_id": ObjectId(item_id)}, {"$set": item}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"modified": result.modified_count}


@router.delete("/items/{item_id}")
async def delete_item(item_id: str, db=Depends(get_db)):
    """Delete an item."""
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid item ID")

    result = await db.items.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"deleted": True}
