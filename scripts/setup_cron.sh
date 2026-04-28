#!/bin/bash
# setup_cron.sh -- PolyAlpha HKUST Server Setup
# Run this on ugcpu1.cse.ust.hk ONCE to set up the environment.
#
# Usage:
#   ssh wyong@ugcpu1.cse.ust.hk
#   bash setup_cron.sh
#
# After running: fill in ~/project/polyalpha/.env and you're live.

set -e

echo "=== PolyAlpha HKUST Server Setup ==="
echo "Server: $(hostname) | User: $(whoami)"
echo

# 1. Create project directories (~/project/ persists across reboots)
echo "[1/5] Creating project directories..."
mkdir -p ~/project/polyalpha/reports
mkdir -p ~/project/polyalpha/logs
mkdir -p ~/project/polyalpha/agent/logs
echo "  Done: ~/project/polyalpha/{reports,logs,agent/logs}"

# 2. Clone or pull the repo
echo "[2/5] Setting up repo..."
if [ -d ~/project/polyalpha/.git ]; then
    echo "  Repo exists -- pulling latest..."
    cd ~/project/polyalpha && git pull origin main
else
    echo "  Cloning from GitHub..."
    git clone https://github.com/YongWilliam-ai/polyalpha-protocol.git ~/project/polyalpha
    cd ~/project/polyalpha
fi

# 3. Install Python dependencies
echo "[3/5] Installing Python dependencies..."
pip install --user plotly pandas kaleido requests python-telegram-bot pytz python-dotenv 2>/dev/null
echo "  Done (--user install to ~/)"

# 4. Create .env template (user fills in secrets)
echo "[4/5] Creating .env template..."
cat > ~/project/polyalpha/.env.template << 'ENVEOF'
# Fill in your values and rename this file to .env
# NEVER commit .env to GitHub

TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
OKX_API_KEY=your_okx_key_here_optional
OKX_API_SECRET=your_okx_secret_here_optional
POLYMARKET_PRIVATE_KEY=your_key_here_optional
VAULT_CONTRACT_ADDRESS=0x1c275054C7159aBBF446E652A744EFB8cbf6efd0
ENVEOF
echo "  Template: ~/project/polyalpha/.env.template"
echo "  ACTION REQUIRED: cp ~/.../polyalpha/.env.template ~/project/polyalpha/.env && nano ~/.../polyalpha/.env"

# 5. Set up cron job (08:00 HKT = 00:00 UTC)
echo "[5/5] Installing cron job (08:00 HKT daily)..."
CRON_CMD="0 0 * * * cd ~/project/polyalpha/agent && python3 daily_runner.py >> ~/project/polyalpha/logs/daily.log 2>&1"
# Add only if not already present
( crontab -l 2>/dev/null | grep -v "daily_runner.py" ; echo "$CRON_CMD" ) | crontab -
echo "  Cron installed: $CRON_CMD"

echo
echo "=== Setup Complete ==="
echo "Cron job: daily at 08:00 HKT (00:00 UTC)"
echo "Logs:     ~/project/polyalpha/logs/daily.log"
echo "Reports:  ~/project/polyalpha/reports/"
echo
echo "NEXT STEPS:"
echo "  1. cp ~/project/polyalpha/.env.template ~/project/polyalpha/.env"
echo "  2. nano ~/project/polyalpha/.env  (fill in TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)"
echo "  3. Test manually: cd ~/project/polyalpha/agent && python3 daily_runner.py --dry-run"
echo "  4. Wait for 08:00 HKT and check ~/project/polyalpha/logs/daily.log"
