/**
 * KOSHA LABS – Fingerprint ML Biometrics Service
 * Integrates client scanner acquisition, image upload fallback, and FastAPI/TensorFlow model inference.
 */

export interface MlHealthStatus {
  connected: boolean;
  endpoint: string;
  mode: 'FASTAPI_LIVE_MODEL' | 'BUILTIN_DETERMINISTIC_ENGINE';
  model_configured: boolean;
  model_file?: string;
  model_info?: {
    target_path?: string;
    embedding_dimension?: number;
    framework?: string;
    similarity_threshold?: number;
    [key: string]: any;
  };
  message?: string;
}

export interface CandidateResult {
  worker_id: string;
  worker_name: string;
  department: string;
  similarity_score: number;
  confidence_percent: number;
}

export interface RecognitionResult {
  status: 'MATCH' | 'UNCERTAIN' | 'NO_MATCH';
  worker_id?: string;
  worker_name?: string;
  confidence_score: number;
  verification_required: boolean;
  matched_worker?: {
    id: string;
    worker_id: string;
    name: string;
    age: number;
    weight: number;
    department: string;
    siteName: string;
    sessionsCount: number;
  };
  candidates: CandidateResult[];
  review_id?: string;
  model_version?: string;
  message?: string;
}

export interface ExtractionResult {
  status: string;
  embedding_dimension: number;
  quality_score: number;
  finger_type: string;
  embedding: number[];
  is_duplicate: boolean;
  duplicate_match?: {
    worker_id: string;
    worker_name: string;
    similarity: number;
    finger: string;
    worker?: any;
  } | null;
  highest_similarity: number;
  model_version: string;
}

class BiometricsService {
  private customEndpointKey = 'kosha_ml_endpoint';

  public getSavedEndpoint(): string {
    return localStorage.getItem(this.customEndpointKey) || 'http://localhost:8000';
  }

  public setSavedEndpoint(url: string) {
    localStorage.setItem(this.customEndpointKey, url);
  }

  public async getHealth(): Promise<MlHealthStatus> {
    try {
      const res = await fetch('/api/ml/health');
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      // Fallback
    }
    return {
      connected: false,
      endpoint: this.getSavedEndpoint(),
      mode: 'BUILTIN_DETERMINISTIC_ENGINE',
      model_configured: true,
      message: 'FastAPI service offline. Built-in 128D engine active.',
    };
  }

  public async updateConfig(url: string): Promise<{ success: boolean; message: string }> {
    try {
      this.setSavedEndpoint(url);
      const res = await fetch('/api/ml/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });
      if (res.ok) {
        const data = await res.json();
        return { success: true, message: data.message };
      }
      return { success: false, message: 'Server rejected configuration.' };
    } catch (e: any) {
      return { success: false, message: e.message || 'Failed to update config.' };
    }
  }

  public async extract(params: {
    imageBase64?: string;
    fingerType: string;
    workerHint?: string;
    forceDuplicate?: boolean;
  }): Promise<ExtractionResult> {
    const res = await fetch('/api/ml/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image_base64: params.imageBase64,
        finger_type: params.fingerType,
        worker_hint: params.workerHint,
        force_duplicate: params.forceDuplicate,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || 'Biometric template extraction failed.');
    }

    return await res.json();
  }

  public async recognize(params: {
    imageBase64?: string;
    fingerType?: string;
    scenarioOverride?: 'MATCH' | 'UNCERTAIN' | 'NO_MATCH';
    targetWorkerId?: string;
  }): Promise<RecognitionResult> {
    const res = await fetch('/api/biometrics/recognize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image_base64: params.imageBase64,
        finger_type: params.fingerType,
        scenario_override: params.scenarioOverride,
        target_worker_id: params.targetWorkerId,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || 'Recognition service failure.');
    }

    return await res.json();
  }

  /**
   * Reads an uploaded scanner image (BMP, PNG, JPG) and returns base64 data URL
   */
  public async fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        if (typeof reader.result === 'string') {
          resolve(reader.result);
        } else {
          reject(new Error('Invalid image buffer'));
        }
      };
      reader.onerror = (err) => reject(err);
      reader.readAsDataURL(file);
    });
  }
}

export const biometricsService = new BiometricsService();
