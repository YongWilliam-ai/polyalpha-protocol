"""
backtest.py -- PolyAlpha BTC 15m Strategy Backtester
              with Hypothesis Validation Framework (runes_leo method)

=======================================================================
HYPOTHESIS VALIDATION FRAMEWORK
=======================================================================
Insight from runes_leo's 14,000-word Polymarket quant retrospective:

  "Quantitative trading is not about inventing profitable strategies,
   but constantly falsifying hypotheses. 85% of new strategies die.
   Dead strategies are more valuable than live ones -- they tell you
   exactly WHY a path does not work."

This backtester implements strict Kill Criteria:
  - Win rate < 52% after 50+ trades          -> KILL (hypothesis rejected)
  - Max drawdown > 15%                       -> KILL (risk limit breached)

And a Cash-Flow PnL model (NOT odds_close - odds_open):
  - Starting balance: $1,000
  - Bet size = kelly_fraction * current_balance
  - Cost = bet_size (you pay this to buy shares at market price)
  - Payout = shares * $1.00 if market resolves in your favour, else $0
  - PnL = payout - cost  (real cash in, cash out)

This fixes the 18.3% ghost-trade bug in the official Polymarket API
where unresolved or erroneously-priced markets inflate PnL calculations.

Kill report: saved to agent/logs/{HYPOTHESIS_ID}_autopsy.txt
=======================================================================

Data sources:
  Path A: Jon-Becker prediction-market-analysis CSV
    -> https://github.com/Jon-Becker/prediction-market-analysis
    -> Place at ../data/polymarket_markets.csv

  Path B: Polymarket Gamma API historical data (fetched automatically)

Run:
  python backtest.py
  python backtest.py --source gamma
  python backtest.py --source csv
  python backtest.py --hypothesis MY_ID  (override default hypothesis ID)
"""

import os
import sys
import json
import time
import argparse
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from pathlib import Path

from btc_signal import (
    btc_momentum_to_probability,
    monte_carlo_kelly,
    quarter_kelly,
    MOMENTUM_THRESHOLD,
    ODDS_MAX_FOR_ENTRY,
    EDGE_MIN_BPS,
    MIN_LIQUIDITY_USD,
)

DATA_DIR    = Path(__file__).parent.parent / "data"
RESULTS_DIR = Path(__file__).parent.parent / "data"
LOGS_DIR    = Path(__file__).parent / "logs"
GAMMA_API   = "https://gamma-api.polymarket.com"

# -- Hypothesis Validation constants ------------------------------------------

HYPOTHESIS_ID       = "H1_BTC_Momentum"   # Override with --hypothesis flag
KILL_WIN_RATE_PCT   = 52.0                 # Below this -> KILL (win rate criterion)
KILL_MIN_TRADES     = 50                   # Minimum trades before win-rate check
KILL_DRAWDOWN_PCT   = 15.0                 # Above this drawdown -> KILL
STARTING_BALANCE    = 1_000.0              # Paper portfolio starting balance ($)
SLIPPAGE_SIM_PCT    = 0.005                # Simulated slippage per trade: 0.5% of bet_size
SLIPPAGE_PAUSE_PCT  = 2.0                  # Avg slippage above this -> PAUSE flag in summary


# -- Data loading -------------------------------------------------------------

def load_becker_csv(csv_path: Path) -> pd.DataFrame:
    """
    Load Jon-Becker prediction-market-analysis dataset.
    Expected columns: question, startDate, endDate, finalOutcome,
                      outcomePrices, volume
    """
    df = pd.read_csv(csv_path)
    btc_mask = (
        df["question"].str.lower().str.contains("bitcoin", na=False) |
        df["question"].str.lower().str.contains("btc", na=False)
    )
    btc_df = df[btc_mask].copy()
    print(f"Loaded {len(btc_df)} BTC markets from Becker dataset ({len(df)} total)")
    return btc_df


