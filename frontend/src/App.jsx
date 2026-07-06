import { useState } from "react";
import ShortenForm from "./components/ShortenForm";
import LinkList from "./components/LinkList";
import AnalyticsPanel from "./components/AnalyticsPanel";

export default function App() {
  const [links, setLinks] = useState([]);
  const [selectedCode, setSelectedCode] = useState(null);

  function handleShortened(newLink) {
    setLinks((previous) => [newLink, ...previous]);
    setSelectedCode(newLink.short_code);
  }

  return (
    <div className="app">
      <header>
        <h1>URL Shortener &amp; Analytics</h1>
        <p className="subtitle">Shorten links and track every click in real time.</p>
      </header>

      <ShortenForm onShortened={handleShortened} />

      <main className="main-grid">
        <section>
          <h2>Your links</h2>
          <LinkList links={links} onSelect={setSelectedCode} selectedCode={selectedCode} />
        </section>

        <section>
          <h2>Analytics</h2>
          <AnalyticsPanel shortCode={selectedCode} />
        </section>
      </main>
    </div>
  );
}
