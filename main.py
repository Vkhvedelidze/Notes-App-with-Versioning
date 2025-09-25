from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from datetime import datetime
import uuid

app = FastAPI(title="Notes App with Versioning", version="1.0.0")


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class NoteCreate(BaseModel):
    title: str
    content: str

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class Note(BaseModel):
    id: str
    title: str
    content: str
    created_at: str
    updated_at: str
    version: int

class NoteVersion(BaseModel):
    id: str
    note_id: str
    title: str
    content: str
    version: int
    created_at: str

DATA_FILE = "notes_data.json"

def load_data():
    """Load notes data from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"notes": {}, "versions": {}}

def save_data(data):
    """Save notes data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def create_note_version(note_id: str, title: str, content: str, version: int):
    """Create a new version of a note"""
    version_id = str(uuid.uuid4())
    version_data = {
        "id": version_id,
        "note_id": note_id,
        "title": title,
        "content": content,
        "version": version,
        "created_at": datetime.now().isoformat()
    }
    return version_data

# API Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main notes app interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/notes/")
async def create_note(note: NoteCreate):
    """Create a new note"""
    data = load_data()
    note_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    new_note = {
        "id": note_id,
        "title": note.title,
        "content": note.content,
        "created_at": now,
        "updated_at": now,
        "version": 1
    }
    
    version_data = create_note_version(note_id, note.title, note.content, 1)
    
    data["notes"][note_id] = new_note
    data["versions"][version_data["id"]] = version_data
    
    save_data(data)
    return new_note

@app.get("/api/notes/")
async def get_notes():
    """Get all notes"""
    data = load_data()
    return list(data["notes"].values())

@app.get("/api/notes/{note_id}")
async def get_note(note_id: str):
    """Get a specific note"""
    data = load_data()
    if note_id not in data["notes"]:
        raise HTTPException(status_code=404, detail="Note not found")
    return data["notes"][note_id]

@app.put("/api/notes/{note_id}")
async def update_note(note_id: str, note_update: NoteUpdate):
    """Update a note and create a new version"""
    data = load_data()
    if note_id not in data["notes"]:
        raise HTTPException(status_code=404, detail="Note not found")
    
    existing_note = data["notes"][note_id]
    new_version = existing_note["version"] + 1
    
    # Create new version before updating
    version_data = create_note_version(
        note_id,
        note_update.title or existing_note["title"],
        note_update.content or existing_note["content"],
        new_version
    )
    
    # Update the note
    updated_note = existing_note.copy()
    if note_update.title is not None:
        updated_note["title"] = note_update.title
    if note_update.content is not None:
        updated_note["content"] = note_update.content
    updated_note["updated_at"] = datetime.now().isoformat()
    updated_note["version"] = new_version
    
    data["notes"][note_id] = updated_note
    data["versions"][version_data["id"]] = version_data
    
    save_data(data)
    return updated_note

@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: str):
    """Delete a note"""
    data = load_data()
    if note_id not in data["notes"]:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Also delete all versions
    versions_to_delete = [v_id for v_id, v_data in data["versions"].items() 
                         if v_data["note_id"] == note_id]
    
    for v_id in versions_to_delete:
        del data["versions"][v_id]
    
    del data["notes"][note_id]
    save_data(data)
    return {"message": "Note deleted successfully"}

@app.get("/api/notes/{note_id}/versions")
async def get_note_versions(note_id: str):
    """Get all versions of a specific note"""
    data = load_data()
    if note_id not in data["notes"]:
        raise HTTPException(status_code=404, detail="Note not found")
    
    versions = [v_data for v_data in data["versions"].values() 
               if v_data["note_id"] == note_id]
    return sorted(versions, key=lambda x: x["version"], reverse=True)

@app.post("/api/notes/{note_id}/restore/{version_id}")
async def restore_note_version(note_id: str, version_id: str):
    """Restore a note to a specific version"""
    data = load_data()
    if note_id not in data["notes"]:
        raise HTTPException(status_code=404, detail="Note not found")
    
    if version_id not in data["versions"]:
        raise HTTPException(status_code=404, detail="Version not found")
    
    version_data = data["versions"][version_id]
    if version_data["note_id"] != note_id:
        raise HTTPException(status_code=400, detail="Version does not belong to this note")
    
    # Create new version with restored content
    existing_note = data["notes"][note_id]
    new_version = existing_note["version"] + 1
    
    # Create version record for the restore action
    restore_version = create_note_version(
        note_id,
        version_data["title"],
        version_data["content"],
        new_version
    )
    
    # Update the note with restored content
    restored_note = existing_note.copy()
    restored_note["title"] = version_data["title"]
    restored_note["content"] = version_data["content"]
    restored_note["updated_at"] = datetime.now().isoformat()
    restored_note["version"] = new_version
    
    data["notes"][note_id] = restored_note
    data["versions"][restore_version["id"]] = restore_version
    
    save_data(data)
    return restored_note

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
