// Global variables
let currentNoteId = null;
let notes = [];
let versions = [];

// DOM elements
const notesList = document.getElementById('notesList');
const editorContainer = document.getElementById('editorContainer');
const welcomeMessage = document.getElementById('welcomeMessage');
const noteTitle = document.getElementById('noteTitle');
const noteContent = document.getElementById('noteContent');
const saveBtn = document.getElementById('saveBtn');
const cancelBtn = document.getElementById('cancelBtn');
const newNoteBtn = document.getElementById('newNoteBtn');
const versionHistory = document.getElementById('versionHistory');
const versionsList = document.getElementById('versionsList');
const loadingSpinner = document.getElementById('loadingSpinner');
const confirmModal = document.getElementById('confirmModal');
const confirmMessage = document.getElementById('confirmMessage');
const confirmYes = document.getElementById('confirmYes');
const confirmNo = document.getElementById('confirmNo');

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    loadNotes();
    setupEventListeners();
});

// Event listeners
function setupEventListeners() {
    newNoteBtn.addEventListener('click', createNewNote);
    saveBtn.addEventListener('click', saveNote);
    cancelBtn.addEventListener('click', cancelEdit);
    confirmYes.addEventListener('click', confirmAction);
    confirmNo.addEventListener('click', hideConfirmModal);
}

// API functions
async function apiCall(url, options = {}) {
    showLoading();
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'An error occurred');
        }
        
        return await response.json();
    } catch (error) {
        showNotification('Error: ' + error.message, 'error');
        throw error;
    } finally {
        hideLoading();
    }
}

// Load all notes
async function loadNotes() {
    try {
        notes = await apiCall('/api/notes/');
        renderNotes();
    } catch (error) {
        console.error('Failed to load notes:', error);
    }
}

// Render notes list
function renderNotes() {
    if (notes.length === 0) {
        notesList.innerHTML = '<div class="empty-state"><i class="fas fa-sticky-note"></i><p>No notes yet. Create your first note!</p></div>';
        return;
    }
    
    notesList.innerHTML = notes.map(note => `
        <div class="note-item ${note.id === currentNoteId ? 'active' : ''}" data-note-id="${note.id}">
            <div class="note-title">${escapeHtml(note.title)}</div>
            <div class="note-preview">${escapeHtml(note.content.substring(0, 100))}${note.content.length > 100 ? '...' : ''}</div>
            <div class="note-meta">
                <span>v${note.version} • ${formatDate(note.updated_at)}</span>
                <div class="note-actions">
                    <button class="action-btn versions" onclick="event.stopPropagation(); showVersionHistory('${note.id}')" title="View versions">
                        <i class="fas fa-history"></i>
                    </button>
                    <button class="action-btn delete" onclick="event.stopPropagation(); deleteNote('${note.id}')" title="Delete note">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
    
    // Add click listeners to note items
    document.querySelectorAll('.note-item').forEach(item => {
        item.addEventListener('click', function(e) {
            // Check if the click was on an action button
            if (e.target.closest('.note-actions')) {
                return; // Don't select the note if clicking action buttons
            }
            const noteId = this.dataset.noteId;
            selectNote(noteId);
        });
    });
}

// Select a note for editing
async function selectNote(noteId) {
    try {
        const note = await apiCall(`/api/notes/${noteId}`);
        currentNoteId = noteId;
        noteTitle.value = note.title;
        noteContent.value = note.content;
        
        editorContainer.style.display = 'block';
        welcomeMessage.style.display = 'none';
        
        // Update active note in list
        document.querySelectorAll('.note-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-note-id="${noteId}"]`).classList.add('active');
        
        // Load versions for this note
        await loadNoteVersions(noteId);
        
    } catch (error) {
        console.error('Failed to load note:', error);
    }
}

// Create new note
function createNewNote() {
    currentNoteId = null;
    noteTitle.value = '';
    noteContent.value = '';
    
    editorContainer.style.display = 'block';
    welcomeMessage.style.display = 'none';
    versionHistory.style.display = 'none';
    
    noteTitle.focus();
}

