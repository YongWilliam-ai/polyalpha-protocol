// PolyAlpha Protocol — Contract Configuration
// Network: ChainLab Testnet (chainId: 31337)
// Deployed: 2026-04-27

export const CHAIN_ID        = 31337;
export const CHAIN_NAME      = "ChainLab Testnet";
export const RPC_URL         = "https://testnet.chainlab.fun";
export const EXPLORER_URL    = "https://testnet.chainlab.fun";
export const POLYGONSCAN_URL = "https://testnet.chainlab.fun"; // alias for ChainLab explorer

// ── Deployed Contract Addresses ──────────────────────────────────────────────
export const VAULT_ADDRESS        = "0x1c275054C7159aBBF446E652A744EFB8cbf6efd0";
export const PALPHA_ADDRESS       = "0x36381Cd13C9030Eb7dfa7C274837115370FEcdbF";
export const MOCK_USDC_ADDRESS    = "0x77D7D52eE789B7C6bcD94eb87e2391BBb94A8D0a";
export const STAKING_ADDRESS      = "0xF8E9E3af72E1F673B21eCB4d96C99BF9c1D47832";
export const BUYBACK_ADDRESS      = "0xEc33dBc9dFAa1c380863547C5bCB7597eD611Ea4";

// ── ABIs ─────────────────────────────────────────────────────────────────────
export const VAULT_ABI = [
  "function totalAssets() view returns (uint256)",
  "function totalSupply() view returns (uint256)",
  "function balanceOf(address) view returns (uint256)",
  "function halted() view returns (bool)",
  "function currentDrawdownBps() view returns (uint256)",
  "function peakAssets() view returns (uint256)",
  "function deposit(uint256 assets, address receiver) returns (uint256)",
  "function withdraw(uint256 assets, address receiver, address owner) returns (uint256)",
  "event PositionLogged(address indexed agent, string marketQuestion, uint256 aiProbabilityBps, uint256 marketPriceBps, int256 edgeBps, string side, uint256 kellyFractionBps, bytes32 oracleInputHash, uint256 timestamp)",
];

export const PALPHA_ABI = [
  "function balanceOf(address) view returns (uint256)",
  "function totalSupply() view returns (uint256)",
  "function totalBurned() view returns (uint256)",
  "function feeTier(address) view returns (uint8)",
  "function MAX_SUPPLY() view returns (uint256)",
  "function approve(address spender, uint256 amount) returns (bool)",
];

export const USDC_ABI = [
  "function balanceOf(address) view returns (uint256)",
  "function approve(address spender, uint256 amount) returns (bool)",
  "function allowance(address owner, address spender) view returns (uint256)",
  "function decimals() view returns (uint8)",
];

export const STAKING_ABI = [
  "function stake(uint256 amount) external",
  "function unstake(uint256 amount) external",
  "function claimReward() external",
  "function stakedBalance(address) view returns (uint256)",
  "function earned(address) view returns (uint256)",
  "function totalStaked() view returns (uint256)",
  "event Staked(address indexed user, uint256 amount)",
  "event Unstaked(address indexed user, uint256 amount)",
  "event RewardClaimed(address indexed user, uint256 reward)",
];

export const BUYBACK_ABI = [
  "function depositForBurn(uint256 amount) external",
  "function executeBurn(uint256 usdcSpent) external",
  "function pendingBurn() view returns (uint256)",
  "function totalAlphaBurned() view returns (uint256)",
  "event BuybackExecuted(uint256 usdcSpent, uint256 alphaBurned, uint256 timestamp)",
];
