# Salim AI Assistant - Frontend

A beautiful, modern frontend for the Salim AI Assistant - your intelligent multi-purpose assistant for banking, trading, travel, and research.

![Salim AI Assistant](https://img.shields.io/badge/Salim_AI-Assistant-6366f1?style=for-the-badge)

## Features

- 🏦 **Multi-Country Banking** - Manage accounts across Canada, US, and Kenya
- 📈 **Stock Trading** - Portfolio management and real-time quotes
- ✈️ **Travel Booking** - Flight search, hotel booking, price alerts
- ⚖️ **Research** - Legal and business research capabilities
- 🎤 **Voice Input** - Voice command support
- 🌙 **Dark/Light Mode** - Theme switching support

## Quick Demo

### Option 1: Instant Demo (No Installation Required)

Simply open the `demo.html` file in your browser:

```bash
# On Windows, double-click demo.html or run:
start demo.html

# On Mac:
open demo.html

# On Linux:
xdg-open demo.html
```

This standalone HTML file works without any backend - perfect for client demos!

### Option 2: Full React Application

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm start
   ```

3. **Open in browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

## Connecting to Backend

The frontend will automatically connect to the backend API at `http://localhost:8000/api/v1`.

To start the backend:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Project Structure

```
frontend/
├── public/
│   └── index.html          # HTML template
├── src/
│   ├── index.js            # React entry point
│   ├── index.css           # Global styles
│   ├── App.js              # Main React component
│   └── App.css             # Component styles
├── demo.html               # Standalone demo (no build required)
├── package.json            # Dependencies
└── README.md               # This file
```

## Available Modules

### 🤖 General Assistant
- General Q&A
- System information
- Help and guidance

### 🏦 Banking
- Check account balances (Canada 🇨🇦, US 🇺🇸, Kenya 🇰🇪)
- View recent transactions
- Export reports for accountant
- Transfer money

### 📈 Stock Trading
- View portfolio summary
- Get real-time stock quotes
- Track gains and losses
- Execute trades

### ✈️ Travel
- Search flights
- Find and book hotels
- Set price alerts
- View bookings

### ⚖️ Research
- Legal research (Canada & US)
- Case law search
- Business analysis
- Generate reports

## Demo Mode

When the backend is not available, the frontend operates in demo mode with pre-configured sample data:

- Sample account balances across 3 countries
- Mock transaction history
- Demo stock portfolio with AAPL, GOOGL, MSFT, NVDA, TSLA
- Sample flight and hotel search results
- Legal research examples

This makes it perfect for client presentations!

## Customization

### Changing API URL

In `src/App.js`:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
```

Or set environment variable:
```bash
REACT_APP_API_URL=https://your-api.com/api/v1 npm start
```

### Adding New Modules

1. Add module configuration in `MODULES` object
2. Add quick actions in `QUICK_ACTIONS` object
3. Add demo responses in `DEMO_RESPONSES` object

## Tech Stack

- **React 18** - UI Framework
- **Lucide React** - Icons
- **Axios** - HTTP client
- **CSS3** - Styling with modern features

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## License

MIT License - feel free to use for your projects!
