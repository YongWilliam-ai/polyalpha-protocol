// SPDX-License-Identifier: MIT
pragma solidity 0.8.25;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title PALPHABuybackBurn
 * @notice Accepts PALPHA tokens bought back off-chain and burns them on-chain.
 *
 * Flow (monthly, called by DAO treasury):
 *   1. DAO buys PALPHA on QuickSwap using protocol USDC revenue (off-chain).
 *   2. DAO transfers bought PALPHA to this contract via depositForBurn().
 *   3. Owner (DAO in Phase 3) calls executeBurn(usdcSpent) to burn all queued PALPHA.
 *   4. BuybackExecuted event is permanently logged -- verifiable on Polygonscan.
 *
 * Separation of concerns:
 *   - This contract does NOT handle USDC (no DEX integration in v1).
 *   - The usdcSpent parameter is for transparency / accounting only.
 *   - Any address can depositForBurn(); only owner can trigger the actual burn.
 *
 * Phase 2 upgrade: replace owner check with DAO timelock vote.
 */
contract PALPHABuybackBurn is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    ERC20Burnable public immutable palpha;

    uint256 public totalAlphaBurned; // cumulative PALPHA burned by this contract

    // --- Events ------------------------------------------------------------------

    event DepositedForBurn(address indexed depositor, uint256 amount);
    event BuybackExecuted(
        uint256 usdcSpent,   // USDC (6 decimals) spent on buyback -- for transparency
        uint256 alphaBurned, // PALPHA tokens burned
        uint256 timestamp
    );

    // --- Errors ------------------------------------------------------------------

    error ZeroAmount();
    error NothingToBurn();

    // --- Constructor -------------------------------------------------------------

    constructor(address _palpha) Ownable(msg.sender) {
        palpha = ERC20Burnable(_palpha);
    }

    // --- Deposit -----------------------------------------------------------------

    /**
     * @notice Deposit PALPHA to queue it for the next burn.
     *         Callable by anyone -- DAO treasury routes buyback proceeds here.
     *         Tokens are held until executeBurn() is called.
     */
    function depositForBurn(uint256 amount) external {
        if (amount == 0) revert ZeroAmount();
        IERC20(address(palpha)).safeTransferFrom(msg.sender, address(this), amount);
        emit DepositedForBurn(msg.sender, amount);
    }

    // --- Burn --------------------------------------------------------------------

    /**
     * @notice Burns all PALPHA currently held by this contract.
     *         Only callable by the owner (DAO treasury in Phase 3).
     *
     * @param usdcSpent  USDC (6-decimal units) spent on the off-chain buyback.
     *                   Logged in BuybackExecuted for Polygonscan transparency.
     *                   No USDC is transferred or held here.
     */
    function executeBurn(uint256 usdcSpent) external onlyOwner nonReentrant {
        uint256 balance = IERC20(address(palpha)).balanceOf(address(this));
        if (balance == 0) revert NothingToBurn();

        totalAlphaBurned += balance;

        // ERC20Burnable.burn() burns from msg.sender -- this contract holds the tokens
        palpha.burn(balance);

        emit BuybackExecuted(usdcSpent, balance, block.timestamp);
    }

    // --- Views -------------------------------------------------------------------

    /**
     * @notice How much PALPHA is queued for the next executeBurn() call.
     */
    function pendingBurn() external view returns (uint256) {
        return IERC20(address(palpha)).balanceOf(address(this));
    }
}
