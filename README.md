# Notes App with Versioning

A simple notes application built with Python FastAPI and HTML/CSS/JavaScript. This app lets you create, edit, and delete notes while keeping track of all changes through a version history system.

## What This App Does

This is a web-based notes application that allows you to:
- Create new notes with titles and content
- Edit existing notes (automatically creates new versions)
- Delete notes completely
- View the complete history of changes for any note
- Restore any previous version of a note

## Features

### Core Features
- **Create Notes**: Add new notes with titles and content
- **Read Notes**: View all your notes in a clean list
- **Update Notes**: Edit existing notes, which automatically creates new versions
- **Delete Notes**: Remove notes completely along with their version history
- **Version History**: Every change is tracked with timestamps
- **Restore Versions**: Go back to any previous version of a note

### Technical Features
- **RESTful API**: Clean API design that follows web standards 
- **Persistent Storage**: Your notes are saved to a JSON file
- **Real-time Updates**: Changes appear immediately without refreshing
- **Error Handling**: Clear error messages when something goes wrong

## How to Run the Application

### Prerequisites
- Python and pip installed

### Installation Steps

1. **Download the project files or copy Git repo** 

2. **Install the required packages**:
   ```
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```
   python run.py
   ```
   Or alternatively:
   ```
   python main.py
   ```

4. **Open your web browser** and go to:
   ```
   http://localhost:8000
   ```

### Alternative Running Method
You can also use the convenient run script:
```
python run.py
```

## How to Use the Application

### Creating a Note
1. Click the "New Note" button
2. Enter a title for your note
3. Write your content in the text area
4. Click "Save" to create the note

### Editing a Note
1. Click on any note in the notes list
2. The note will open in the editor
3. Make your changes to the title or content
4. Click "Save" to update the note (this creates a new version)

### Viewing Version History
1. Click on a note to select it
2. Click the history icon (clock symbol) next to the note
3. You'll see all previous versions with timestamps
4. Click "Restore" on any version to go back to that version

### Deleting a Note
1. Click the trash icon next to any note
2. Confirm the deletion in the popup dialog
3. The note and all its versions will be permanently deleted

### Project Structure

-**main.py**:                  Main application file (FastAPI backend)

-**run.py**:                   Simple script to start the application

-**test_app.py**:              Test suite for the application

-**requirements.txt**:         Python packages needed

-**README.md**:               Project description

-**templates/index.html**:     Main web page

-**static/style.css**:         Styling for the web page

-**static/script.js**:         JavaScript functionality


## Technical Details

### Backend (Python FastAPI)
- **Framework**: FastAPI for the web API
- **Data Storage**: JSON file for simplicity
- **API Endpoints**: RESTful design with proper HTTP methods (assignment requirement)
- **Version Management**: Automatic version tracking for all changes

### Frontend (HTML/CSS/JavaScript)
- **HTML**: Clean structure
- **CSS**: Modern styling with responsive design
- **JavaScript**: Vanilla JavaScript (no frameworks)
- **API Integration**: Direct communication with the backend

### Data Storage
- **Format**: JSON file (notes_data.json)
- **Structure**: Separate storage for notes and versions
- **Backup**: Easy to backup by copying the JSON file

## API Endpoints

RESTful API endpoints:

- `GET /api/notes/` - Get all notes
- `POST /api/notes/` - Create a new note
- `GET /api/notes/{id}` - Get a specific note
- `PUT /api/notes/{id}` - Update a note
- `DELETE /api/notes/{id}` - Delete a note
- `GET /api/notes/{id}/versions` - Get all versions of a note
- `POST /api/notes/{id}/restore/{version_id}` - Restore a note to a previous version

You can test these endpoints using tools like Postman or curl, or view the interactive documentation at http://localhost:8000/docs when the app is running.

## Testing

### Running Tests
To run the test suite:
```
python test_app.py
```

The test suite includes:
- Creating and retrieving notes
- Updating notes and version tracking
- Deleting notes
- Version history functionality
- Restore functionality
- Error handling

## Software Development Life Cycle (SDLC)

### Chosen SDLC Model: Agile Development

**Justification for Agile Model:**
- **Rapid Prototyping**: The assignment requires a working application with multiple features quickly
- **Flexibility**: Individual assignment with evolving requirements needs adaptability
- **Feature-Driven Development**: Assignment specifically requires 2+ core features plus a third feature
- **Continuous Integration**: Promotes continuous testing and integration for seamless functionality
- **Documentation Balance**: Emphasizes working software while maintaining necessary documentation

### SDLC Implementation:
1. **Planning**: Analyzed assignment requirements and selected technology stack
2. **Analysis**: Defined functional and non-functional requirements
3. **Design**: Created system architecture and API design
4. **Implementation**: Built FastAPI backend and HTML/CSS/JavaScript frontend
5. **Testing**: Performed unit testing and integration testing
6. **Deployment**: Set up local development environment
7. **Maintenance**: Code review and documentation updates

## System Architecture

### Architecture Diagram
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Data Layer    │
│   (HTML/CSS/JS) │◄──►│   (FastAPI)     │◄──►│   (JSON Files)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Overview
- **Frontend**: HTML templates, CSS styling, JavaScript functionality
- **Backend**: FastAPI application with RESTful API endpoints
- **Data Layer**: JSON file storage for notes and version history
- **API Layer**: RESTful endpoints for CRUD operations and versioning

### Data Flow
1. User interacts with HTML interface
2. JavaScript sends HTTP requests to FastAPI backend
3. Backend processes requests and updates JSON data files
4. Backend returns responses to frontend
5. Frontend updates UI based on responses

## Assignment Requirements

This project meets all the requirements for the Individual Assignment 1:

**Required Core Features (2+ needed):**
- **CRUD Operations**: Complete create, read, update, delete functionality
- **Persistent Storage**: JSON-based data storage  
- **RESTful API Endpoints**: Full API with proper HTTP methods

**Third Feature (for higher grade):**
- **Versioning System**: Advanced version history with restore functionality

**Documentation Requirements:**
- **Setup Instructions**: Complete installation and usage guide
- **Version Control**: Git repository with meaningful commits

**Additional Features:**
- Modern web interface with responsive design
- Real-time updates without page refresh
- Comprehensive error handling

## Future Improvements

This application can be extended with:
- User authentication and accounts
- Database storage instead of JSON files
- Real-time collaboration features
- Cloud storage integration
- Advanced search functionality
