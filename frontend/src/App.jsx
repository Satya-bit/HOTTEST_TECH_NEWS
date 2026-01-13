import { useState } from "react";

const DEFAULT_QUERY = "hottest tech news";

function App() {
  const [query, setQuery] = useState(DEFAULT_QUERY);
  const [numResults, setNumResults] = useState(8);
  const [summary, setSummary] = useState("");
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const apiBase = import.meta.env.VITE_API_BASE || "http://localhost:8000";

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    setSummary("");
    setArticles([]);
    try {
      const response = await fetch(`${apiBase}/api/summarize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: query.trim() || DEFAULT_QUERY,
          num_results: numResults,
        }),
      });
      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || "Failed to fetch summary.");
      }
      const data = await response.json();
      setSummary(data.summary || "");
      setArticles(data.articles || []);
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const renderLine = (line) => {
    const parts = line.split(/(\*\*[^*]+\*\*)/g).filter(Boolean);
    return parts.map((part, index) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return <strong key={index}>{part.slice(2, -2)}</strong>;
      }
      return <span key={index}>{part}</span>;
    });
  };

  const summaryLines = summary
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => line.replace(/^[-*]\s+/, ""));

  return (
    <div className="page">
      <header className="hero">
        <p className="eyebrow">Daily Tech Pulse</p>
        <h1>Summarize the hottest tech news in seconds.</h1>
        <p className="subhead">
          Powered by SerpApi for discovery and OpenAI for concise, engineer-friendly
          summaries.
        </p>
      </header>

      <section className="panel">
        <form onSubmit={handleSubmit} className="form">
          <label className="field">
            <span>Topic or query</span>
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="e.g., AI chips, cloud security, open-source"
            />
          </label>

          <label className="field">
            <span>Number of headlines</span>
            <div className="range">
              <input
                type="range"
                min="3"
                max="12"
                value={numResults}
                onChange={(event) => setNumResults(Number(event.target.value))}
              />
              <strong>{numResults}</strong>
            </div>
          </label>

          <button type="submit" disabled={loading}>
            {loading ? "Summarizing..." : "Generate summary"}
          </button>
        </form>

        {error && <div className="error">{error}</div>}

        {summary && (
          <div className="summary">
            <h2>Snapshot</h2>
            <ul>
              {summaryLines.map((line, index) => (
                <li key={`${index}-${line.slice(0, 20)}`}>{renderLine(line)}</li>
              ))}
            </ul>
          </div>
        )}
      </section>

      {articles.length > 0 && (
        <section className="results">
          <h2>Sources</h2>
          <div className="cards">
            {articles.map((article) => (
              <article key={article.link} className="card">
                <div className="card-body">
                  <div className="card-text">
                    <div className="source">
                      {article.icon && (
                        <img
                          src={article.icon}
                          alt=""
                          className="source-icon"
                          loading="lazy"
                        />
                      )}
                      <span>{article.source || "Unknown source"}</span>
                    </div>
                    <h3>{article.title}</h3>
                    <div className="meta">
                      <span>{article.date || "Recently"}</span>
                    </div>
                    <a href={article.link} target="_blank" rel="noreferrer">
                      Read story
                    </a>
                  </div>
                  {(article.thumbnail || article.thumbnail_small) && (
                    <img
                      className="thumb"
                      src={article.thumbnail || article.thumbnail_small}
                      alt=""
                      loading="lazy"
                    />
                  )}
                </div>
              </article>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

export default App;
