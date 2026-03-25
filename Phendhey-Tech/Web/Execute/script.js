/* ── Bhutan Lifestyle Study · script.js ── */

let visitorName = '';

// Paste your Apps Script Web App URL here
const SHEET_URL = 'https://script.google.com/macros/s/AKfycbys3-Yefk8RbNEMZFzBJ9xupG4WMWhitYAw1EfoJnQwDEI-miDb9jNC2bthJtGbLGib2A/exec';

/**
 * Silently logs the visitor's name and timestamp to Google Sheets.
 * Fails gracefully — never blocks the user flow.
 */
function logVisitor(name) {
  if (!SHEET_URL || SHEET_URL === 'YOUR_APPS_SCRIPT_URL') return;

  const now = new Date().toLocaleString('en-GB', {
    day:    '2-digit',
    month:  'short',
    year:   'numeric',
    hour:   '2-digit',
    minute: '2-digit',
    hour12: true,
  });

  fetch(SHEET_URL, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ name, time: now }),
    mode:    'no-cors',
  }).catch(() => {}); // silent — never blocks the user
}

/**
 * Validates the name input, logs the visit, and transitions to the overview screen.
 */
function submitName() {
  const input = document.getElementById('inp-name');
  const err   = document.getElementById('name-error');
  const name  = input.value.trim();

  if (!name) {
    err.style.display = 'block';
    return;
  }

  err.style.display = 'none';
  visitorName = name;

  logVisitor(name);

  document.getElementById('name-screen').style.display     = 'none';
  document.getElementById('overview-screen').style.display = 'block';
  document.getElementById('nav-name').textContent          = name;
  document.getElementById('greeting-name').textContent     = name;

  const bar = document.getElementById('greeting-bar');
  bar.style.display    = 'block';
  bar.style.opacity    = '0';
  bar.style.transition = 'opacity 0.35s ease';
  setTimeout(() => { bar.style.opacity = '1'; }, 60);

  window.scrollTo({ top: 0, behavior: 'instant' });
}

/**
 * Signs the user out and returns to the name screen.
 */
function doSignOut() {
  document.getElementById('overview-screen').style.display = 'none';
  document.getElementById('greeting-bar').style.display    = 'none';
  document.getElementById('name-screen').style.display     = 'flex';
  document.getElementById('inp-name').value                = '';
  document.getElementById('name-error').style.display      = 'none';
  visitorName = '';
}

// Allow pressing Enter on the name screen to submit
document.addEventListener('keydown', function (e) {
  const nameScreenVisible =
    document.getElementById('name-screen').style.display !== 'none';

  if (e.key === 'Enter' && nameScreenVisible) {
    submitName();
  }
});
