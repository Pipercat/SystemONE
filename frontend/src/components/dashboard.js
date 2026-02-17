import { renderHealthCard } from './healthcard.js';
import { renderPeetChat, initPeetChat } from './peet_chat.js';

function renderStaticCards() {
  return `
    <section class="card">
      <h3>PEET Status</h3>
      <p class="muted">Bereit · verbunden mit lokalen Services</p>
    </section>
    <section class="card">
      <h3>Storage Übersicht</h3>
      <p class="muted">NAS: 1.2 TB frei von 4.0 TB</p>
    </section>
    <section class="card">
      <h3>Letzte Tasks</h3>
      <ul class="muted">
        <li>OCR-Job #194 abgeschlossen</li>
        <li>Embedding Batch #52 gestartet</li>
        <li>Backup-Check erfolgreich</li>
      </ul>
    </section>
  `;
}

export async function renderDashboard() {
  let health = { api: 'offline', redis: 'offline', qdrant: 'offline', ollama: 'offline' };

  try {
    const response = await fetch('/api/peet/system/healthcard', {
      headers: { 'x-ss-api-key': localStorage.getItem('ss_api_key') || 'dev-test-key' },
    });
    if (response.ok) {
      health = await response.json();
    }
  } catch (_error) {
    // Fallback already set to offline
  }

  const main = document.getElementById('main-content');
  if (!main) return;

  main.innerHTML = `
    <main class="main">
      <div class="grid">
        ${renderHealthCard(health)}
        ${renderStaticCards()}
      </div>
      ${renderPeetChat()}
    </main>
  `;

  initPeetChat();
}