// Save note
async function saveNote() {
    const title = noteTitle.value.trim();
    const content = noteContent.value.trim();
    
    if (!title || !content) {
        showNotification('Please fill in both title and content', 'error');
        return;
    }
    
    try {
        if (currentNoteId) {
            // Update existing note
            await apiCall(`/api/notes/${currentNoteId}`, {
                method: 'PUT',
                body: JSON.stringify({ title, content })
            });
            showNotification('Note updated successfully!', 'success');
        } else {
            // Create new note
            const newNote = await apiCall('/api/notes/', {
                method: 'POST',
                body: JSON.stringify({ title, content })
            });
            currentNoteId = newNote.id;
            showNotification('Note created successfully!', 'success');
        }
        
        await loadNotes();
        await loadNoteVersions(currentNoteId);
        
    } catch (error) {
        console.error('Failed to save note:', error);
    }
}

// Cancel editing
function cancelEdit() {
    editorContainer.style.display = 'none';
    welcomeMessage.style.display = 'block';
    versionHistory.style.display = 'none';
    currentNoteId = null;
}

// Delete note
function deleteNote(noteId) {
    const note = notes.find(n => n.id === noteId);
    showConfirmModal(
        `Are you sure you want to delete "${note.title}"?`,
        () => performDelete(noteId)
    );
}

async function performDelete(noteId) {
    try {
        console.log('Deleting note:', noteId);
        await apiCall(`/api/notes/${noteId}`, { method: 'DELETE' });
        console.log('Note deleted successfully');
        showNotification('Note deleted successfully!', 'success');
        
        // Reload notes to update the UI
        await loadNotes();
        
        // If we were editing the deleted note, cancel edit mode
        if (currentNoteId === noteId) {
            cancelEdit();
        }
    } catch (error) {
        console.error('Failed to delete note:', error);
        showNotification('Failed to delete note: ' + error.message, 'error');
    }
}

// Load note versions
async function loadNoteVersions(noteId) {
    try {
        versions = await apiCall(`/api/notes/${noteId}/versions`);
        renderVersions();
    } catch (error) {
        console.error('Failed to load versions:', error);
    }
}

// Show version history
function showVersionHistory(noteId) {
    if (currentNoteId !== noteId) {
        selectNote(noteId);
    }
    versionHistory.style.display = 'block';
    loadNoteVersions(noteId);
}

// Render versions
function renderVersions() {
    if (versions.length === 0) {
        versionsList.innerHTML = '<div class="empty-state">No versions available</div>';
        return;
    }
    
    versionsList.innerHTML = versions.map(version => `
        <div class="version-item">
            <div class="version-header">
                <span class="version-number">Version ${version.version}</span>
                <span class="version-date">${formatDate(version.created_at)}</span>
            </div>
            <div class="version-content">
                <strong>${escapeHtml(version.title)}</strong><br>
                ${escapeHtml(version.content.substring(0, 150))}${version.content.length > 150 ? '...' : ''}
            </div>
            <div class="version-actions">
                <button class="btn btn-primary" onclick="restoreVersion('${version.id}')">
                    <i class="fas fa-undo"></i> Restore
                </button>
            </div>
        </div>
    `).join('');
}

// Restore version
function restoreVersion(versionId) {
    showConfirmModal(
        'Are you sure you want to restore this version? This will create a new version with the restored content.',
        () => performRestore(versionId)
    );
}

async function performRestore(versionId) {
    try {
        await apiCall(`/api/notes/${currentNoteId}/restore/${versionId}`, {
            method: 'POST'
        });
        showNotification('Version restored successfully!', 'success');
        await loadNotes();
        await loadNoteVersions(currentNoteId);
        
        // Refresh the current note
        await selectNote(currentNoteId);
    } catch (error) {
        console.error('Failed to restore version:', error);
    }
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

function showLoading() {
    loadingSpinner.style.display = 'flex';
}

function hideLoading() {
    loadingSpinner.style.display = 'none';
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#48bb78' : type === 'error' ? '#f56565' : '#4299e1'};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 1001;
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 500;
        animation: slideIn 0.3s ease;
    `;
    
    // Add animation keyframes
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

function showConfirmModal(message, onConfirm) {
    confirmMessage.textContent = message;
    confirmModal.style.display = 'flex';
    
    // Remove existing listeners
    const newConfirmYes = confirmYes.cloneNode(true);
    const newConfirmNo = confirmNo.cloneNode(true);
    confirmYes.parentNode.replaceChild(newConfirmYes, confirmYes);
    confirmNo.parentNode.replaceChild(newConfirmNo, confirmNo);
    
    // Add new listeners
    newConfirmYes.addEventListener('click', () => {
        hideConfirmModal();
        onConfirm();
    });
    newConfirmNo.addEventListener('click', hideConfirmModal);
}

function hideConfirmModal() {
    confirmModal.style.display = 'none';
}
