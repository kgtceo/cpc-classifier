# Deploy

Backend (FastAPI) → **Railway**; frontend (Next.js in `web/`) → **Vercel**. Push to GitHub first.

## Backend → Railway
1. New Project → Deploy from GitHub repo → `cpc-classifier`. Uses the `Dockerfile`.
2. **Variables:** `ANTHROPIC_API_KEY`, `VOYAGE_API_KEY` (+ `CP_CORS_ORIGINS` = your custom domain if attached).
3. Settings → **Networking → Generate Domain**. Set the domain's target port to the deploy-log port.
4. `GET /health` → `{"status":"ok"}`.

## Frontend → Vercel
1. Import `cpc-classifier`, **Root Directory = `web`**.
2. Env var `NEXT_PUBLIC_API_URL` = the Railway URL.
3. Deploy. Optionally attach `cpc-classifier.kareemghazal.com` and add it to `CP_CORS_ORIGINS`.
