// Mirrors the backend Pydantic models (cpc_classifier.models).

export interface CpcClass {
  symbol: string;
  title: string;
}

export interface RetrievedClass {
  cpc_class: CpcClass;
  score: number;
}

export interface CpcCandidate {
  symbol: string;
  title: string;
  confidence: number;
  evidence_span: string;
}

export interface ClassificationResult {
  invention: string;
  candidates: CpcCandidate[];
  abstained: boolean;
  retrieved: RetrievedClass[];
  disclaimer: string;
}

export interface Sample {
  label: string;
  text: string;
  tag: string | null;
}

export interface SamplesResponse {
  samples: Sample[];
  disclaimer: string;
}
