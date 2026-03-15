# Assignment 6 - Clerk Auth + Admin Integration Notes

This document summarizes the current authentication setup for ARCA Platform and explains why the JWKS URL is required.

## Current Status

- Frontend is configured with Clerk publishable key in `arca-platform/frontend/.env`.
- Backend is configured with Clerk JWKS URL in `arca-platform/backend/.env`.
- Login flow is handled by Clerk.
- Frontend sends `Bearer <token>` automatically to backend API calls.
- Admin UI is enabled based on user role metadata.

## JWT Template (Clerk) - Recommended Values

In Clerk Dashboard, create or edit JWT template:

- Name: `ARCA`
- Token lifetime: `60` seconds
- Allowed clock skew: `5` seconds
- Issuer: `https://discrete-insect-70.clerk.accounts.dev`
- JWKS Endpoint: `https://discrete-insect-70.clerk.accounts.dev/.well-known/jwks.json`
- Custom signing key: `Disabled` (recommended unless a third-party requires custom keys)

### Customize Session Token Claims

Use custom claims so backend can perform role-based access checks.

Example claims:

```json
{
  "role": "{{user.public_metadata.role}}",
  "email": "{{user.primary_email_address.email_address}}",
  "name": "{{user.full_name}}"
}
```

Note:

- If your backend reads role from `public_metadata.role`, keep the existing backend logic.
- If you place role as top-level `role`, then backend should read `payload.role`.

## Why We Use JWKS URL

JWKS (JSON Web Key Set) URL is used so backend can validate Clerk-issued JWT signatures securely.

- Clerk signs tokens with private keys.
- Backend verifies signatures using public keys from JWKS endpoint.
- This proves token authenticity and prevents tampering.
- Key rotation is handled automatically by Clerk without changing backend secrets.
- Better security model than sharing private signing secrets with your backend.

In short: **JWKS is required for secure token verification in production.**

## Environment Settings Used

### Frontend

File: `arca-platform/frontend/.env`

```env
VITE_API_URL=http://localhost:5000/api
VITE_CLERK_PUBLISHABLE_KEY=<your_publishable_key>
```

### Backend

File: `arca-platform/backend/.env`

```env
CLERK_JWKS_URL=https://discrete-insect-70.clerk.accounts.dev/.well-known/jwks.json
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Admin Role Setup

To make a user Admin in Clerk:

1. Open Clerk Dashboard -> Users.
2. Select the user.
3. In Public Metadata, set:

```json
{
  "role": "admin"
}
```

4. Save changes and re-login.

## Important Backend Note

Auth decorators (`require_auth` / `require_admin`) exist in backend code, but they must be applied on routes to enforce API-level protection.

Example:

```python
@app.route('/api/admin/summary', methods=['GET'])
@require_admin
def admin_summary():
    ...
```

Without decorators on routes, frontend route protection works, but direct API calls are not fully protected.

## Quick Run Steps

1. Start MongoDB.
2. Run seed data:

```powershell
cd arca-platform
python seed.py
```

3. Start backend:

```powershell
cd arca-platform/backend
python app.py
```

4. Start frontend:

```powershell
cd arca-platform/frontend
npm run dev
```

5. Open the Vite URL shown in terminal.
