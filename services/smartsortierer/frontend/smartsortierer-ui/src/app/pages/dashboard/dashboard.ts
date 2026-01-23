import { Component, OnInit, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Api, HealthCheck, Stats, Document } from '../../services/api';

@Component({
  selector: 'app-dashboard',
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class Dashboard implements OnInit {
  private api = inject(Api);

  health = signal<HealthCheck | null>(null);
  stats = signal<Stats | null>(null);
  recentDocs = signal<Document[]>([]);
  loading = signal(true);
  error = signal<string | null>(null);

  ngOnInit() {
    this.loadDashboardData();
    // Refresh every 30 seconds
    setInterval(() => this.loadDashboardData(), 30000);
  }

  async loadDashboardData() {
    try {
      this.loading.set(true);
      this.error.set(null);

      // Load health check (no API key needed)
      this.api.getHealth().subscribe({
        next: (data) => this.health.set(data),
        error: (err) => console.error('Health check failed:', err)
      });

      // Load stats
      this.api.getStats().subscribe({
        next: (data) => this.stats.set(data),
        error: (err) => {
          console.error('Stats failed:', err);
          this.error.set('Failed to load statistics');
        }
      });

      // Load recent documents
      this.api.getDocuments(1, 5).subscribe({
        next: (data) => this.recentDocs.set(data.documents),
        error: (err) => console.error('Documents failed:', err)
      });

    } catch (err) {
      this.error.set('Failed to load dashboard data');
      console.error(err);
    } finally {
      this.loading.set(false);
    }
  }

  getStatusColor(status: string): string {
    const colors: Record<string, string> = {
      'ok': 'var(--good)',
      'degraded': 'var(--warn)',
      'failed': 'var(--bad)',
      'inbox': 'var(--muted)',
      'ingested': 'var(--accent)',
      'classified': 'var(--accent2)',
      'reviewed': 'var(--good)',
      'sorted': 'var(--good)',
      'archived': 'var(--muted)',
      'error': 'var(--bad)'
    };
    return colors[status] || 'var(--muted)';
  }

  formatFileSize(bytes: number | undefined): string {
    if (!bytes) return '0 B';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    return (bytes / (1024 * 1024 * 1024)).toFixed(1) + ' GB';
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  }

  getStatusEntries(): Array<{key: string, value: number}> {
    const stats = this.stats();
    if (!stats) return [];
    return Object.entries(stats.by_status).map(([key, value]) => ({ key, value }));
  }

  getTypeEntries(): Array<{key: string, value: number}> {
    const stats = this.stats();
    if (!stats) return [];
    return Object.entries(stats.by_type).map(([key, value]) => ({ key, value }));
  }
}
