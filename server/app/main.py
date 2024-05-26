"""Recipes API — FastAPI + MongoDB.

Store recipes with ingredients, steps, cook time and a rating; search by
ingredient and filter by maximum cook time.

Endpoints:
    GET    /api/health
    GET    /api/recipes?q=&ingredient=&max_minutes=
    POST   /api/recipes
    GET    /api/recipes/{id}
    PUT    /api/recipes/{id}
    POST   /api/recipes/{id}/rate          {rating: 1..5}
    DELETE /api/recipes/{id}
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .db import get_db

app = FastAPI(title="Recipes API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class RecipeIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    ingredients: List[str] = Field(default_factory=list)
    steps: List[str] = Field(default_factory=list)
    minutes: int = Field(ge=0, le=100000)
    tags: List[str] = Field(default_factory=list)


class Rating(BaseModel):
    rating: int = Field(ge=1, le=5)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ser(doc: dict) -> dict:
    doc = dict(doc)
    doc["id"] = str(doc.pop("_id"))
    n = doc.get("rating_count", 0)
    doc["avg_rating"] = round(doc.get("rating_sum", 0) / n, 2) if n else None
    return doc


def _oid(rid: str) -> ObjectId:
    try:
        return ObjectId(rid)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="recipe not found")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/recipes")
def list_recipes(q: Optional[str] = None, ingredient: Optional[str] = None,
                 max_minutes: Optional[int] = None, db=Depends(get_db)):
    query: dict = {}
    if q:
        query["title"] = {"$regex": re.escape(q), "$options": "i"}
    if ingredient:
        query["ingredients"] = {"$regex": re.escape(ingredient), "$options": "i"}
    if max_minutes is not None:
        query["minutes"] = {"$lte": max_minutes}
    return [_ser(d) for d in db.recipes.find(query).sort("created_at", -1)]


@app.post("/api/recipes", status_code=201)
def create_recipe(r: RecipeIn, db=Depends(get_db)):
    doc = r.model_dump()
    doc.update(rating_sum=0, rating_count=0, created_at=_now())
    doc["_id"] = db.recipes.insert_one(doc).inserted_id
    return _ser(doc)


@app.get("/api/recipes/{rid}")
def get_recipe(rid: str, db=Depends(get_db)):
    doc = db.recipes.find_one({"_id": _oid(rid)})
    if not doc:
        raise HTTPException(status_code=404, detail="recipe not found")
    return _ser(doc)


@app.put("/api/recipes/{rid}")
def update_recipe(rid: str, r: RecipeIn, db=Depends(get_db)):
    doc = db.recipes.find_one_and_update(
        {"_id": _oid(rid)}, {"$set": r.model_dump()}, return_document=True)
    if not doc:
        raise HTTPException(status_code=404, detail="recipe not found")
    return _ser(doc)


@app.post("/api/recipes/{rid}/rate")
def rate_recipe(rid: str, rating: Rating, db=Depends(get_db)):
    doc = db.recipes.find_one_and_update(
        {"_id": _oid(rid)},
        {"$inc": {"rating_sum": rating.rating, "rating_count": 1}},
        return_document=True,
    )
    if not doc:
        raise HTTPException(status_code=404, detail="recipe not found")
    return _ser(doc)


@app.delete("/api/recipes/{rid}", status_code=204)
def delete_recipe(rid: str, db=Depends(get_db)):
    if db.recipes.delete_one({"_id": _oid(rid)}).deleted_count == 0:
        raise HTTPException(status_code=404, detail="recipe not found")
    return None
