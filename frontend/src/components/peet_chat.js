export function renderPeetChat() {
  return `
    <section class="card">
      <h3>PEET Chat</h3>
      <div id="chat-window" class="chat-window"></div>
      <div class="chat-controls">
        <input id="chat-input" type="text" placeholder="Frag PEET etwas ..." />
        <button id="chat-send" type="button">Send</button>
      </div>
    </section>
  `;
}

function appendMessage(role, text) {
  const chat = document.getElementById('chat-window');
  if (!chat) return;
  const el = document.createElement('div');
  el.className = `message ${role}`;
  el.textContent = text;
  chat.appendChild(el);
  chat.scrollTop = chat.scrollHeight;
}

export function initPeetChat() {
  const input = document.getElementById('chat-input');
  const sendButton = document.getElementById('chat-send');
  if (!input || !sendButton) return;

  const send = async () => {
    const message = input.value.trim();
    if (!message) return;

    appendMessage('user', message);
    input.value = '';

    try {
      const response = await fetch('/api/peet/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-ss-api-key': localStorage.getItem('ss_api_key') || 'dev-test-key',
        },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        throw new Error(`PEET request failed (${response.status})`);
      }

      const data = await response.json();
      appendMessage('assistant', data.reply || 'Keine Antwort erhalten.');
    } catch (error) {
      appendMessage('assistant', `Fehler: ${error.message}`);
    }
  };

  sendButton.addEventListener('click', send);
  input.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      send();
    }
  });

  appendMessage('assistant', 'Hi, ich bin PEET. Wie kann ich helfen?');
}
