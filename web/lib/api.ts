import type { ClassificationResult, SamplesResponse } from "./types";

const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/+$/, "");

export async function getSamples(): Promise<SamplesResponse> {
  const res = await fetch(`${API_URL}/api/samples`);
  if (!res.ok) throw new Error(`Could not load samples (${res.status})`);
  return res.json();
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