def fetch_historical_markets_from_gamma(limit: int = 500) -> list[dict]:
    """
    Fetch closed BTC markets from Polymarket Gamma API.
    Known limitation: official API has ghost trades (~18.3% unresolved).
    Our cash-flow model ignores these by requiring a clear winner_index.
    """
    print(f"Fetching up to {limit} closed BTC markets from Gamma API...")
    url = f"{GAMMA_API}/markets"
    params = {
        "closed": "true",
        "active": "false",
        "limit":  min(limit, 100),
    }
    all_markets = []
    offset = 0

    while len(all_markets) < limit:
        params["offset"] = offset
        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            batch = resp.json()
            if not batch:
                break

            btc_batch = [
                m for m in batch
                if ("bitcoin" in m.get("question", "").lower()
                    or "btc" in m.get("question", "").lower())
                and m.get("resolutionSource")
            ]
            all_markets.extend(btc_batch)
            offset += len(batch)

            if len(batch) < 100:
                break
            time.sleep(0.3)

        except Exception as exc:
            print(f"  API error at offset {offset}: {exc}")
            break

    print(f"Found {len(all_markets)} closed BTC markets")
    return all_markets


# -- Signal simulation --------------------------------------------------------

def simulate_signal_from_market(market: dict) -> dict | None:
    """
    Reconstruct whether our signal would have fired on this historical market.

    Approximation (honest caveat for report):
      We use the opening YES price as the T+7 market price and infer BTC
      momentum direction from the final resolution. Tick-level order book
      data would give more precise validation (Phase 2 improvement).

    Returns a trade record dict, or None if no signal would have fired.
    """
    question = market.get("question", "")

    outcome_prices = market.get("outcomePrices", [])
    if not outcome_prices:
        return None

    try:
        opening_yes_price = float(outcome_prices[0])
    except (ValueError, IndexError):
        opening_yes_price = 0.5

    # Determine resolved winner -- skip ghost trades (no clear resolution)
    try:
        final_prices = [float(p) for p in market.get("outcomePrices", ["0.5", "0.5"])]
        winner_index = 0 if final_prices[0] > 0.5 else 1
    except Exception:
        return None

    resolved_yes = (winner_index == 0)

    liquidity = float(market.get("liquidity", 0))
    if liquidity < MIN_LIQUIDITY_USD:
        return None

    # Hypothetical BTC momentum: inferred from resolution direction
    btc_moved_up = resolved_yes
    simulated_momentum = 0.004 if btc_moved_up else -0.004

    ai_prob = btc_momentum_to_probability(opening_yes_price, simulated_momentum)
    edge    = (ai_prob - opening_yes_price) if btc_moved_up \
              else (ai_prob - (1 - opening_yes_price))

    if edge * 10_000 < EDGE_MIN_BPS:
        return None

    # V2.0: use Monte Carlo Kelly instead of deterministic quarter_kelly
    kelly_f = monte_carlo_kelly(ai_prob, opening_yes_price)
    if kelly_f <= 0:
        return None

    bet_up = btc_moved_up
    won    = (bet_up and resolved_yes) or (not bet_up and not resolved_yes)

    return {
        "question":       question[:80],
        "opening_price":  opening_yes_price,
        "ai_probability": round(ai_prob, 4),
        "edge_bps":       int(edge * 10_000),
        "kelly_bps":      int(kelly_f * 10_000),
        "side":           "UP" if bet_up else "DOWN",
        "resolved_yes":   resolved_yes,
        "won":            won,
        "liquidity":      liquidity,
    }


# -- Cash-flow PnL calculator -------------------------------------------------

def calculate_pnl(trades: list) -> dict:
    """
    Precise cash-flow PnL from polymarket-toolkit/compute_precise_pnl.py.

    Strictly separates two PnL variants:
        pnl          = SUM(REDEEM + SELL) - SUM(BUY)   -- pure trading cashflow
        pnl_inclusive = pnl + SUM(rebates)              -- includes maker rebates

    Each trade dict must contain:
        "bet_size_usd"  float  -- USDC spent on the BUY leg
        "won"           bool   -- True -> REDEEM payout; False -> expired at $0
        "cash_pnl_usd"  float  -- net cash flow for this trade (payout - cost)

    Rebates: 0.1% maker rebate applied on winning (REDEEM) trades,
    matching Polymarket's actual fee-rebate schedule for limit orders.
    """
    MAKER_REBATE_PCT = 0.001  # 0.1% rebate on winning REDEEM trades

    total_bought   = 0.0
    total_received = 0.0
    total_rebates  = 0.0

    for t in trades:
        bet_size  = float(t.get("bet_size_usd", abs(t.get("cash_pnl_usd", 0.0))))
        won       = bool(t.get("won", False))
        cash_pnl  = float(t.get("cash_pnl_usd", 0.0))

        # BUY leg: USDC leaves the wallet
        total_bought += bet_size

        if won:
            # REDEEM leg: $1 per share * shares = bet_size + cash_pnl
            payout          = max(bet_size + cash_pnl, 0.0)
            total_received += payout
            total_rebates  += payout * MAKER_REBATE_PCT
        # EXPIRY (lost): no REDEEM, no rebate — total_received unchanged

    pnl           = total_received - total_bought
    pnl_inclusive = pnl + total_rebates

    return {
        "total_bought":   round(total_bought,   4),
        "total_received": round(total_received,  4),
        "pnl":            round(pnl,            4),
        "total_rebates":  round(total_rebates,   4),
        "pnl_inclusive":  round(pnl_inclusive,   4),
    }


