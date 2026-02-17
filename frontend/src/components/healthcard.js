function badge(status) {
  const normalized = String(status || 'offline').toLowerCase();
  if (normalized === 'online' || normalized === 'ok') return '<span class="badge ok">online</span>';
  if (normalized === 'degraded' || normalized === 'warning') return '<span class="badge warn">degraded</span>';
  return '<span class="badge err">offline</span>';
}

export function renderHealthCard(data) {
  const map = {
    API: data.api,
    Redis: data.redis,
    Qdrant: data.qdrant,
    Ollama: data.ollama,
  };

  return `
    <section class="card">
      <h3>Health Card</h3>
      <div class="health-list">
        ${Object.entries(map)
          .map(([name, status]) => `<div class="health-row"><span>${name}</span>${badge(status)}</div>`)
          .join('')}
      </div>
    </section>
  `;
}
