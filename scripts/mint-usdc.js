/**
 * mint-usdc.js — Mint MockUSDC test tokens to a target address
 * 
 * Usage:
 *   npx hardhat run scripts/mint-usdc.js --network chainlab
 * 
 * By default mints 10,000 USDC to the deployer wallet.
 * To mint to a different address, set MINT_TO env var:
 *   MINT_TO=0xYourAddress npx hardhat run scripts/mint-usdc.js --network chainlab
 */

const { ethers } = require("hardhat");

// MockUSDC deployed address on ChainLab Testnet
const MOCK_USDC_ADDRESS = "0x77D7D52eE789B7C6bcD94eb87e2391BBb94A8D0a";

const MOCK_USDC_ABI = [
  "function mint(address to, uint256 amount) external",
  "function balanceOf(address) view returns (uint256)",
  "function decimals() view returns (uint8)",
  "function owner() view returns (address)",
];

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Using wallet:", deployer.address);

  const mintTo = process.env.MINT_TO || deployer.address;
  const mintAmount = process.env.MINT_AMOUNT || "10000"; // default 10,000 USDC

  const usdc = new ethers.Contract(MOCK_USDC_ADDRESS, MOCK_USDC_ABI, deployer);

  // Check owner
  const owner = await usdc.owner();
  console.log("MockUSDC owner:", owner);
  if (owner.toLowerCase() !== deployer.address.toLowerCase()) {
    console.error("ERROR: Your wallet is not the owner of MockUSDC.");
    console.error("Only the deployer wallet can mint. Use the deployer private key.");
    process.exit(1);
  }

  // Check balance before
  const balBefore = await usdc.balanceOf(mintTo);
  console.log(`Balance before: ${ethers.formatUnits(balBefore, 6)} USDC`);

  // Mint
  const amount = ethers.parseUnits(mintAmount, 6);
  console.log(`Minting ${mintAmount} USDC to ${mintTo}...`);
  const tx = await usdc.mint(mintTo, amount);
  await tx.wait();
  console.log(`Tx hash: ${tx.hash}`);

  // Check balance after
  const balAfter = await usdc.balanceOf(mintTo);
  console.log(`Balance after: ${ethers.formatUnits(balAfter, 6)} USDC`);
  console.log("Done! You can now deposit USDC into the PolyAlpha Vault.");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
