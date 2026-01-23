import { Routes } from '@angular/router';
import { Dashboard } from './pages/dashboard/dashboard';
import { Documents } from './pages/documents/documents';
import { Rules } from './pages/rules/rules';
import { Review } from './pages/review/review';

export const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: Dashboard },
  { path: 'documents', component: Documents },
  { path: 'rules', component: Rules },
  { path: 'review', component: Review },
];
