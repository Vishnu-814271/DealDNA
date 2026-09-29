const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api/v1';

export async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      'X-Correlation-ID': `web-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`,
    },
    cache: 'no-store',
  });

  if (!response.ok) {
    let errMessage = `Request failed: ${response.status}`;
    try {
      const errData = await response.json();
      if (errData && errData.message) {
        errMessage = errData.message;
      }
    } catch {
      // ignore
    }
    throw new Error(errMessage);
  }

  return response.json() as Promise<T>;
}

export async function postJson<T>(path: string, body: any): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Correlation-ID': `web-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`,
    },
    body: JSON.stringify(body),
    cache: 'no-store',
  });

  if (!response.ok) {
    let errMessage = `Request failed: ${response.status}`;
    try {
      const errData = await response.json();
      if (errData && errData.message) {
        errMessage = errData.message;
      }
    } catch {
      // ignore
    }
    throw new Error(errMessage);
  }

  return response.json() as Promise<T>;
}

export async function patchJson<T>(path: string, body: any): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'X-Correlation-ID': `web-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`,
    },
    body: JSON.stringify(body),
    cache: 'no-store',
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}
