# AI Waifu Web Client Setup

## Overview
This is an Angular 19 web client with standalone components for the AI Waifu Cross-Platform System.

## Technologies
- **Angular**: 19.2.18 (with standalone components)
- **TailwindCSS**: 3.x (for styling)
- **TypeScript**: 5.7.3

## Configuration

### Environment Files
- `src/environments/environment.ts` - Development configuration
- `src/environments/environment.prod.ts` - Production configuration

Both files contain the `apiUrl` property pointing to the backend API (default: `http://localhost:8000`).

### TailwindCSS
TailwindCSS is configured via:
- `tailwind.config.js` - Tailwind configuration
- `postcss.config.js` - PostCSS configuration
- `src/styles.css` - Global styles with Tailwind directives

## Development

### Install Dependencies
```bash
npm install
```

### Run Development Server
```bash
npm start
# or
ng serve
```

The application will be available at `http://localhost:4200/`.

### Build for Production
```bash
npm run build
# or
ng build --configuration production
```

## Project Structure
```
web-client/
├── src/
│   ├── app/                    # Application components
│   ├── environments/           # Environment configurations
│   │   ├── environment.ts      # Development config
│   │   └── environment.prod.ts # Production config
│   ├── styles.css              # Global styles with Tailwind
│   └── index.html              # Main HTML file
├── tailwind.config.js          # Tailwind configuration
├── postcss.config.js           # PostCSS configuration
└── angular.json                # Angular CLI configuration
```

## Next Steps
- Implement chat service to communicate with the backend API
- Create chat component for the user interface
- Create affection meter component to display relationship status
- Style the interface with TailwindCSS
