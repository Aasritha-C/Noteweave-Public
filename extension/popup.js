const queryInput = document.getElementById('queryInput');
const results = document.getElementById('results');

function displayTriplets(triplets) {
  for (const { subject, predicate, object } of triplets) {
    const note = document.createElement('div');
    note.className = 'note';
    note.textContent = `${subject} ${predicate.replace(/_/g, ' ')} ${object}`;
    results.appendChild(note);
  }
}

async function search(askQuestion) {
  const query = queryInput.value.trim();
  if (!query) {
    results.textContent = askQuestion ? 'Enter a question first.' : 'Enter a subject first.';
    return;
  }

  const encoded = encodeURIComponent(query);
  const route = askQuestion ? `/query?q=${encoded}` : `/query/${encoded}`;
  results.textContent = 'Searching...';

  try {
    const response = await fetch(`http://127.0.0.1:8000${route}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();

    if (data.status !== 'success') {
      results.textContent = data.message || 'No records found.';
      return;
    }

    results.replaceChildren();
    if (askQuestion) {
      const answer = document.createElement('div');
      answer.style.whiteSpace = 'pre-line';
      answer.textContent = data.answer;
      results.appendChild(answer);
      for (const path of data.evidence_paths || []) {
        displayTriplets(path);
      }
    } else {
      displayTriplets(data.triplets);
    }
  } catch (error) {
    results.textContent = 'Error connecting to the Noteweave server.';
    console.error(error);
  }
}

document.getElementById('searchBtn').addEventListener('click', () => search(false));
document.getElementById('askBtn').addEventListener('click', () => search(true));
queryInput.focus();

const notesPanel = document.getElementById('notesPanel');
const noteInput = document.getElementById('noteInput');
const saveNoteButton = document.getElementById('saveNoteBtn');
const noteStatus = document.getElementById('noteStatus');
const recentNotes = document.getElementById('recentNotes');
const notesUrl = 'http://127.0.0.1:8000/notes';

async function refreshNotes() {
  try {
    const response = await fetch(notesUrl);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const { notes } = await response.json();
    recentNotes.replaceChildren();
    for (const note of notes) {
      const item = document.createElement('li');
      item.textContent = note.text;
      recentNotes.appendChild(item);
    }
  } catch (error) {
    noteStatus.textContent = 'Could not load recent notes.';
    console.error(error);
  }
}

notesPanel.addEventListener('toggle', () => {
  if (notesPanel.open) refreshNotes();
});

saveNoteButton.addEventListener('click', async () => {
  const text = noteInput.value.trim();
  if (!text) {
    noteStatus.textContent = 'Enter some note text.';
    return;
  }

  saveNoteButton.disabled = true;
  try {
    const response = await fetch(notesUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    if (noteInput.value.trim() === text) noteInput.value = '';
    noteStatus.textContent = 'Note saved.';
    await refreshNotes();
  } catch (error) {
    noteStatus.textContent = 'Could not save the note.';
    console.error(error);
  } finally {
    saveNoteButton.disabled = false;
  }
});
