from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.app.models.database import get_db
from backend.app.models.models import Restaurant, MenuItem

router = APIRouter(prefix="/api", tags=["Restaurants"])

@router.get("/restaurants")
def get_restaurants(db: Session = Depends(get_db)):
    restaurants = db.query(Restaurant).all()
    result = []
    for r in restaurants:
        item_count = db.query(MenuItem).filter(MenuItem.restaurant_id == r.id).count()
        result.append({
            "id": r.id,
            "name": r.name,
            "location": r.location,
            "address": r.address,
            "cuisine": r.cuisine,
            "rating": r.rating,
            "phone": r.phone,
            "opening_hours": r.opening_hours,
            "menu_item_count": item_count
        })
    return result

@router.get("/restaurants/{restaurant_id}")
def get_restaurant_by_id(restaurant_id: str, db: Session = Depends(get_db)):
    r = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return {
        "id": r.id,
        "name": r.name,
        "location": r.location,
        "address": r.address,
        "cuisine": r.cuisine,
        "rating": r.rating,
        "phone": r.phone,
        "opening_hours": r.opening_hours
    }

@router.get("/menu/{restaurant_id}")
def get_menu_by_restaurant(restaurant_id: str, db: Session = Depends(get_db)):
    items = db.query(MenuItem).filter(MenuItem.restaurant_id == restaurant_id).all()
    result = []
    for item in items:
        result.append({
            "id": item.id,
            "restaurant_id": item.restaurant_id,
            "item_name": item.item_name,
            "category": item.category,
            "price": item.price,
            "description": item.description,
            "is_vegetarian": item.is_vegetarian,
            "is_non_vegetarian": item.is_non_vegetarian,
            "spice_level": item.spice_level,
            "cuisine": item.cuisine,
            "availability": item.availability
        })
    return result
