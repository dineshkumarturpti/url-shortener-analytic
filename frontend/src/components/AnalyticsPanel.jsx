import { useEffect, useState } from "react";
import { getAnalytics } from "../services/api";

export default function AnalyticsPanel({ shortCode }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!shortCode) return;

    let cancelled = false;
    setError(null);
    setData(null);

    getAnalytics(shortCode)
      .then((result) => {
        if (!cancelled) setData(result);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      });

    return () => {
      cancelled = true;
    };
  }, [shortCode]);

  if (!shortCode) {
    return <p className="empty-state">Select a link to see its analytics.</p>;
  }

  if (error) {
    return <p className="error-text">{error}</p>;
  }

  if (!data) {
    return <p>Loading analytics…</p>;
  }

  return (
    <div className="analytics-panel">
      <h3>{data.short_code}</h3>
      <p className="long-url">{data.long_url}</p>
      <p className="total-clicks">{data.total_clicks} total clicks</p>

      <h4>Recent activity</h4>
      {data.recent_clicks.length === 0 ? (
        <p className="empty-state">No clicks yet.</p>
      ) : (
        <ul className="click-list">
          {data.recent_clicks.map((click, index) => (
            <li key={index}>
              <span>{new Date(click.clicked_at).toLocaleString()}</span>
              <span className="referrer">{click.referrer || "direct"}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
