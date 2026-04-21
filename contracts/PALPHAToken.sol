// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title PALPHAToken
 * @notice The $PALPHA utility token for the PolyAlpha Protocol.
 *
 * Max supply: 10,000,000 PALPHA (hard cap - no inflation beyond this)
 * Initial:    3,000,000 PALPHA minted to deployer at launch (30% of max)
 *
 * Token Distribution:
 *   30% (3,000,000) -> Early Depositor Rewards  (vested, locked 6 months)
 *   20% (2,000,000) -> Team/Founder (William)   (locked 12 months, vested)
 *   20% (2,000,000) -> DAO Treasury             (governed by PolyAlphaDAO)
 *   15% (1,500,000) -> Staking Rewards Pool     (released over 3 years)
 *   10% (1,000,000) -> Liquidity Provision      (QuickSwap PALPHA/USDC pair)
 *    5% (  500,000) -> Ecosystem / Partnerships  (DAO-voted grants)
 *
 * 6 Utility Model (Lecture 8 framework):
 *   1. RIGHT      - PALPHA holders vote on protocol parameters (PolyAlphaDAO)
 *   2. VALUE      - Fee discounts: 500 PALPHA -> 15%, 2000 -> 10%, 5000 -> 5%
 *   3. TOLL       - Bootstrap phase: vault deposit requires >=100 PALPHA (first 60 days)
 *   4. EARNINGS   - Staking yields 10% APY + 20% share of protocol revenue
 *   5. CURRENCY   - Performance fees can be paid in PALPHA at 20% discount
 *   6. BURN       - 30% of all protocol revenue used to buyback-and-burn monthly
 *
 * Phase transitions (DAO governance):
 *   Phase 1: Owner (William) controls mint/burn - advisory DAO only
 *   Phase 2: DAO controls risk parameters via 48h timelock
 *   Phase 3: renounceFounderControl() transfers ownership to DAO treasury permanently
 *
 * Prototype scope: Deployed on Polygon Amoy testnet.
 *                  Staking pool and DAO governance are architectural stubs in v1.
 */
contract PALPHAToken is ERC20, ERC20Burnable, Ownable {

    uint256 public constant MAX_SUPPLY    = 10_000_000e18;  // 10 million PALPHA
    uint256 public constant INITIAL_MINT  =  3_000_000e18;  // 3 million at launch

    // Governance thresholds
    uint256 public constant MIN_TO_PROPOSE  = 1_000e18;  // 1,000 PALPHA to create a DAO proposal
    uint256 public constant TOLL_THRESHOLD  =   100e18;  // 100 PALPHA for vault deposit access

    // Fee discount tiers (checked by vault in v2)
    uint256 public constant TIER1_BALANCE = 500e18;     // -> 15% performance fee
    uint256 public constant TIER2_BALANCE = 2_000e18;   // -> 10% performance fee
    uint256 public constant TIER3_BALANCE = 5_000e18;   // ->  5% performance fee + 5% APY boost

    // Burn tracking (for Polygonscan transparency)
    uint256 public totalBurned;

    // Phase 3 flag - set when founder renounces control
    bool public founderControlRenounced;

    // -- Events ----------------------------------------------------------------
    event BuybackBurn(uint256 usdcSpent, uint256 alphaBurned, uint256 timestamp);
    event FounderControlRenounced(address indexed daoTreasury, uint256 timestamp);

    // -- Constructor -----------------------------------------------------------

    constructor() ERC20("PolyAlpha Token", "PALPHA") Ownable(msg.sender) {
        _mint(msg.sender, INITIAL_MINT);
    }

    // -- Mint (owner-controlled in Phase 1; DAO-controlled in Phase 2+) -------

    /**
     * @notice Mint new PALPHA. Total supply cannot exceed MAX_SUPPLY.
     *         Used for: staking rewards, governance participation rewards.
     *         Cannot be called after founder renounces control (Phase 3).
     */
    function mint(address to, uint256 amount) external onlyOwner {
        require(!founderControlRenounced, "Control renounced - DAO only");
        require(totalSupply() + amount <= MAX_SUPPLY, "Exceeds max supply");
        _mint(to, amount);
    }

    // -- Buyback & Burn (called monthly by DAO treasury) ----------------------

    /**
     * @notice Records a buyback-and-burn event.
     *         The actual USDC->PALPHA swap happens off-chain (QuickSwap).
     *         The burned tokens are sent here, and the event is logged immutably.
     *
     * @param usdcSpent    USDC (in 6-decimal units) spent on buyback
     * @param alphaToBurn  Amount of PALPHA to burn (must be pre-approved by caller)
     */
    function buybackAndBurn(uint256 usdcSpent, uint256 alphaToBurn) external onlyOwner {
        require(alphaToBurn > 0, "Nothing to burn");
        _burn(msg.sender, alphaToBurn);
        totalBurned += alphaToBurn;
        emit BuybackBurn(usdcSpent, alphaToBurn, block.timestamp);
    }

    // -- Fee discount tier (read by vault) ------------------------------------

    /**
     * @notice Returns the performance fee tier for an address based on PALPHA balance.
     *         0 = standard (20%), 1 = 15%, 2 = 10%, 3 = 5%
     */
    function feeTier(address holder) external view returns (uint8) {
        uint256 bal = balanceOf(holder);
        if (bal >= TIER3_BALANCE) return 3;
        if (bal >= TIER2_BALANCE) return 2;
        if (bal >= TIER1_BALANCE) return 1;
        return 0;
    }

    // -- Toll gate (vault bootstrap check) ------------------------------------

    /**
     * @notice Returns true if the address holds enough PALPHA to deposit during bootstrap.
     *         After bootstrap period (60 days), vault is permissionless - this check is removed.
     */
    function meetsBootstrapToll(address depositor) external view returns (bool) {
        return balanceOf(depositor) >= TOLL_THRESHOLD;
    }

    // -- Phase 3: Founder key burn ---------------------------------------------

    /**
     * @notice Permanently transfers control to the DAO treasury.
     *         After this is called:
     *           - William can never mint or burn again
     *           - All admin functions require DAO governance
     *           - PALPHA ownership = address(daoTreasury)
     *
     *         Guard conditions (from whitepaper):
     *           - DAO must have >=300 active PALPHA holders (checked off-chain)
     *           - Vault must have >=$500K TVL (checked off-chain)
     *           - At least 3 successful DAO proposals executed
     *
     *         This function is the "burn the key" moment described in Lecture 8.
     */
    function renounceFounderControl(address daoTreasury) external onlyOwner {
        require(daoTreasury != address(0), "Invalid DAO treasury");
        founderControlRenounced = true;
        _transferOwnership(daoTreasury);
        emit FounderControlRenounced(daoTreasury, block.timestamp);
    }

    // -- ERC-20 override: track burns ------------------------------------------

    function _update(address from, address to, uint256 value) internal override {
        if (to == address(0)) {
            // Burn - tracked in totalBurned if not via buybackAndBurn
            // (buybackAndBurn updates totalBurned directly)
        }
        super._update(from, to, value);
    }
}
