import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Property, Inquiry, Lead

app = FastAPI(title="Real Estate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Real Estate Backend Running"}

# ------------------------------
# Properties
# ------------------------------

@app.post("/api/properties", response_model=dict)
def create_property(property: Property):
    try:
        prop_id = create_document("property", property)
        return {"id": prop_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class PropertiesResponse(BaseModel):
    items: List[dict]
    total: int

@app.get("/api/properties", response_model=PropertiesResponse)
def list_properties(
    q: Optional[str] = None,
    status: Optional[str] = Query(None, description="For Sale or For Rent"),
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    beds: Optional[int] = None,
    baths: Optional[float] = None,
    property_type: Optional[str] = None,
    city: Optional[str] = None,
    sort: Optional[str] = Query("newest", description="newest|price_asc|price_desc"),
    limit: int = 24,
):
    try:
        filter_dict = {}
        if status:
            filter_dict["status"] = status
        if beds is not None:
            filter_dict["beds"] = {"$gte": beds}
        if baths is not None:
            filter_dict["baths"] = {"$gte": baths}
        if property_type:
            filter_dict["property_type"] = property_type
        if city:
            filter_dict["location.city"] = city
        if min_price is not None or max_price is not None:
            price_filter = {}
            if min_price is not None:
                price_filter["$gte"] = min_price
            if max_price is not None:
                price_filter["$lte"] = max_price
            filter_dict["price"] = price_filter
        if q:
            # simple text search on title/description
            filter_dict["$or"] = [
                {"title": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}},
            ]
        # Sorting
        sort_spec = None
        if sort == "price_asc":
            sort_spec = [("price", 1)]
        elif sort == "price_desc":
            sort_spec = [("price", -1)]
        else:
            sort_spec = [("_id", -1)]  # newest

        # Execute
        cursor = db["property"].find(filter_dict)
        if sort_spec:
            cursor = cursor.sort(sort_spec)
        total = db["property"].count_documents(filter_dict)
        items = list(cursor.limit(limit))
        # Convert ObjectId to str
        for item in items:
            item["id"] = str(item.pop("_id"))
        return {"items": items, "total": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/properties/{property_id}")
def get_property(property_id: str):
    from bson import ObjectId
    try:
        doc = db["property"].find_one({"_id": ObjectId(property_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Property not found")
        doc["id"] = str(doc.pop("_id"))
        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------
# Leads & Inquiries
# ------------------------------

@app.post("/api/inquiries", response_model=dict)
def create_inquiry(inquiry: Inquiry):
    try:
        inquiry_id = create_document("inquiry", inquiry)
        return {"id": inquiry_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/leads", response_model=dict)
def create_lead(lead: Lead):
    try:
        lead_id = create_document("lead", lead)
        return {"id": lead_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------
# Health
# ------------------------------

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = getattr(db, 'name', None) or "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
