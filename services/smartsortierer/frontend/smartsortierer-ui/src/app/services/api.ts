import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

export interface HealthCheck {
  status: string;
  service: string;
  version: string;
  phase: string;
  checks: {
    database: string;
    storage_root: string;
    environment: string;
  };
}

export interface Stats {
  total_documents: number;
  by_status: {
    inbox: number;
    ingested: number;
    classified: number;
    reviewed: number;
    sorted: number;
    archived: number;
    error: number;
  };
  by_type: Record<string, number>;
  recent_activity: {
    last_24h: number;
    last_7d: number;
    last_30d: number;
  };
}

export interface Document {
  id: number;
  original_filename: string;
  file_size_bytes: number;
  mime_type: string;
  status: string;
  file_sha256: string;
  category?: string | null;
  suggested_filename?: string | null;
  classification_confidence?: number | null;
  classification?: {
    document_type: string;
    confidence: number;
    category?: string;
    tags?: string[];
  };
  created_at: string;
  analyzed_at?: string | null;
  approved_at?: string | null;
  committed_at?: string | null;
  duplicate_of_doc?: number | null;
}

export interface DocumentsResponse {
  documents: Document[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

@Injectable({
  providedIn: 'root',
})
export class Api {
  private http = inject(HttpClient);
  private baseUrl = '/api';
  private apiKey = 'dev-test-key-change-in-production-min-32-chars-required';

  private getHeaders(): HttpHeaders {
    return new HttpHeaders({
      'x-ss-api-key': this.apiKey,
      'Content-Type': 'application/json'
    });
  }

  getHealth(): Observable<HealthCheck> {
    return this.http.get<HealthCheck>(`${this.baseUrl}/health`);
  }

  getStats(): Observable<Stats> {
    // Stats endpoint doesn't exist yet, return mock data
    return new Observable(observer => {
      this.getDocuments(1, 1000).subscribe({
        next: (response) => {
          const stats = this.calculateStats(response.documents);
          observer.next(stats);
          observer.complete();
        },
        error: (err) => observer.error(err)
      });
    });
  }

  private calculateStats(documents: Document[]): Stats {
    const byStatus: any = {
      inbox: 0,
      ingested: 0,
      classified: 0,
      reviewed: 0,
      sorted: 0,
      archived: 0,
      error: 0
    };
    
    const byType: Record<string, number> = {};
    const now = new Date();
    const last24h = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    const last7d = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    const last30d = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
    
    let count24h = 0, count7d = 0, count30d = 0;
    
    documents.forEach(doc => {
      // Count by status (API returns uppercase like "APPROVED", "INGESTED")
      const status = doc.status.toLowerCase();
      // Map API statuses to our expected format
      if (status === 'approved') {
        byStatus['reviewed']++;
      } else if (status === 'committed') {
        byStatus['sorted']++;
      } else if (status in byStatus) {
        byStatus[status]++;
      }
      
      // Count by type (use category field)
      if (doc.category) {
        const type = doc.category;
        byType[type] = (byType[type] || 0) + 1;
      }
      
      // Count recent activity
      const created = new Date(doc.created_at);
      if (created >= last24h) count24h++;
      if (created >= last7d) count7d++;
      if (created >= last30d) count30d++;
    });
    
    return {
      total_documents: documents.length,
      by_status: byStatus,
      by_type: byType,
      recent_activity: {
        last_24h: count24h,
        last_7d: count7d,
        last_30d: count30d
      }
    };
  }

  getDocuments(page: number = 1, pageSize: number = 20, status?: string): Observable<DocumentsResponse> {
    // API uses offset/limit, not page/pageSize
    const offset = (page - 1) * pageSize;
    let url = `${this.baseUrl}/docs/list?limit=${pageSize}&offset=${offset}`;
    if (status && status !== 'all') {
      url += `&status_filter=${status}`;
    }
    
    return this.http.get<any>(url, {
      headers: this.getHeaders()
    }).pipe(
      map((response: any) => ({
        documents: response.documents || [],
        total: response.total || 0,
        page: page,
        page_size: pageSize,
        has_more: (offset + pageSize) < (response.total || 0)
      }))
    );
  }

  getDocument(id: string): Observable<Document> {
    return this.http.get<Document>(`${this.baseUrl}/docs/${id}`, {
      headers: this.getHeaders()
    });
  }
}
