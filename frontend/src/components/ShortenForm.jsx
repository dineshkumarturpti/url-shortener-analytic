import { useState } from "react";
import { shortenUrl } from "../services/api";

export default function ShortenForm({ onShortened }) {
  const [longUrl, setLongUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const result = await shortenUrl(longUrl);
      onShortened(result);
      setLongUrl("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="shorten-form" onSubmit={handleSubmit}>
      <input
        type="url"
        required
        placeholder="Paste a long URL to shorten…"
        value={longUrl}
        onChange={(event) => setLongUrl(event.target.value)}
      />
      <button type="submit" disabled={loading}>
        {loading ? "Shortening…" : "Shorten"}
      </button>
      {error && <p className="error-text">{error}</p>}
    </form>
  );
}
