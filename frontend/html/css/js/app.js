const notesInput = document.getElementById('notes-input');
const generateBtn = document.getElementById('generate-btn');
const loadingIndicator = document.getElementById('loading-indicator');
const flashcardsSection = document.getElementById('flashcards-section');
const flashcardContainer = document.getElementById('flashcard-container');
const prevBtn = document.getElementById('prev-card');
const nextBtn = document.getElementById('next-card');
const flipBtn = document.getElementById('flip-card');

let flashcards = [];
let currentCard = 0;
let showFront = true;

// UI State functions
function showLoading(show) {
  loadingIndicator.style.display = show ? 'block' : 'none';
  generateBtn.disabled = show;
}
function showFlashcardsSection(show) {
  flashcardsSection.style.display = show ? 'flex' : 'none';
}
function renderFlashcard() {
  if (!flashcards.length) return;
  const card = flashcards[currentCard];
  flashcardContainer.textContent = showFront ? card.front : card.back;
}
// Navigation
function updateNavButtons() {
  prevBtn.disabled = (currentCard === 0);
  nextBtn.disabled = (currentCard === flashcards.length - 1);
}
// User actions
async function generateFlashcards() {
  const notes = notesInput.value.trim();
  if (!notes) return alert('Please paste your notes.');
  showLoading(true);
  showFlashcardsSection(false);
  try {
    const resp = await fetch('http://localhost:5001/api/generate_flashcards', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ notes })
    });
    if (!resp.ok) throw new Error('Unable to generate flashcards.');
    const data = await resp.json();
    // Expects data.flashcards = [ { front: '', back: '' }, ... ]
    if (!data.flashcards || !data.flashcards.length) throw new Error('No flashcards returned.');
    flashcards = data.flashcards;
    currentCard = 0;
    showFront = true;
    showFlashcardsSection(true);
    renderFlashcard();
    updateNavButtons();
  } catch (e) {
    alert(e.message || 'An error occurred.');
  } finally {
    showLoading(false);
  }
}

function flipCard() {
  if (!flashcards.length) return;
  showFront = !showFront;
  renderFlashcard();
}
function showPrevCard() {
  if (currentCard > 0) {
    currentCard--;
    showFront = true;
    renderFlashcard();
    updateNavButtons();
  }
}
function showNextCard() {
  if (currentCard < flashcards.length - 1) {
    currentCard++;
    showFront = true;
    renderFlashcard();
    updateNavButtons();
  }
}
// Event Listeners
generateBtn.addEventListener('click', generateFlashcards);
flipBtn.addEventListener('click', flipCard);
prevBtn.addEventListener('click', showPrevCard);
nextBtn.addEventListener('click', showNextCard);

// Keyboard navigation
window.addEventListener('keydown', (e) => {
  if (!flashcards.length) return;
  if (e.key === 'ArrowLeft') showPrevCard();
  if (e.key === 'ArrowRight') showNextCard();
  if (e.key === ' ') {
    e.preventDefault();
    flipCard();
  }
});