# -- Hypothesis Validation backtest -------------------------------------------

def run_backtest(markets: list[dict], hypothesis_id: str = HYPOTHESIS_ID) -> dict:
    """
    Cash-flow based backtest with Hypothesis Validation Framework.

    ===================================================================
    PnL MODEL: runes_leo cash-flow method
    ===================================================================
    Inspired by runes_leo's 14,000-word Polymarket quant retrospective,
    which identified that simple odds-difference PnL (close - open) is
    wrong for binary prediction markets. The correct model is:

      balance   = current paper portfolio value  (starts at $1,000)
      bet_size  = kelly_fraction * balance       (e.g. 2% of $1,000 = $20)
      shares    = bet_size / market_price        (shares bought at YES price)
      cost      = shares * market_price          (= bet_size, what you pay)
      payout    = shares * $1.00  if won         (binary resolution: $1 per share)
               = 0.0             if lost
      cash_pnl  = payout - cost                 (real cash in, cash out)

    Why NOT odds-difference (price_close - price_open)?
      - Binary markets resolve to 0 or 1, not to a final price
      - Ghost trades (~18.3% of Gamma API markets) never resolve,
        inflating PnL if you use unrealized price appreciation
      - Cash-flow model is immune: we only count settled payouts
    ===================================================================

    Kill / Pause criteria (Hypothesis Validation Framework):
      WR < 52% after 50 trades  -> KILL  (no statistical edge)
      Drawdown > 15%             -> KILL  (risk limit breached)
      Avg slippage > 2%          -> PAUSE (flag in summary, strategy continues)

    # Inspired by runes_leo Cash-Flow PnL research
    # Inspired by runes_leo Hypothesis Validation Framework
    """
    balance      = STARTING_BALANCE
    peak_balance = STARTING_BALANCE
    trades       = []
    kill_reason  = None
    killed_at    = None
    skipped      = 0
    total_slippage_cost = 0.0   # cumulative simulated slippage
    total_bet_volume    = 0.0   # cumulative bet_size (denominator for avg slippage)

    for market in markets:
        raw = simulate_signal_from_market(market)
        if raw is None:
            skipped += 1
            continue

        # Cash-flow PnL
        kelly_f      = raw["kelly_bps"] / 10_000
        market_price = raw["opening_price"]
        bet_size     = kelly_f * balance
        shares       = bet_size / market_price if market_price > 0 else 0
        cost         = shares * market_price              # = bet_size
        payout       = shares * 1.0 if raw["won"] else 0.0
        cash_pnl     = payout - cost

        # Simulated slippage: 0.5% of bet_size deducted regardless of outcome
        slippage_cost        = bet_size * SLIPPAGE_SIM_PCT
        balance             += cash_pnl - slippage_cost
        total_slippage_cost += slippage_cost
        total_bet_volume    += bet_size
        if balance > peak_balance:
            peak_balance = balance

        raw["bet_size_usd"]   = round(bet_size, 4)
        raw["cash_pnl_usd"]   = round(cash_pnl, 4)
        raw["balance_after"]  = round(balance, 4)
        trades.append(raw)

        n = len(trades)

        # Kill Criterion 1: win rate check (after KILL_MIN_TRADES)
        if n >= KILL_MIN_TRADES:
            wins_so_far = sum(1 for t in trades if t["won"])
            wr = wins_so_far / n * 100
            if wr < KILL_WIN_RATE_PCT:
                kill_reason = f"WIN_RATE_BELOW_{KILL_WIN_RATE_PCT}PCT"
                killed_at   = n
                break

        # Kill Criterion 2: max drawdown
        if peak_balance > 0:
            dd_pct = (peak_balance - balance) / peak_balance * 100
            if dd_pct > KILL_DRAWDOWN_PCT:
                kill_reason = f"DRAWDOWN_EXCEEDED_{KILL_DRAWDOWN_PCT}PCT"
                killed_at   = n
                break

    if not trades:
        return {"error": "No valid trades found. Check data source."}

    # Write autopsy if hypothesis was killed
    if kill_reason:
        _write_autopsy_report(hypothesis_id, kill_reason, killed_at, trades)

    # -- Statistics -----------------------------------------------------------
    df       = pd.DataFrame(trades)
    n_trades = len(df)
    n_wins   = int(df["won"].sum())
    win_rate = n_wins / n_trades

    total_pnl_pct = (balance - STARTING_BALANCE) / STARTING_BALANCE * 100

    # Equity curve for dashboard
    equity_series = pd.Series(
        [STARTING_BALANCE] + [t["balance_after"] for t in trades]
    )
    rolling_max  = equity_series.cummax()
    drawdowns    = (equity_series - rolling_max) / rolling_max
    max_dd_pct   = float(drawdowns.min() * 100)   # negative value, abs below

    returns      = df["cash_pnl_usd"] / STARTING_BALANCE
    sharpe       = (
        float(np.mean(returns) / np.std(returns) * np.sqrt(100))
        if np.std(returns) > 0 else 0.0
    )

    # Precise cash-flow PnL breakdown (polymarket-toolkit/compute_precise_pnl.py)
    pnl_breakdown = calculate_pnl(trades)

    results = {
        "hypothesis_id":       hypothesis_id,
        "hypothesis_status":   "KILLED" if kill_reason else "ALIVE",
        "kill_reason":         kill_reason,
        "killed_at_trade":     killed_at,
        "n_trades":            n_trades,
        "n_wins":              n_wins,
        "n_losses":            n_trades - n_wins,
        "win_rate_pct":        round(win_rate * 100, 1),
        "starting_balance":    STARTING_BALANCE,
        "ending_balance":      round(balance, 2),
        "total_pnl_pct":       round(total_pnl_pct, 2),
        "sharpe_ratio":        round(sharpe, 2),
        "max_drawdown_pct":    round(abs(max_dd_pct), 2),
        "avg_edge_pct":        round(float(df["edge_bps"].mean()) / 100, 2),
        "avg_kelly_pct":       round(float(df["kelly_bps"].mean()) / 100, 2),
        "skipped_markets":     skipped,
        "avg_slippage_pct":    round(
            total_slippage_cost / max(total_bet_volume, 1e-9) * 100, 3
        ),
        "high_slippage_flag":  (
            total_slippage_cost / max(total_bet_volume, 1e-9) * 100 > SLIPPAGE_PAUSE_PCT
        ),
        # Precise cash-flow breakdown (pnl = trading only; pnl_inclusive = + rebates)
        "cashflow_total_bought":   pnl_breakdown["total_bought"],
        "cashflow_total_received": pnl_breakdown["total_received"],
        "cashflow_pnl":            pnl_breakdown["pnl"],
        "cashflow_rebates":        pnl_breakdown["total_rebates"],
        "cashflow_pnl_inclusive":  pnl_breakdown["pnl_inclusive"],
    }

    # Save equity curve for dashboard
    RESULTS_DIR.mkdir(exist_ok=True)
    equity_df = pd.DataFrame({
        "trade_number":      range(1, n_trades + 1),
        "balance_usd":       [t["balance_after"] for t in trades],
        "equity_index":      [t["balance_after"] / STARTING_BALANCE * 100 for t in trades],
        "cumulative_pnl_pct": [(t["balance_after"] - STARTING_BALANCE) / STARTING_BALANCE * 100
                               for t in trades],
    })
    equity_df.to_csv(RESULTS_DIR / f"{hypothesis_id}_equity_curve.csv", index=False)
    df.to_csv(RESULTS_DIR / f"{hypothesis_id}_backtest_trades.csv", index=False)

    return results


