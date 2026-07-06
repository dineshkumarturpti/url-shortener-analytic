const API_BASE = "/api";

export async function shortenUrl(longUrl) {
  const response = await fetch(`${API_BASE}/shorten`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ long_url: longUrl }),
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || "Failed to shorten URL");
  }

  return response.json();
}

export async function getAnalytics(shortCode) {
  const response = await fetch(`${API_BASE}/analytics/${shortCode}`);

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || "Failed to fetch analytics");
  }

  return response.json();
}
