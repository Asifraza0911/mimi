# Angular Web Client Build Configuration

## Overview

This document describes the production build configuration for the AI Waifu web client.

## Build Configurations

### Development Build
```bash
npm start
# or
npm run build -- --configuration development
```

**Features:**
- Source maps enabled for debugging
- No optimization for faster builds
- Development API URL: `http://localhost:8000`

### Production Build
```bash
npm run build:prod
# or
npm run build -- --configuration production
```

**Features:**
- Full optimization enabled
- Source maps disabled
- Output hashing for cache busting
- Named chunks disabled for smaller bundles
- License extraction enabled
- Production API URL: `https://your-production-api.com`

## Environment Configuration

### Development Environment (`src/environments/environment.ts`)
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000'
};
```

### Production Environment (`src/environments/environment.prod.ts`)
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://your-production-api.com' // Replace with actual production API URL
};
```

**Important:** Before deploying to production, update the `apiUrl` in `environment.prod.ts` with your actual backend API URL.

## Build Optimizations

The production build includes the following optimizations:

1. **Code Optimization**: Minification and tree-shaking
2. **Output Hashing**: All files include content hashes for cache invalidation
3. **License Extraction**: Third-party licenses extracted to `3rdpartylicenses.txt`
4. **Bundle Size Limits**:
   - Initial bundle: 500kB warning, 1MB error
   - Component styles: 4kB warning, 8kB error

## Build Output

Production builds are output to `dist/web-client/browser/`:
- `index.html` - Main HTML file
- `main-[hash].js` - Application code
- `polyfills-[hash].js` - Browser polyfills
- `styles-[hash].css` - Compiled styles
- `3rdpartylicenses.txt` - Third-party licenses

## Deployment

1. Build the production bundle:
   ```bash
   npm run build:prod
   ```

2. Update the API URL in `src/environments/environment.prod.ts` before building

3. Deploy the contents of `dist/web-client/browser/` to your web server

4. Configure your web server to:
   - Serve `index.html` for all routes (for Angular routing)
   - Set appropriate cache headers for hashed files
   - Enable gzip/brotli compression

## Testing the Production Build Locally

You can test the production build locally using a simple HTTP server:

```bash
# Install http-server globally (if not already installed)
npm install -g http-server

# Serve the production build
cd dist/web-client/browser
http-server -p 4200
```

Then open `http://localhost:4200` in your browser.

## Troubleshooting

### Build Fails with Bundle Size Errors

If the build fails due to bundle size limits, you can:
1. Analyze the bundle: `npm run build:prod -- --stats-json`
2. Use webpack-bundle-analyzer to identify large dependencies
3. Implement lazy loading for large features
4. Adjust budget limits in `angular.json` if necessary

### API Connection Issues

If the app can't connect to the API:
1. Verify the `apiUrl` in the environment file matches your backend
2. Check CORS configuration on the backend
3. Ensure the backend is running and accessible
