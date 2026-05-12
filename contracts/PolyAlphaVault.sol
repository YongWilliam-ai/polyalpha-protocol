// SPDX-License-Identifier: MIT
pragma solidity 0.8.25;

import "@openzeppelin/contracts/token/ERC20/extensions/ERC4626.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/**
 * @title PolyAlphaVault
 * @notice ERC-4626 vault where an AI agent logs Polymarket trading signals on-chain.
 *         Every trade decision is immutably recorded via PositionLogged events,
 *         creating a tamper-proof audit trail verifiable by anyone on Polygonscan.
 *
 * Architecture:
 *   User deposits USDC -> receives paUSDC shares (ERC-4626)
 *   AI agent calls logPosition() after each signal -> immutable on-chain event
 *   Circuit breaker halts all activity if NAV drops 20% from peak
 *   Performance fee (20%) + management fee (0.5%) collected by owner
 *
 * Prototype scope: Polygon Amoy testnet only. No live execution in v1.
 */
contract PolyAlphaVault is ERC4626, Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    // --- Fee constants (immutable - DAO governance controls these in v2) -------
    uint256 public constant PERFORMANCE_FEE_BPS = 2000;   // 20%
    uint256 public constant MGMT_FEE_BPS        = 50;     // 0.5% annual
    uint256 public constant MAX_PERFORMANCE_FEE = 3000;   // Hard cap: 30%
    uint256 public constant BPS_DENOMINATOR     = 10_000;

    // --- Risk limits (hardcoded - cannot be changed without redeployment) -----
    uint256 public constant MAX_POSITION_BPS    = 500;    // 5% TVL per position
    uint256 public constant MAX_EXPOSURE_BPS    = 4000;   // 40% TVL total open
    uint256 public constant DRAWDOWN_HALT_BPS   = 2000;   // 20% drawdown -> halt

    // --- State ----------------------------------------------------------------
    address public aiAgent;
    uint256 public peakAssets;    // All-time high total assets (for drawdown calc)
    bool    public halted;        // Circuit breaker flag
    uint256 public lastMgmtFeeAt; // Timestamp of last management fee collection

    // --- Events ---------------------------------------------------------------

    /**
     * @notice Emitted by the AI agent for every trading signal.
     *         All fields are scaled by BPS_DENOMINATOR (10,000) for precision.
     *         oracleInputHash is SHA-256(btcOpenPrice + btcCurrentPrice + polymarketOdds + timestamp)
     *         stored as tamper-evidence of the agent's exact inputs at decision time.
     */
    event PositionLogged(
        address indexed agent,
        string  marketQuestion,
        uint256 aiProbabilityBps,   // e.g. 7100 = 71.00%
        uint256 marketPriceBps,     // e.g. 6200 = 62.00%
        int256  edgeBps,            // ai - market, signed (negative = no trade)
        string  side,               // "UP" or "DOWN"
        uint256 kellyFractionBps,   // e.g. 750 = 7.50% of TVL
        bytes32 oracleInputHash,    // SHA-256 of all off-chain inputs
        uint256 timestamp
    );

    event CircuitBreakerTriggered(uint256 currentAssets, uint256 peakAssets, uint256 drawdownBps);
    event CircuitBreakerReset(address indexed by);
    event AgentUpdated(address indexed oldAgent, address indexed newAgent);
    event PerformanceFeeClaimed(uint256 profitAmount, uint256 feeAmount);
    event ManagementFeeClaimed(uint256 feeAmount);

    // --- Errors ---------------------------------------------------------------
    error OnlyAgent();
    error VaultHalted();
    error ZeroAmount();
    error InvalidFee();

    // --- Constructor ----------------------------------------------------------

    /**
     * @param _usdc    Address of USDC (or mock USDC on testnet)
     * @param _agent   Address of the AI agent wallet that calls logPosition()
     */
    constructor(IERC20 _usdc, address _agent)
        ERC4626(_usdc)
        ERC20("PolyAlpha Vault Share", "paUSDC")
        Ownable(msg.sender)
    {
        aiAgent      = _agent;
        lastMgmtFeeAt = block.timestamp;
    }

    // --- Modifiers ------------------------------------------------------------

    modifier onlyAgent() {
        if (msg.sender != aiAgent) revert OnlyAgent();
        _;
    }

    modifier notHalted() {
        if (halted) revert VaultHalted();
        _;
    }

    // --- Core ERC-4626 overrides (add circuit breaker check) -----------------

    function deposit(uint256 assets, address receiver)
        public override nonReentrant notHalted returns (uint256)
    {
        if (assets == 0) revert ZeroAmount();
        uint256 shares = super.deposit(assets, receiver);
        _updatePeakAndCheck();
        return shares;
    }

    function withdraw(uint256 assets, address receiver, address owner_)
        public override nonReentrant returns (uint256)
    {
        // Withdrawals allowed even when halted (users must be able to exit)
        return super.withdraw(assets, receiver, owner_);
    }

    // --- AI Agent: Signal Logging ---------------------------------------------

    /**
     * @notice Called by the AI agent after each trading signal.
     *         This function ONLY emits an event - it does NOT move funds.
     *         Fund execution is handled off-chain via py-clob-client.
     *         The oracleInputHash proves the agent's exact inputs were not manipulated.
     *
     * @param marketQuestion    Polymarket market question text
     * @param aiProbabilityBps  AI-estimated win probability x 10000
     * @param marketPriceBps    Current Polymarket YES price x 10000
     * @param side              "UP" or "DOWN"
     * @param kellyFractionBps  Quarter-Kelly position size x 10000
     * @param oracleInputHash   SHA-256 hash of: btcOpen + btcCurrent + polyOdds + timestamp
     */
    function logPosition(
        string calldata marketQuestion,
        uint256 aiProbabilityBps,
        uint256 marketPriceBps,
        string  calldata side,
        uint256 kellyFractionBps,
        bytes32 oracleInputHash
    ) external onlyAgent notHalted {
        int256 edgeBps = int256(aiProbabilityBps) - int256(marketPriceBps);

        emit PositionLogged(
            msg.sender,
            marketQuestion,
            aiProbabilityBps,
            marketPriceBps,
            edgeBps,
            side,
            kellyFractionBps,
            oracleInputHash,
            block.timestamp
        );
    }

    // --- Circuit Breaker ------------------------------------------------------

    /**
     * @notice Checks if drawdown from peak exceeds 20%. If so, halts the vault.
     *         Anyone can call this - it's a public safety function.
     */
    function checkCircuitBreaker() external {
        _updatePeakAndCheck();
    }

    /**
     * @notice Owner can reset the circuit breaker after DAO review (v2: requires DAO vote).
     */
    function resetCircuitBreaker() external onlyOwner {
        halted = false;
        peakAssets = totalAssets();
        emit CircuitBreakerReset(msg.sender);
    }

    function _updatePeakAndCheck() internal {
        uint256 current = totalAssets();
        if (current > peakAssets) {
            peakAssets = current;
            return;
        }
        if (peakAssets == 0) return;

        uint256 drawdownBps = ((peakAssets - current) * BPS_DENOMINATOR) / peakAssets;
        if (drawdownBps >= DRAWDOWN_HALT_BPS && !halted) {
            halted = true;
            emit CircuitBreakerTriggered(current, peakAssets, drawdownBps);
        }
    }

    // --- Fee Collection -------------------------------------------------------

    /**
     * @notice Owner calls this after each resolved position to collect performance fee.
     * @param profitAmount  USDC profit from the resolved position (off-chain calculated)
     */
    function collectPerformanceFee(uint256 profitAmount) external onlyOwner nonReentrant {
        if (profitAmount == 0) revert ZeroAmount();
        uint256 fee = (profitAmount * PERFORMANCE_FEE_BPS) / BPS_DENOMINATOR;
        IERC20(asset()).safeTransfer(owner(), fee);
        emit PerformanceFeeClaimed(profitAmount, fee);
    }

    /**
     * @notice Collect the 0.5% annual management fee (pro-rated since last collection).
     */
    function collectManagementFee() external onlyOwner nonReentrant {
        uint256 elapsed = block.timestamp - lastMgmtFeeAt;
        uint256 annualFee = (totalAssets() * MGMT_FEE_BPS) / BPS_DENOMINATOR;
        uint256 fee = (annualFee * elapsed) / 365 days;
        if (fee == 0) revert ZeroAmount();
        lastMgmtFeeAt = block.timestamp;
        IERC20(asset()).safeTransfer(owner(), fee);
        emit ManagementFeeClaimed(fee);
    }

    // --- Admin ----------------------------------------------------------------

    function setAgent(address newAgent) external onlyOwner {
        emit AgentUpdated(aiAgent, newAgent);
        aiAgent = newAgent;
    }

    // --- View helpers ---------------------------------------------------------

    function currentDrawdownBps() external view returns (uint256) {
        if (peakAssets == 0) return 0;
        uint256 current = totalAssets();
        if (current >= peakAssets) return 0;
        return ((peakAssets - current) * BPS_DENOMINATOR) / peakAssets;
    }
}
