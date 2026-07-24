import { API_BASE_URL } from './config';

export async function planTrip(payload) {
  try {
    const response = await fetch(`${API_BASE_URL}/plan-trip/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `Server responded with status ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API error in planTrip:', error);
    throw error;
  }
}
