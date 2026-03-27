# IdeaValidator Frontend

A modern React + Vite + Tailwind CSS application for validating startup ideas using AI agents.

## Features

- 🎨 Clean, custom-built UI components (no component libraries)
- 📊 Real-time progress tracking with animated agent steps
- 📈 Interactive charts and comparisons with Recharts
- 💾 Local storage for past validation results
- 🎯 Responsive design with Tailwind CSS
- ⚡️ Fast development with Vite HMR

## Components

- **App.jsx** - Main layout with sidebar and routing
- **IdeaInput.jsx** - Text area for idea submission
- **AgentProgress.jsx** - Real-time agent progress tracker (polls backend every 1.5s)
- **ResultCard.jsx** - Comprehensive result display with expandable sections
- **ComparisonView.jsx** - Side-by-side idea comparison with bar and radar charts

## Getting Started

### Prerequisites
- Node.js 16+
- Backend running at `http://localhost:8000`

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
npm run preview
```

## API Endpoints Used

- `POST /validate-idea` - Submit an idea for validation
- `GET /validation-status/{validation_id}` - Poll validation progress

## Project Structure

```
frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── IdeaInput.jsx
│   │   ├── AgentProgress.jsx
│   │   ├── ResultCard.jsx
│   │   └── ComparisonView.jsx
│   ├── App.jsx
│   ├── main.jsx
│   ├── App.css
│   └── index.css
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

## Libraries Used

- **React** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Recharts** - Charts and visualizations

