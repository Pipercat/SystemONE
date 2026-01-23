import { Component, OnInit, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Api, Document, DocumentsResponse } from '../../services/api';

@Component({
  selector: 'app-documents',
  imports: [CommonModule, FormsModule],
  templateUrl: './documents.html',
  styleUrl: './documents.css'
})
export class Documents implements OnInit {
  private api = inject(Api);

  documents = signal<Document[]>([]);
  loading = signal(true);
  error = signal<string | null>(null);
  
  // Pagination
  currentPage = signal(1);
  pageSize = signal(20);
  totalDocs = signal(0);
  hasMore = signal(false);

  // Filters
  statusFilter = signal<string>('all');
  searchQuery = signal('');
  
  // View mode
  viewMode = signal<'table' | 'grid'>('table');
  
  // Upload
  showUploadDialog = signal(false);
  uploading = signal(false);
  uploadProgress = signal(0);

  ngOnInit() {
    this.loadDocuments();
  }
  
  openUploadDialog() {
    this.showUploadDialog.set(true);
  }
  
  closeUploadDialog() {
    this.showUploadDialog.set(false);
    this.uploadProgress.set(0);
  }
  
  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.uploadFiles(Array.from(input.files));
    }
  }
  
  uploadFiles(files: File[]) {
    this.uploading.set(true);
    this.uploadProgress.set(0);
    
    // TODO: Implement actual file upload to API
    // For now, simulate upload
    console.log('Uploading files:', files.map(f => f.name));
    
    let progress = 0;
    const interval = setInterval(() => {
      progress += 10;
      this.uploadProgress.set(progress);
      
      if (progress >= 100) {
        clearInterval(interval);
        this.uploading.set(false);
        this.closeUploadDialog();
        this.loadDocuments(); // Reload to show new files
        
        // Show success message
        alert(`${files.length} file(s) uploaded successfully!`);
      }
    }, 200);
  }

  loadDocuments() {
    this.loading.set(true);
    this.error.set(null);

    const status = this.statusFilter() === 'all' ? undefined : this.statusFilter();

    this.api.getDocuments(this.currentPage(), this.pageSize(), status).subscribe({
      next: (response: DocumentsResponse) => {
        this.documents.set(response.documents);
        this.totalDocs.set(response.total);
        this.hasMore.set(response.has_more);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set('Failed to load documents');
        console.error('Documents error:', err);
        this.loading.set(false);
      }
    });
  }

  onStatusFilterChange(status: string) {
    this.statusFilter.set(status);
    this.currentPage.set(1);
    this.loadDocuments();
  }

  onSearch() {
    // In future: implement search API call
    this.currentPage.set(1);
    this.loadDocuments();
  }

  nextPage() {
    if (this.hasMore()) {
      this.currentPage.update(p => p + 1);
      this.loadDocuments();
    }
  }

  previousPage() {
    if (this.currentPage() > 1) {
      this.currentPage.update(p => p - 1);
      this.loadDocuments();
    }
  }

  toggleViewMode() {
    this.viewMode.update(mode => mode === 'table' ? 'grid' : 'table');
  }

  getStatusColor(status: string): string {
    const colors: Record<string, string> = {
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
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  getFileIcon(mimeType: string): string {
    if (mimeType.includes('pdf')) return '📕';
    if (mimeType.includes('image')) return '🖼️';
    if (mimeType.includes('word') || mimeType.includes('document')) return '📘';
    if (mimeType.includes('excel') || mimeType.includes('spreadsheet')) return '📊';
    if (mimeType.includes('zip') || mimeType.includes('archive')) return '📦';
    return '📄';
  }

  getTotalPages(): number {
    return Math.ceil(this.totalDocs() / this.pageSize());
  }
}
