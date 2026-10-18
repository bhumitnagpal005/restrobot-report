from typing import Optional, List
from pydantic import BaseModel, Field

class ExtractedConstraints(BaseModel):
    dietary_preference: Optional[str] = Field(None, description="'vegetarian' or 'non-vegetarian'")
    max_price: Optional[float] = Field(None, description="Maximum price limit in INR")
    min_price: Optional[float] = Field(None, description="Minimum price limit in INR")
    spice_level: Optional[str] = Field(None, description="Desired spice level")
    restaurant_name: Optional[str] = Field(None, description="Specific restaurant name if mentioned")
    cuisine: Optional[str] = Field(None, description="Cuisine type")
    category: Optional[str] = Field(None, description="Food category (e.g., pizza, burger, biryani, roll)")
    location: Optional[str] = Field(None, description="Location context")
    food_item: Optional[str] = Field(None, description="Specific food item keyword")
    hard_constraints: List[str] = Field(default_factory=list, description="List of active hard constraint keys")

    def dict_summary(self) -> dict:
        res = {}
        if self.dietary_preference:
            res["Diet"] = self.dietary_preference.capitalize()
        if self.max_price is not None:
            res["Max Price"] = f"≤ ₹{self.max_price:.0f}"
        if self.min_price is not None:
            res["Min Price"] = f"≥ ₹{self.min_price:.0f}"
        if self.spice_level:
            res["Spice Level"] = self.spice_level.capitalize()
        if self.restaurant_name:
            res["Restaurant"] = self.restaurant_name
        if self.cuisine:
            res["Cuisine"] = self.cuisine
        if self.category:
            res["Category"] = self.category
        if self.location:
            res["Location"] = self.location
        if self.food_item:
            res["Food Item"] = self.food_item
        return res