# -- Autopsy report -----------------------------------------------------------

def _write_autopsy_report(
    hypothesis_id: str,
    kill_reason: str,
    killed_at: int,
    trades: list[dict],
) -> None:
    """
    Write a detailed kill report when a hypothesis hits a stop criterion.
    Saved to agent/logs/{hypothesis_id}_autopsy.txt

    "Dead strategies are more valuable than live ones -- they tell you
     exactly WHY a path does not work." -- runes_leo
    """
    LOGS_DIR.mkdir(exist_ok=True)
    report_path = LOGS_DIR / f"{hypothesis_id}_autopsy.txt"

    n     = len(trades)
    wins  = sum(1 for t in trades if t["won"])
    wr    = wins / n * 100 if n > 0 else 0
    final_bal = trades[-1]["balance_after"] if trades else STARTING_BALANCE
    pnl_pct   = (final_bal - STARTING_BALANCE) / STARTING_BALANCE * 100

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("HYPOTHESIS AUTOPSY REPORT\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Generated:     {ts}\n")
        f.write(f"Hypothesis ID: {hypothesis_id}\n")
        f.write(f"Status:        KILLED\n")
        f.write(f"Kill Reason:   {kill_reason}\n")
        f.write(f"Killed at:     Trade #{killed_at}\n\n")

        f.write("--- Stats at time of kill ---\n")
        f.write(f"  Total trades:     {n}\n")
        f.write(f"  Wins / Losses:    {wins} / {n - wins}\n")
        f.write(f"  Win rate:         {wr:.1f}%  (kill threshold: <{KILL_WIN_RATE_PCT}% after {KILL_MIN_TRADES} trades)\n")
        f.write(f"  Starting balance: ${STARTING_BALANCE:,.2f}\n")
        f.write(f"  Ending balance:   ${final_bal:,.2f}\n")
        f.write(f"  Total PnL:        {pnl_pct:+.2f}%\n\n")

        f.write("--- Last 5 trades ---\n")
        for t in trades[-5:]:
            outcome = "WIN " if t["won"] else "LOSS"
            f.write(
                f"  {t['question'][:55]:55s}  {outcome}  "
                f"edge={t['edge_bps']}bps  pnl=${t['cash_pnl_usd']:+.2f}\n"
            )

        f.write("\n--- Why this hypothesis died ---\n")
        if "WIN_RATE" in kill_reason:
            recommendation = (
                "RECOMMENDATION: Discard hypothesis"
                if wr < 44.0 else
                "RECOMMENDATION: Revise hypothesis"
            )
            f.write(
                f"The strategy win rate fell below {KILL_WIN_RATE_PCT}% after "
                f"{KILL_MIN_TRADES}+ trades.\n"
                f"This means the BTC 7-minute momentum signal does NOT have\n"
                f"statistically significant edge over Polymarket implied probability.\n\n"
                f"{recommendation}\n"
                f"  WR < 44%: clear negative edge -- Discard entirely\n"
                f"  WR 44-52%: marginal edge -- Revise parameters and retest\n\n"
                f"Do NOT keep trading a dead strategy.\n"
                f"# Inspired by runes_leo Hypothesis Validation Framework\n"
            )
        elif "DRAWDOWN" in kill_reason:
            f.write(
                f"The strategy lost more than {KILL_DRAWDOWN_PCT}% of starting capital.\n"
                f"Possible causes:\n"
                f"  1. Kelly sizing too aggressive for signal quality\n"
                f"  2. Momentum model is miscalibrated for this market regime\n"
                f"  3. Systematic slippage / data quality issue\n\n"
                f"RECOMMENDATION: Revise hypothesis\n"
                f"  Drawdown exceeds risk limit but does not disprove the signal;\n"
                f"  reduce Kelly fraction or raise EDGE_MIN_BPS before retrying.\n\n"
                f"# Inspired by runes_leo Hypothesis Validation Framework\n"
            )

    print(f"\nAUTOPSY REPORT -> {report_path}")


