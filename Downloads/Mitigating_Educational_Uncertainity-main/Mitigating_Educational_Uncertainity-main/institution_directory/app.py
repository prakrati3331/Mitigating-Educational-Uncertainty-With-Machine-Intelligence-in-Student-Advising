"""
Institution Directory FastAPI Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from institution_backend import InstitutionBackend

app = FastAPI(title="Institution Directory API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize backend
backend = InstitutionBackend()

# Serve static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    """Serve the main HTML file"""
    return FileResponse("templates/institution_directory.html")

@app.get("/api/institutions")
async def get_institutions():
    """Get all institutions"""
    return backend.get_all_institutions()

@app.get("/api/institutions/category/{category}")
async def get_institutions_by_category(category: str):
    """Get institutions by category"""
    return backend.get_institutions_by_category(category)

@app.get("/api/institutions/state/{state}")
async def get_institutions_by_state(state: str):
    """Get institutions by state"""
    return backend.get_institutions_by_state(state)

@app.get("/api/institutions/{institution_id}")
async def get_institution_details(institution_id: str):
    """Get institution details"""
    return backend.get_institution_details(institution_id)

@app.get("/api/institutions/search/{query}")
async def search_institutions(query: str):
    """Search institutions"""
    return backend.search_institutions(query)

@app.get("/api/institutions/top")
async def get_top_institutions(limit: int = 10):
    """Get top institutions"""
    return backend.get_top_institutions(limit)

@app.get("/api/states")
async def get_states_list():
    """Get list of states"""
    return backend.get_states_list()

@app.post("/api/institutions/filter")
async def filter_institutions(filters: dict):
    """Filter institutions"""
    return backend.filter_institutions(filters)

@app.post("/api/college-selection/save")
async def save_college_selection(data: dict):
    """Save college selection"""
    user_id = data.get("user_id")
    selected_colleges = data.get("selected_colleges", [])
    
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")
    
    return backend.save_college_selection(user_id, selected_colleges)

@app.get("/api/college-selection/{user_id}")
async def get_college_selection(user_id: str):
    """Get college selection"""
    return backend.get_college_selection(user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
