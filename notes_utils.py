from macnotesapp import NotesApp

def get_notes():
    notesapp = NotesApp()
    notes = notesapp.notes()
    return notes

