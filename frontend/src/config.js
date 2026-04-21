// Contract configuration — update after deployment
export const VAULT_ADDRESS   = process.env.REACT_APP_VAULT_ADDRESS   || "";
export const PALPHA_ADDRESS  = process.env.REACT_APP_PALPHA_ADDRESS  || "";
export const CHAIN_ID        = 80002;  // Polygon Amoy
export const CHAIN_NAME      = "Polygon Amoy Testnet";
export const RPC_URL         = "https://rpc-amoy.polygon.technology/";
export const POLYGONSCAN_URL = "https://amoy.polygonscan.com";

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
];
