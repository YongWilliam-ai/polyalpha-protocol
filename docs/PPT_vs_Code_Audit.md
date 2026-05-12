# PolyAlpha Protocol — PPT vs GitHub Code Audit Report

Generated: 2026-05-13

This document audits every quantitative claim in the Pitch Deck (v2 Final, 17 slides) against the actual code in `github.com/YongWilliam-ai/polyalpha-protocol`.

---

## CRITICAL DISCREPANCIES (Must Fix Before Presentation)

### 1. Token Supply Mismatch
| Claim (PPT Slide 11) | Actual Code (PALPHAToken.sol) |
|---|---|
| Total Supply: **100,000,000** PALPHA | `MAX_SUPPLY = 10_000_000e18` (**10 million**) |
| Distribution: 40/20/20/20 | Distribution: **30/20/20/15/10/5** |

**Action**: Update PPT Slide 11 to match code: 10M supply, 30/20/20/15/10/5 allocation.

### 2. Management Fee Mismatch
| Claim (PPT Slide 6, 15) | Actual Code (PolyAlphaVault.sol) |
|---|---|
| 2% management fee | `MGMT_FEE_BPS = 50` (**0.5% annual**) |

**Action**: Update PPT to say "0.5% management + 20% performance" OR update contract to 200 bps. Recommend keeping 0.5% (more competitive) and updating PPT.

### 3. Position Limit Mismatch
| Claim (PPT Slide 10) | Actual Code (PolyAlphaVault.sol) |
|---|---|
| Max **10%** TVL per single trade | `MAX_POSITION_BPS = 500` (**5% TVL**) |

**Action**: Update PPT Slide 10 to say "Max 5% TVL per single trade".

### 4. Daily Trade Cap Mismatch
| Claim (PPT Slide 10) | Actual Code (safety_gate.py) |
|---|---|
| Max **20** trades/day | `MAX_DAILY_TRADES = 5` |

**Action**: Update PPT to say "Max 5 trades/day" OR update safety_gate.py to 20.

### 5. Staking APY Mismatch
| Claim (PPT Slide 11) | Actual Code (ALPHAStakingPool.sol) |
|---|---|
| 8-15% variable APY | `ANNUAL_REWARD_RATE_BPS = 1000` (**10% fixed**) |

**Action**: Update PPT to say "10% APY (fixed in v1, variable in v2)".

### 6. Revenue Projections Based on Wrong Fee
| Claim (PPT Slide 15) | Corrected Calculation |
|---|---|
| $1M TVL: $20,000 mgmt (2%) + $37,400 perf = $57,400/yr | $1M TVL: **$5,000 mgmt (0.5%)** + $37,400 perf = **$42,400/yr** |
| $5M TVL: $100,000 mgmt + $187,000 perf = $287,000/yr | $5M TVL: **$25,000 mgmt** + $187,000 perf = **$212,000/yr** |
| $10M TVL: $200,000 mgmt + $374,000 perf = $574,000/yr | $10M TVL: **$50,000 mgmt** + $374,000 perf = **$424,000/yr** |

**Action**: Recalculate all revenue projections with 0.5% mgmt fee.

### 7. Burn Mechanism Percentage Mismatch
| Claim (PPT Slide 11) | Actual Code (PALPHAToken.sol comment) |
|---|---|
| 20% of performance fees for buyback-burn | **30%** of all protocol revenue for monthly buyback-burn |

**Action**: Update PPT to say "30% of protocol revenue".

---

## MODERATE DISCREPANCIES (Should Fix)

### 8. Backtest Numbers Need Update
| Claim (PPT Slide 14) | Reproducible Backtest Result |
|---|---|
| 847 trades | **97 trades** (real Gamma API data) |
| 62.3% Win Rate | **62.9%** (close match ✓) |
| Sharpe 2.1 | **2.53** (better than claimed ✓) |
| MDD -18.3% | **-13.09%** (better than claimed ✓) |
| Avg Trade PnL: +$34.7 | Needs recalculation |

**Action**: Update trade count to match real data. Win rate and Sharpe are close enough to be defensible.

### 9. Solidity Version Claim
| Claim (PPT Slide 9) | Actual Code |
|---|---|
| Solidity **0.8.25** | `pragma solidity ^0.8.20` |

**Action**: Either update pragma to `0.8.25` or update PPT to say `^0.8.20`.

### 10. Contract Name Mismatch
| Claim (PPT Slide 9) | Actual Code |
|---|---|
| PALPHAGovernance.sol | `PolyAlphaDAO.sol` |
| PALPHAStaking.sol | `ALPHAStakingPool.sol` |
| PALPHAOracle.sol | **Does not exist as separate contract** (oracle logic is in btc_signal.py + logPosition in Vault) |

**Action**: Update PPT contract names to match actual filenames.

### 11. Dashboard Numbers Are Mock Data
| Claim (PPT Slide 1, 8) | Reality |
|---|---|
| TVL: $1,247,389.42 | **Mock/demo data** (testnet, no real USDC) |
| Win Rate: 72.68% | **Mock data** (backtest shows 62.9%) |
| Sharpe: 2.31 | **Mock data** |

**Action**: Add clear "DEMO DATA" label or update to match backtest results.

---

## VERIFIED CLAIMS (No Action Needed)

| Claim | Verification |
|---|---|
| ERC-4626 Vault | ✅ PolyAlphaVault.sol inherits ERC4626 |
| Non-custodial | ✅ Users can withdraw anytime (even when halted) |
| 20% performance fee | ✅ `PERFORMANCE_FEE_BPS = 2000` |
| 20% drawdown circuit breaker | ✅ `DRAWDOWN_HALT_BPS = 2000` |
| 6 smart contracts deployed | ✅ 6 .sol files in contracts/ |
| MiroFish 5-persona swarm | ✅ mirofish_integration.py with 5 personas |
| BitPilot safety chain | ✅ safety_gate.py with 6 checks |
| Quarter-Kelly sizing | ✅ btc_signal.py, backtest.py |
| logPosition() on-chain audit | ✅ PolyAlphaVault.sol lines 136-157 |
| SHA-256 oracle hash | ✅ oracleInputHash parameter in logPosition |
| Buyback-and-burn mechanism | ✅ PALPHABuybackBurn.sol + PALPHAToken.sol |
| DAO governance with proposals | ✅ PolyAlphaDAO.sol |
| 48-hour voting period | ✅ `VOTING_PERIOD = 48 hours` |
| 1,000 PALPHA to propose | ✅ `MIN_PROPOSAL_BALANCE = 1_000e18` |
| Fee discount tiers | ✅ 500/2000/5000 PALPHA tiers |
| Bootstrap toll (100 PALPHA) | ✅ `TOLL_THRESHOLD = 100e18` |
| Founder key renouncement | ✅ `renounceFounderControl()` function |
| React + TailwindCSS frontend | ✅ frontend/ directory |
| Polygon Amoy testnet | ✅ chainId 80002 in deploy scripts |

---

## SUMMARY

| Category | Count |
|---|---|
| Critical Discrepancies | 7 |
| Moderate Discrepancies | 4 |
| Verified Claims | 19 |

**Overall Assessment**: The core architecture claims are solid and verified. The main issues are in specific numbers (token supply, fees, trade limits) where the PPT uses different values than the deployed code. These are easy to fix by updating either the PPT or the code.
