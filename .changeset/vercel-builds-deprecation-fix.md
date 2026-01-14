# Vercel Configuration Modernization

## Summary

Removed deprecated `builds` field from Vercel configuration to resolve deployment warnings and align with modern Vercel best practices for monorepo deployments.

## Problem

The root `vercel.json` file was using the legacy `builds` configuration:
```json
{
  "builds": [
    {
      "src": "web/package.json",
      "use": "@vercel/next"
    }
  ],
  "routes": [...]
}
```

This caused Vercel to display a warning during deployment:
> "WARNING! Due to builds existing in your configuration file, the Build and Development Settings defined in your Project Settings will not apply."

## Solution

1. **Removed** the root `vercel.json` file entirely
2. **Kept** the `web/vercel.json` with modern framework detection:
   ```json
   {
     "$schema": "https://openapi.vercel.sh/vercel.json",
     "framework": "nextjs"
   }
   ```

## Migration Required

Users deploying this project to Vercel need to ensure the **Root Directory** is set to `web` in their Vercel project settings:

1. Go to Vercel Dashboard → Your Project
2. Navigate to Settings → General
3. Set **Root Directory** to `web`
4. Save changes

Alternatively, when using Vercel CLI (as in the CI/CD workflow), run commands from the `web/` directory with `working-directory: ./web`.

## Why This Works

- Modern Vercel automatically detects Next.js apps when `framework: "nextjs"` is specified
- The CI/CD workflow (`.github/workflow/vercel-deploy.yml`) already runs all Vercel commands from the `web/` directory
- This approach aligns with Vercel's recommended monorepo practices as of 2024

## Files Changed

- **Removed:** `vercel.json` (root level)
- **Updated:** `README_DEPLOY.md` - Updated configuration documentation
- **Updated:** `docs/VERCEL_SETUP.md` - Added Root Directory setup instructions

## References

- [Vercel Monorepo Documentation](https://vercel.com/docs/monorepos)
- [Vercel Configuration with vercel.json](https://vercel.com/docs/project-configuration/vercel-json)
- [Migration from Legacy Builds](https://vercel.com/docs/builds/configure-a-build)
