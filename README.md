# DrawGames

This repository is now configured as a static React frontend only.

## What changed
- Removed backend deployment from Dockerfile.
- No MongoDB or backend environment variables are required.
- The frontend uses local seed data when no backend URL is provided.

## Build and run locally
1. `cd frontend`
2. `npm install --legacy-peer-deps`
3. `npm run build`
4. `npx serve -s build`

## Deploy
- Use any static hosting provider (Netlify, Vercel, GitHub Pages, etc.)
- No environment variables are needed for this repo.