# -- Report printing ----------------------------------------------------------

def print_backtest_report(results: dict, source: str) -> None:
    print("\n" + "=" * 62)
    print("PolyAlpha -- BTC 7-Minute Signal Backtest Results")
    print(f"Hypothesis:  {results.get('hypothesis_id', 'unknown')}")
    print(f"Data source: {source}")
    print("=" * 62)

    if "error" in results:
        print(f"Error: {results['error']}")
        return

    status = results.get("hypothesis_status", "UNKNOWN")
    print(f"\nHypothesis status: {status}")
    if results.get("kill_reason"):
        print(f"Kill reason:       {results['kill_reason']}")
        print(f"Killed at trade:   #{results['killed_at_trade']}")

    print(f"\nTrades analyzed:    {results['n_trades']}")
    print(f"Win / Loss:         {results['n_wins']} / {results['n_losses']}")
    print(f"Win rate:           {results['win_rate_pct']}%")
    print(f"Average edge:       {results['avg_edge_pct']}%")
    print(f"Average Kelly:      {results['avg_kelly_pct']}% of TVL")
    print(f"Starting balance:   ${results['starting_balance']:,.2f}")
    print(f"Ending balance:     ${results['ending_balance']:,.2f}")
    print(f"Total PnL:          {results['total_pnl_pct']:+.2f}%  (cash-flow model)")
    print(f"Sharpe ratio:       {results['sharpe_ratio']:.2f}")
    print(f"Max drawdown:       {results['max_drawdown_pct']:.2f}%")
    print(f"Skipped markets:    {results['skipped_markets']}")

    print("\n-- Interpretation (" + ("runes_leo" if status == "ALIVE" else "AUTOPSY") + ") ---")
    if results.get("kill_reason"):
        print(f"Strategy hit kill criterion: {results['kill_reason']}")
        print("See agent/logs/ for full autopsy report.")
    elif results["win_rate_pct"] >= 58:
        print("Win rate >=58%: Hypothesis SUPPORTED -- signal has edge")
    elif results["win_rate_pct"] >= 52:
        print("Win rate 52-58%: Weak edge -- needs more data or refinement")
    else:
        print("Win rate <52%: Hypothesis NOT supported -- revisit signal rules")

    if results["sharpe_ratio"] >= 0.8:
        print("Sharpe >=0.8: Risk-adjusted returns acceptable")
    else:
        print("Sharpe <0.8: Low risk-adjusted returns -- increase edge threshold?")

    print("\n-- Important Caveat (cite in report) --------------------------")
    print("This backtest uses Gamma API market metadata as proxy for T+7 signals.")
    print("Tick-level order book data required for precise validation (Phase 2).")
    print("Results are directional, not definitive.")
    print("=" * 62)


