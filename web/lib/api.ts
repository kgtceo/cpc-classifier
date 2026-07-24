import { FALLBACK_SAMPLES } from "./samples";
import type { ClassificationResult, Sample, SamplesResponse } from "./types";

const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/+$/, "");

const FALLBACK_DISCLAIMER =
  "Demo/educational tool using an illustrative CPC subset (not the full scheme). " +
  "Suggestions only — not a substitute for a professional classification search.";

// Never rejects: falls back to the baked-in samples when the API is cold or the
// response isn't the expected shape, so "Load example" always works.
export async function getSamples(): Promise<SamplesResponse> {
  try {
    const res = await fetch(`${API_URL}/api/samples`);
    if (!res.ok) throw new Error(`status ${res.status}`);
    const body = await res.json();
    const ok =
      Array.isArray(body?.samples) &&
      body.samples.length > 0 &&
      body.samples.every((s: Sample) => typeof s?.text === "string" && typeof s?.label === "string");
    if (!ok) throw new Error("unexpected samples shape");
    return body as SamplesResponse;
  } catch {
    return { samples: FALLBACK_SAMPLES, disclaimer: FALLBACK_DISCLAIMER };
  }
}

export async function classify(invention: string): Promise<ClassificationResult> {
  const res = await fetch(`${API_URL}/api/classify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ invention }),
  });
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      /* non-JSON */
    }
    throw new Error(detail);
  }
  return res.json();
}
