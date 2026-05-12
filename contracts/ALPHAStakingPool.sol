// SPDX-License-Identifier: MIT
pragma solidity 0.8.25;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title ALPHAStakingPool
 * @notice Stake PALPHA tokens to earn 10% APY in PALPHA rewards.
 *
 * Design (pre-funded pool, no minting):
 *   Owner calls fundRewards() to deposit PALPHA reward tokens into this contract.
 *   Stakers earn 10% APY on their staked balance, paid from that pool.
 *   If the reward pool runs dry, claimReward() reverts -- owner must refund.
 *
 * Reward accounting uses the Synthetix reward-per-token accumulator pattern:
 *   rewardPerTokenStored += elapsed * RATE / SECONDS_PER_YEAR
 *   earned(user) = stakedBalance * (rewardPerToken - userCheckpoint) / 1e18
 *
 * This formula gives each staker exactly 10% APY regardless of total staked size.
 * The reward pool must be pre-funded accordingly by the DAO treasury.
 *
 * Phase 2 upgrade: replace 10% hardcoded APY with DAO-voted parameter.
 */
contract ALPHAStakingPool is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    IERC20 public immutable palpha;

    // 10% APY -- 1,000 bps out of 10,000
    uint256 public constant ANNUAL_REWARD_RATE_BPS = 1_000;
    uint256 public constant BPS_DENOMINATOR        = 10_000;
    uint256 public constant SECONDS_PER_YEAR       = 365 days;

    // Global accumulator (scaled 1e18 for precision)
    uint256 public rewardPerTokenStored;
    uint256 public lastUpdateTime;
    uint256 public totalStaked;

    // Per-user state
    mapping(address => uint256) public stakedBalance;
    mapping(address => uint256) public userRewardPerTokenPaid; // checkpoint
    mapping(address => uint256) public pendingRewards;         // accrued, not yet claimed

    // --- Events ------------------------------------------------------------------

    event Staked(address indexed user, uint256 amount);
    event Unstaked(address indexed user, uint256 amount);
    event RewardClaimed(address indexed user, uint256 amount);
    event RewardsFunded(uint256 amount);

    // --- Errors ------------------------------------------------------------------

    error ZeroAmount();
    error InsufficientStake();
    error NothingToClaim();
    error RewardPoolDepleted();

    // --- Constructor -------------------------------------------------------------

    constructor(address _palpha) Ownable(msg.sender) {
        palpha = IERC20(_palpha);
        lastUpdateTime = block.timestamp;
    }

    // --- Owner: fund the reward pool ---------------------------------------------

    /**
     * @notice Deposit PALPHA into this contract to back future staking rewards.
     *         DAO treasury should call this monthly with enough PALPHA to cover
     *         10% APY for the expected staked amount over the coming period.
     */
    function fundRewards(uint256 amount) external onlyOwner {
        if (amount == 0) revert ZeroAmount();
        palpha.safeTransferFrom(msg.sender, address(this), amount);
        emit RewardsFunded(amount);
    }

    // --- Staker actions ----------------------------------------------------------

    /**
     * @notice Stake PALPHA. Accrued rewards are snapshotted first.
     */
    function stake(uint256 amount) external nonReentrant {
        if (amount == 0) revert ZeroAmount();
        _updateReward(msg.sender);

        stakedBalance[msg.sender] += amount;
        totalStaked += amount;
        palpha.safeTransferFrom(msg.sender, address(this), amount);

        emit Staked(msg.sender, amount);
    }

    /**
     * @notice Unstake PALPHA. Accrued rewards remain claimable separately.
     */
    function unstake(uint256 amount) external nonReentrant {
        if (amount == 0) revert ZeroAmount();
        if (stakedBalance[msg.sender] < amount) revert InsufficientStake();
        _updateReward(msg.sender);

        stakedBalance[msg.sender] -= amount;
        totalStaked -= amount;
        palpha.safeTransfer(msg.sender, amount);

        emit Unstaked(msg.sender, amount);
    }

    /**
     * @notice Claim all accrued PALPHA rewards.
     *         Reverts if the reward pool has insufficient balance.
     */
    function claimReward() external nonReentrant {
        _updateReward(msg.sender);

        uint256 reward = pendingRewards[msg.sender];
        if (reward == 0) revert NothingToClaim();

        // Safety: available = total balance minus the staked tokens
        uint256 available = palpha.balanceOf(address(this)) - totalStaked;
        if (available < reward) revert RewardPoolDepleted();

        pendingRewards[msg.sender] = 0;
        palpha.safeTransfer(msg.sender, reward);

        emit RewardClaimed(msg.sender, reward);
    }

    // --- Views -------------------------------------------------------------------

    /**
     * @notice Current global reward accumulator per staked token (scaled 1e18).
     *         Increases at ANNUAL_REWARD_RATE_BPS / SECONDS_PER_YEAR per second.
     */
    function rewardPerToken() public view returns (uint256) {
        uint256 elapsed = block.timestamp - lastUpdateTime;
        return rewardPerTokenStored
            + (elapsed * ANNUAL_REWARD_RATE_BPS * 1e18)
            / (BPS_DENOMINATOR * SECONDS_PER_YEAR);
    }

    /**
     * @notice Total PALPHA rewards earned by `user` since last claim.
     */
    function earned(address user) public view returns (uint256) {
        return (
            stakedBalance[user]
            * (rewardPerToken() - userRewardPerTokenPaid[user])
            / 1e18
        ) + pendingRewards[user];
    }

    /**
     * @notice PALPHA available to pay future rewards (excludes staked principal).
     */
    function rewardPoolBalance() external view returns (uint256) {
        uint256 bal = palpha.balanceOf(address(this));
        return bal > totalStaked ? bal - totalStaked : 0;
    }

    // --- Internal ----------------------------------------------------------------

    function _updateReward(address user) internal {
        rewardPerTokenStored = rewardPerToken();
        lastUpdateTime = block.timestamp;
        if (user != address(0)) {
            pendingRewards[user] = earned(user);
            userRewardPerTokenPaid[user] = rewardPerTokenStored;
        }
    }
}