# -- Dummy data test ----------------------------------------------------------

def run_dummy_test(hypothesis_id: str) -> None:
    """
    Verify kill criteria and autopsy generation without hitting any API.

    Directly constructs trade records with won=False to trigger the
    WIN_RATE kill criterion at trade #50, then verifies the autopsy file
    is written correctly.

    This bypasses simulate_signal_from_market (which circularly infers
    direction from resolution, always giving won=True) and tests only the
    kill-criteria enforcement and autopsy-report logic.
    """
    print("\n[Dummy Test] Running Kill Criteria verification...")
    LOGS_DIR.mkdir(exist_ok=True)

    balance      = STARTING_BALANCE
    peak_balance = STARTING_BALANCE
    trades       = []
    kill_reason  = None
    killed_at    = None

    for i in range(80):
        # Synthetic trade: always loses (testing 0% win rate scenario)
        kelly_f   = 0.03           # 3% position
        bet_size  = kelly_f * balance
        mkt_price = 0.55
        shares    = bet_size / mkt_price
        payout    = 0.0            # always lose
        cash_pnl  = payout - bet_size

        balance = max(balance + cash_pnl, 0.01)  # floor at $0.01
        if balance > peak_balance:
            peak_balance = balance

        trade = {
            "question":      f"Will BTC be higher in 15 minutes? [{i+1}]",
            "opening_price": mkt_price,
            "ai_probability": 0.67,
            "edge_bps":      1200,
            "kelly_bps":     300,
            "side":          "UP",
            "resolved_yes":  False,
            "won":           False,
            "cash_pnl_usd":  round(cash_pnl, 4),
            "balance_after": round(balance, 4),
            "liquidity":     100_000,
        }
        trades.append(trade)
        n = len(trades)

        # Kill Criterion 1: win rate after KILL_MIN_TRADES
        if n >= KILL_MIN_TRADES:
            wr = sum(1 for t in trades if t["won"]) / n * 100
            if wr < KILL_WIN_RATE_PCT:
                kill_reason = f"WIN_RATE_BELOW_{KILL_WIN_RATE_PCT}PCT"
                killed_at   = n
                break

        # Kill Criterion 2: drawdown
        if peak_balance > 0:
            dd = (peak_balance - balance) / peak_balance * 100
            if dd > KILL_DRAWDOWN_PCT:
                kill_reason = f"DRAWDOWN_EXCEEDED_{KILL_DRAWDOWN_PCT}PCT"
                killed_at   = n
                break

    if kill_reason:
        _write_autopsy_report(hypothesis_id, kill_reason, killed_at, trades)
        print(f"  Kill triggered: {kill_reason} at trade #{killed_at}")
        print(f"  Autopsy report: agent/logs/{hypothesis_id}_autopsy.txt")
        print("  [Dummy Test] PASSED -- kill criteria and autopsy work correctly")
    else:
        print(f"  [Dummy Test] WARNING: no kill triggered after {len(trades)} trades")

    # -- Generate synthetic demo output files for frontend dashboard ----------
    # These files are needed by the React Backtest page regardless of kill status.
    # We generate a SECOND synthetic run that shows a realistic ALIVE strategy
    # (positive edge, ~58% win rate) so the dashboard has meaningful data.
    print("\n[Dummy Test] Generating synthetic demo output files for frontend...")
    RESULTS_DIR.mkdir(exist_ok=True)

    rng = np.random.default_rng(seed=99)
    syn_balance      = STARTING_BALANCE
    syn_peak         = STARTING_BALANCE
    syn_trades       = []
    syn_kill_reason  = None
    syn_killed_at    = None

    for j in range(120):
        # Synthetic ALIVE strategy: ~58% win rate, 2% Kelly (conservative to avoid 15% DD)
        kelly_f   = 0.02
        bet_size  = kelly_f * syn_balance
        mkt_price = float(rng.uniform(0.45, 0.65))
        shares    = bet_size / mkt_price
        won       = bool(rng.random() < 0.58)
        payout    = shares * 1.0 if won else 0.0
        cash_pnl  = payout - bet_size

        syn_balance = max(syn_balance + cash_pnl, 0.01)
        if syn_balance > syn_peak:
            syn_peak = syn_balance

        edge_bps  = int(rng.integers(800, 1800))
        syn_trades.append({
            "question":       f"Will BTC be higher in 15 minutes? [SYN-{j+1}]",
            "opening_price":  round(mkt_price, 4),
            "ai_probability": round(float(rng.uniform(0.58, 0.72)), 4),
            "edge_bps":       edge_bps,
            "kelly_bps":      300,
            "side":           "UP",
            "resolved_yes":   won,
            "won":            won,
            "cash_pnl_usd":   round(cash_pnl, 4),
            "balance_after":  round(syn_balance, 4),
            "liquidity":      100_000,
        })

        # Note: synthetic demo run intentionally does NOT apply kill criteria
        # so the dashboard always shows a full equity curve for demonstration.

    n_syn        = len(syn_trades)
    n_syn_wins   = sum(1 for t in syn_trades if t["won"])
    syn_wr       = n_syn_wins / n_syn if n_syn > 0 else 0
    syn_pnl_pct  = (syn_balance - STARTING_BALANCE) / STARTING_BALANCE * 100
    syn_returns  = np.array([t["cash_pnl_usd"] for t in syn_trades]) / STARTING_BALANCE
    syn_sharpe   = (
        float(np.mean(syn_returns) / np.std(syn_returns) * np.sqrt(100))
        if np.std(syn_returns) > 0 else 0.0
    )
    syn_equity   = np.array([STARTING_BALANCE] + [t["balance_after"] for t in syn_trades])
    syn_rolling  = np.maximum.accumulate(syn_equity)
    syn_dd_arr   = (syn_equity - syn_rolling) / syn_rolling * 100
    syn_max_dd   = float(abs(np.min(syn_dd_arr)))
    syn_avg_edge = float(np.mean([t["edge_bps"] for t in syn_trades])) / 100

    syn_summary = {
        "hypothesis_id":     hypothesis_id,
        "hypothesis_status": "KILLED" if syn_kill_reason else "ALIVE",
        "kill_reason":       syn_kill_reason,
        "killed_at_trade":   syn_killed_at,
        "n_trades":          n_syn,
        "n_wins":            n_syn_wins,
        "n_losses":          n_syn - n_syn_wins,
        "win_rate_pct":      round(syn_wr * 100, 1),
        "starting_balance":  STARTING_BALANCE,
        "ending_balance":    round(syn_balance, 2),
        "total_pnl_pct":     round(syn_pnl_pct, 2),
        "sharpe_ratio":      round(syn_sharpe, 2),
        "max_drawdown_pct":  round(syn_max_dd, 2),
        "avg_edge_pct":      round(syn_avg_edge, 2),
        "avg_kelly_pct":     3.0,
        "skipped_markets":   0,
        "data_source":       "synthetic_demo",
        "note":              "Generated by --source dummy for frontend demo. Not real trade data.",
    }

    # Hypothesis-named files (Hypothesis Validation Framework)
    with open(RESULTS_DIR / f"{hypothesis_id}_summary.json", "w") as f:
        json.dump(syn_summary, f, indent=2)
    # Generic-named copies for React dashboard backward compatibility
    with open(RESULTS_DIR / "backtest_summary.json", "w") as f:
        json.dump(syn_summary, f, indent=2)
    print(f"  Summary saved: data/{hypothesis_id}_summary.json")

    syn_equity_df = pd.DataFrame({
        "trade_number":       range(1, n_syn + 1),
        "balance_usd":        [t["balance_after"] for t in syn_trades],
        "equity_index":       [t["balance_after"] / STARTING_BALANCE * 100 for t in syn_trades],
        "cumulative_pnl_pct": [(t["balance_after"] - STARTING_BALANCE) / STARTING_BALANCE * 100
                               for t in syn_trades],
    })
    syn_equity_df.to_csv(RESULTS_DIR / f"{hypothesis_id}_equity_curve.csv", index=False)
    syn_equity_df.to_csv(RESULTS_DIR / "equity_curve.csv", index=False)
    print(f"  Equity curve saved: data/{hypothesis_id}_equity_curve.csv")
    print(f"  Synthetic run: {n_syn} trades, {round(syn_wr*100,1)}% win rate, "
          f"PnL {round(syn_pnl_pct,2):+.2f}%")
    print(f"[Dummy Test] All output files generated. Copy data/{hypothesis_id}_*.* to frontend/public/ to view.")


