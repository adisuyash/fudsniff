## Project Structure

To generate the directory tree, run:

```bash
tree -I "venv|agents|sa_adapter|superior-agents|node_modules|.pnp|frontend/.next|frontend/out|frontend/build|__pycache__|*.py[cod]|*.so|*.db|*.sqlite3|*.log|.DS_Store|*.pem|.vscode|.idea"
```

### Directory Tree:

The directory tree contains 9 directories and 46 files.

```bash
.
├── README.md
├── backend
│   ├── Procfile
│   ├── ai_analyzer.py          # Analyzes news for trading signals
│   ├── app.py                  # Main application file (starting point)
│   ├── list_models.py          # Lists all available Gemini models
│   ├── market_data.py          # Fetches market data from CoinGecko
│   ├── news_fetcher.py         # Fetches news articles
│   ├── prompts.py              # Contains AI prompts
│   ├── requirements.txt
│   ├── runtime.txt
│   ├── telegram_service.py     # Telegram bot service
│   ├── test_bot.py             # Test Telegram bot
│   └── token_detector.py       # Detects tokens in news articles
├── frontend
│   ├── README.md
│   ├── app
│   │   ├── components
│   │   │   ├── FudSniffDashboard.tsx
│   │   │   ├── Navigation.tsx
│   │   │   ├── SignalCard.tsx
│   │   │   ├── Toast.tsx
│   │   │   ├── footer.tsx
│   │   │   └── paws.tsx
│   │   ├── dashboard
│   │   │   └── page.tsx
│   │   ├── favicon.ico
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   ├── lib
│   │   │   └── api.ts
│   │   ├── page.tsx
│   │   └── telegram-signals
│   │       └── page.tsx
│   ├── next-env.d.ts
│   ├── next.config.ts
│   ├── package-lock.json
│   ├── package.json
│   ├── postcss.config.mjs
│   ├── public
│   │   ├── file.svg
│   │   ├── fudsniff-banner.png
│   │   ├── fudsniff.png
│   │   ├── globe.svg
│   │   ├── next.svg
│   │   ├── pawprint.png
│   │   ├── superioragents.png
│   │   ├── vercel.svg
│   │   └── window.svg
│   ├── tsconfig.json
│   └── vercel.json
├── project-structure.txt
├── project_tree.txt
└── setup.sh
```
