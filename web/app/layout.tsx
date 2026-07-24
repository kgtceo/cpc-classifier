import type { Metadata } from "next";
import "./globals.css";

const url = "https://cpc-classifier.kareemghazal.com";
const title = "cpc-classifier — invention → CPC classes (no hallucinated symbols)";
const description =
  "Suggests CPC (Cooperative Patent Classification) classes for an invention via retrieval over an illustrative subset — the LLM only picks from retrieved candidates (never invents a symbol) and abstains. Eval harness included. Demo; not a substitute for a professional classification search.";

export const metadata: Metadata = {
  metadataBase: new URL(url),
  title,
  description,
  alternates: { canonical: "/" },
  openGraph: {
    type: "website",
    url,
    siteName: "cpc-classifier",
    title,
    description,
    locale: "en_GB",
    images: [{ url: "/og.jpg", width: 1200, height: 630, alt: "cpc-classifier — invention description to CPC classes" }],
  },
  twitter: { card: "summary_large_image", title, description, images: ["/og.jpg"] },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
