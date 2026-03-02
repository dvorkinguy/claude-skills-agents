# Environment Variables Guide

## CMS App (apps/cms)

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URI` | PostgreSQL connection string | `postgresql://user:pass@host/db?sslmode=require` |
| `PAYLOAD_SECRET` | Secret for JWT token generation | `any-random-string-32-chars-min` |

### Preview Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PREVIEW_SECRET` | Secret for preview URL validation | `my-preview-secret` |
| `NEXT_PUBLIC_VERCEL_ENV` | Vercel environment (auto-set) | `production`, `preview`, `development` |

### Optional S3 Storage

| Variable | Description | Example |
|----------|-------------|---------|
| `S3_BUCKET` | S3 bucket name (enables S3 storage) | `export-arena-media` |
| `S3_ACCESS_KEY_ID` | AWS/S3 access key | `AKIA...` |
| `S3_SECRET_ACCESS_KEY` | AWS/S3 secret key | `secret...` |
| `S3_REGION` | S3 region | `eu-central-1` |
| `S3_ENDPOINT` | S3 endpoint (for non-AWS) | `https://s3.eu-central-1.amazonaws.com` |

### Example .env File

```bash
# apps/cms/.env

# Database (Required)
DATABASE_URI=postgresql://neondb_owner:password@ep-xxx.eu-central-1.aws.neon.tech/neondb?sslmode=require

# Payload (Required)
PAYLOAD_SECRET=your-super-secret-key-at-least-32-characters

# Preview
PREVIEW_SECRET=my-preview-secret-123

# S3 Storage (Optional)
# Uncomment to enable S3 media storage
# S3_BUCKET=export-arena-media
# S3_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
# S3_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
# S3_REGION=eu-central-1
# S3_ENDPOINT=https://s3.eu-central-1.amazonaws.com
```

---

## WWW App (apps/www)

### CMS Connection

| Variable | Description | Example |
|----------|-------------|---------|
| `CMS_SITE_ORIGIN` | CMS API URL | `http://localhost:3030` (dev), `https://cms.exportarena.com` (prod) |
| `CMS_API_KEY` | API key for authenticated requests | `bearer-token-xxx` |

### Preview Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `CMS_PREVIEW_SECRET` | Must match CMS `PREVIEW_SECRET` | `my-preview-secret` |

### Revalidation

| Variable | Description | Example |
|----------|-------------|---------|
| `REVALIDATE_SECRET` | Secret for manual revalidation API | `revalidate-secret-123` |

### Example .env.local File

```bash
# apps/www/.env.local

# CMS Connection
CMS_SITE_ORIGIN=http://localhost:3030
CMS_API_KEY=your-api-key

# Preview (Must match CMS PREVIEW_SECRET)
CMS_PREVIEW_SECRET=my-preview-secret-123

# Revalidation
REVALIDATE_SECRET=revalidate-secret-123
```

---

## Environment-Specific Configuration

### Local Development

```bash
# apps/cms/.env
DATABASE_URI=postgresql://localhost:5432/exportarena_cms
PAYLOAD_SECRET=dev-secret-key-for-local-development
PREVIEW_SECRET=local-preview-secret

# apps/www/.env.local
CMS_SITE_ORIGIN=http://localhost:3030
CMS_PREVIEW_SECRET=local-preview-secret
```

### Vercel Preview

Vercel automatically sets:
- `NEXT_PUBLIC_VERCEL_ENV=preview`
- `NEXT_PUBLIC_VERCEL_BRANCH_URL=project-git-branch-xxx.vercel.app`

CMS and WWW URLs are computed from branch URL:
```typescript
// CMS URL for preview branches
const CMS_SITE_ORIGIN = `https://${VERCEL_BRANCH_URL.replace('zone-www-dot-com-git-', 'cms-git-')}`
```

### Production

```bash
# apps/cms (Vercel env vars)
DATABASE_URI=postgresql://neondb_owner:xxx@ep-xxx.neon.tech/neondb?sslmode=require
PAYLOAD_SECRET=production-super-secret-key
PREVIEW_SECRET=production-preview-secret
S3_BUCKET=export-arena-media-prod
S3_ACCESS_KEY_ID=AKIA...
S3_SECRET_ACCESS_KEY=...
S3_REGION=eu-central-1

# apps/www (Vercel env vars)
CMS_SITE_ORIGIN=https://cms.exportarena.com
CMS_PREVIEW_SECRET=production-preview-secret
REVALIDATE_SECRET=production-revalidate-secret
```

---

## Secret Alignment

**CRITICAL:** These secrets must match between apps:

| CMS Variable | WWW Variable | Purpose |
|--------------|--------------|---------|
| `PREVIEW_SECRET` | `CMS_PREVIEW_SECRET` | Preview URL validation |

If these don't match:
- Preview will return 401 Unauthorized
- Draft content won't be accessible

### Verify Alignment

```bash
# Check CMS secret
grep PREVIEW_SECRET apps/cms/.env

# Check WWW secret
grep CMS_PREVIEW_SECRET apps/www/.env.local

# These values should be identical
```

---

## Generating Secrets

### Using OpenSSL

```bash
# Generate 32-character random string
openssl rand -base64 32
```

### Using Node.js

```javascript
require('crypto').randomBytes(32).toString('hex')
```

### Recommended Secret Length

| Secret | Minimum Length |
|--------|----------------|
| `PAYLOAD_SECRET` | 32 characters |
| `PREVIEW_SECRET` | 16 characters |
| `REVALIDATE_SECRET` | 16 characters |
| `CMS_API_KEY` | 32 characters |

---

## Troubleshooting

### CMS Won't Start

1. Check `DATABASE_URI` is correct
2. Check `PAYLOAD_SECRET` is set
3. Test database connection:
   ```bash
   psql $DATABASE_URI -c "SELECT 1"
   ```

### Preview Returns 401

1. Check `PREVIEW_SECRET` in CMS .env
2. Check `CMS_PREVIEW_SECRET` in WWW .env.local
3. Values must be identical

### S3 Upload Fails

1. Check all S3_* variables are set
2. Verify bucket exists and permissions are correct
3. Test with AWS CLI:
   ```bash
   aws s3 ls s3://$S3_BUCKET
   ```

### Content Not Updating

1. Check `CMS_SITE_ORIGIN` points to correct CMS
2. Verify CMS is running and accessible:
   ```bash
   curl $CMS_SITE_ORIGIN/api/pages
   ```
3. Check ISR revalidation is working

---

## Security Best Practices

1. **Never commit .env files** - Add to .gitignore
2. **Use different secrets per environment** - Dev, staging, production
3. **Rotate secrets periodically** - Especially after team changes
4. **Use Vercel environment variables** - Not .env files in production
5. **Limit API key permissions** - Use scoped keys when possible
