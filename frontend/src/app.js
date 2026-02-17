import { renderHeader, startClock } from './components/header.js';
import { renderSidebar } from './components/sidebar.js';
import { renderDashboard } from './components/dashboard.js';

const app = document.getElementById('app');

app.innerHTML = `
  <div class="layout">
    ${renderHeader()}
    <div class="content">
      ${renderSidebar('Dashboard')}
      <div id="main-content"></div>
    </div>
  </div>
`;

startClock();
renderDashboard();
