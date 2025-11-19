"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each Pydantic model represents a collection in your database.

Naming rule: Class name lowercased = collection name.
Example: class Property -> "property" collection
"""

from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl

# ------------------------------
# Core Real Estate Schemas
# ------------------------------

class Agent(BaseModel):
    name: str
    photo: Optional[HttpUrl] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    license: Optional[str] = None

class Location(BaseModel):
    street: str
    city: str
    state: str
    postal_code: str
    country: str = "USA"
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)

class Media(BaseModel):
    cover_image: Optional[HttpUrl] = None
    gallery: List[HttpUrl] = []
    video_url: Optional[HttpUrl] = None
    virtual_tour_url: Optional[HttpUrl] = None

class Financial(BaseModel):
    hoa_fees: Optional[float] = Field(None, ge=0)
    taxes: Optional[float] = Field(None, ge=0)

class Property(BaseModel):
    # Collection: "property"
    title: str
    status: str = Field(..., description="For Sale or For Rent")
    price: float = Field(..., ge=0)
    currency: str = "USD"
    location: Location
    beds: Optional[int] = Field(None, ge=0)
    baths: Optional[float] = Field(None, ge=0)
    area_sqft: Optional[int] = Field(None, ge=0)
    lot_size: Optional[float] = Field(None, ge=0)
    property_type: Optional[str] = None
    year_built: Optional[int] = None
    parking: Optional[str] = None
    amenities: List[str] = []
    description: Optional[str] = None
    media: Media = Media()
    financial: Financial = Financial()
    tags: List[str] = []
    agent: Optional[Agent] = None
    slug: Optional[str] = None

class Inquiry(BaseModel):
    # Collection: "inquiry"
    property_id: Optional[str] = None
    name: str
    email: str
    phone: Optional[str] = None
    message: Optional[str] = None
    source: str = "website"

class Lead(BaseModel):
    # Collection: "lead"
    name: str
    email: str
    phone: Optional[str] = None
    interest: Optional[str] = None  # buy/sell/rent
    preferred_area: Optional[str] = None

# Existing example schemas kept below for reference (unchanged)
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")
