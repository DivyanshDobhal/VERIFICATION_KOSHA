/**
 * KOSHA LABS – Central Backend API Client
 * Capacitor & Mobile Web Compatible REST Client
 */

export interface ApiError {
  status: number;
  message: string;
  detail?: string;
}

class KoshaApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor() {
    this.baseUrl = '/api';
    this.token = localStorage.getItem('kosha_jwt_token');
  }

  public setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('kosha_jwt_token', token);
    } else {
      localStorage.removeItem('kosha_jwt_token');
    }
  }

  public getToken(): string | null {
    return this.token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    signal?: AbortSignal
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...(options.headers as Record<string, string>),
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        signal,
      });

      if (!response.ok) {
        let errorData: any = {};
        try {
          errorData = await response.json();
        } catch {
          errorData = { message: response.statusText };
        }

        const apiError: ApiError = {
          status: response.status,
          message: errorData.message || errorData.detail || errorData.error || 'Server error occurred',
          detail: errorData.detail,
        };

        if (response.status === 401) {
          // Token expired or invalid
          this.setToken(null);
        }

        throw apiError;
      }

      return (await response.json()) as T;
    } catch (err: any) {
      if (err.name === 'AbortError') {
        throw { status: 0, message: 'Request cancelled' };
      }
      if (err.status) {
        throw err;
      }
      // Network or offline fallback
      throw {
        status: 503,
        message: 'Network offline or unable to reach Kosha Labs Backend API.',
      } as ApiError;
    }
  }

  // --- Auth Endpoints ---
  async signup(data: {
    name: string;
    email: string;
    password?: string;
    role?: string;
    siteId?: string;
    badgeNumber?: string;
  }) {
    const res = await this.request<{
      access_token: string;
      operator: any;
    }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    this.setToken(res.access_token);
    return res;
  }

  async login(email: string, password?: string) {
    const res = await this.request<{
      access_token: string;
      operator: any;
    }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password: password || 'kosha2026' }),
    });
    this.setToken(res.access_token);
    return res;
  }

  async logout() {
    try {
      await this.request('/auth/logout', { method: 'POST' });
    } finally {
      this.setToken(null);
    }
  }

  async getMe() {
    return this.request('/auth/me');
  }

  // --- Worker Endpoints ---
  async getWorkers(search?: string, siteId?: string, status?: string) {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (siteId && siteId !== 'ALL') params.append('site_id', siteId);
    if (status && status !== 'ALL') params.append('status', status);

    return this.request<{ items: any[]; total: number }>(`/workers?${params.toString()}`);
  }

  async getWorker(workerId: string) {
    return this.request<any>(`/workers/${workerId}`);
  }

  async registerWorker(workerData: any) {
    return this.request<any>('/workers', {
      method: 'POST',
      body: JSON.stringify(workerData),
    });
  }

  async updateWorker(workerId: string, updates: any) {
    return this.request<any>(`/workers/${workerId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  async getWorkerSessions(workerId: string) {
    return this.request<any[]>(`/workers/${workerId}/sessions`);
  }

  // --- Biometric Recognition Endpoints ---
  async recognize(payload: {
    fingerprint_image_base64?: string;
    scanned_finger?: string;
    scenario_override?: string;
  }) {
    return this.request<any>('/biometrics/recognize', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async enrollFingerprint(payload: {
    worker_id: string;
    finger_type: string;
    fingerprint_image_base64: string;
  }) {
    return this.request<any>('/biometrics/enroll', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  // --- Sessions Endpoints ---
  async getSessions() {
    return this.request<any[]>('/sessions');
  }

  async createSession(payload: {
    worker_id: string;
    shift: string;
    gate: string;
    notes?: string;
    idempotency_key: string;
  }) {
    return this.request<any>('/sessions', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  // --- Recognition Review Endpoints ---
  async getReviews() {
    return this.request<any[]>('/recognition/reviews');
  }

  async approveReview(reviewId: string) {
    return this.request<any>(`/recognition/reviews/${reviewId}/approve`, {
      method: 'POST',
    });
  }

  async rejectReview(reviewId: string) {
    return this.request<any>(`/recognition/reviews/${reviewId}/reject`, {
      method: 'POST',
    });
  }

  // --- Analytics & Sites ---
  async getAnalyticsSummary() {
    return this.request<any>('/analytics/summary');
  }

  async getSites() {
    return this.request<any[]>('/sites');
  }
}

export const apiClient = new KoshaApiClient();
