export function renderHeader() {
  const now = new Date();
  return `
    <header class="topbar">
      <div class="brand">
        <div class="logo" aria-hidden="true"></div>
        <div>SystemONE</div>
        <div class="status-pill"><span class="dot ok"></span>System Online</div>
      </div>
      <div id="clock" class="muted">${now.toLocaleString('de-DE')}</div>
    </header>
  `;
}

export function startClock() {
  const clock = document.getElementById('clock');
  if (!clock) return;
  const update = () => {
    clock.textContent = new Date().toLocaleString('de-DE', {
      weekday: 'short',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };
  update();
  setInterval(update, 1000);
}
