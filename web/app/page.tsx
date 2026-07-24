"use client";

import { useEffect, useState } from "react";
import { classify, getSamples } from "../lib/api";
import type { ClassificationResult } from "../lib/types";

export default function Home() {
  const [invention, setInvention] = useState("");
  const [samples, setSamples] = useState<string[]>([]);
  const [disclaimer, setDisclaimer] = useState("");
  const [result, setResult] = useState<ClassificationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getSamples()
      .then((r) => { setSamples(r.samples); setDisclaimer(r.disclaimer); })
      .catch(() => { /* samples optional */ });
  }, []);

  async function run(text: string) {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      setResult(await classify(text));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <header>
        <h1>cpc-classifier</h1>
        <p>Suggests CPC (Cooperative Patent Classification) classes for an invention &mdash; the model only picks from retrieved candidates, so it can&rsquo;t invent a symbol, and abstains when nothing fits.</p>
      </header>

      <div className="banner">
        ⚠️ Demo / educational. Uses an <strong>illustrative CPC subset</strong> (not the full
        scheme). Suggestions only — not a substitute for a professional classification search.
      </div>

      <label htmlFor="invention">Invention description</label>
      <textarea
        id="invention"
        value={invention}
        placeholder="e.g. A wearable sensor that measures blood glucose and streams readings to a phone."
        onChange={(e) => setInvention(e.target.value)}
      />
      <div className="actions">
        <button onClick={() => run(invention)} disabled={loading}>{loading ? "Classifying…" : "Classify"}</button>
      </div>

      {samples.length > 0 && (
        <div className="examples">
          {samples.map((ex) => (
            <span className="chip" key={ex} onClick={() => { setInvention(ex); run(ex); }}>{ex}</span>
          ))}
        </div>
      )}

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="panel">
          <span className={`badge ${result.abstained ? "abstained" : "coded"}`}>
            {result.abstained ? "No confident match — abstained" : `${result.candidates.length} class(es) suggested`}
          </span>
          {!result.abstained && (
            <table>
              <thead>
                <tr><th>CPC symbol</th><th>Title</th><th>Conf</th><th>Evidence in description</th></tr>
              </thead>
              <tbody>
                {result.candidates.map((c) => (
                  <tr key={c.symbol}>
                    <td className="cid">{c.symbol}</td>
                    <td>{c.title}</td>
                    <td className="conf">{c.confidence.toFixed(2)}</td>
                    <td className="ev">“{c.evidence_span}”</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {disclaimer && <p className="disc">{disclaimer}</p>}
    </div>
  );
}
