const items = ['Dashboard', 'PEET', 'SmartSortierer', 'Smart Home', 'NAS', 'Settings'];

export function renderSidebar(active = 'Dashboard') {
  return `
    <aside class="sidebar">
      ${items
        .map(
          (item) =>
            `<button class="nav-item ${item === active ? 'active' : ''}" data-nav="${item}">${item}</button>`
        )
        .join('')}
    </aside>
  `;
}