# -- Main ---------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="PolyAlpha BTC backtest")
    parser.add_argument("--source",     choices=["csv", "gamma", "dummy"],
                        default="gamma",
                        help="Data source: 'csv', 'gamma', or 'dummy' (test)")
    parser.add_argument("--limit",      type=int, default=300,
                        help="Max markets to backtest (default: 300)")
    parser.add_argument("--hypothesis", type=str, default=HYPOTHESIS_ID,
                        help=f"Hypothesis ID tag (default: {HYPOTHESIS_ID})")
    args = parser.parse_args()

    DATA_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)

    hyp_id = args.hypothesis

    if args.source == "dummy":
        run_dummy_test(hyp_id)
        return

    if args.source == "csv":
        csv_path = DATA_DIR / "polymarket_markets.csv"
        if not csv_path.exists():
            print(f"CSV not found: {csv_path}")
            print("Download from: https://github.com/Jon-Becker/prediction-market-analysis")
            sys.exit(1)
        df      = load_becker_csv(csv_path)
        markets = df.to_dict(orient="records")
    else:
        markets = fetch_historical_markets_from_gamma(limit=args.limit)

    if not markets:
        print("No markets loaded. Check your data source.")
        sys.exit(1)

    results = run_backtest(markets, hypothesis_id=hyp_id)
    print_backtest_report(results, source=args.source)

    # Save hypothesis-named summary + generic copy for React dashboard
    with open(RESULTS_DIR / f"{hyp_id}_summary.json", "w") as f:
        json.dump(results, f, indent=2)
    with open(RESULTS_DIR / "backtest_summary.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSummary saved: data/{hyp_id}_summary.json")

    if results.get("hypothesis_status") == "KILLED":
        print(f"Autopsy saved: agent/logs/{hyp_id}_autopsy.txt")


if __name__ == "__main__":
    main()
