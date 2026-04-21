/**
 * PolyAlpha deployment script — Polygon Amoy testnet
 *
 * Usage:
 *   npx hardhat run scripts/deploy.js --network amoy
 *
 * Deploys:
 *   1. MockUSDC (testnet only — real USDC on mainnet)
 *   2. PolyAlphaVault
 *   3. (Optional) PALPHAToken
 *
 * After deployment, copy the contract addresses into your .env file.
 */

const { ethers } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying with:", deployer.address);
  console.log("Balance:", ethers.formatEther(await ethers.provider.getBalance(deployer.address)), "MATIC");

  // ── Step 1: Deploy mock USDC (6 decimals, matches real USDC) ──────────────
  console.log("\n[1/3] Deploying MockUSDC...");
  const MockUSDC = await ethers.getContractFactory("MockUSDC");
  const usdc = await MockUSDC.deploy();
  await usdc.waitForDeployment();
  const usdcAddress = await usdc.getAddress();
  console.log("✅ MockUSDC deployed:", usdcAddress);

  // Mint 10,000 USDC to deployer for testing
  await usdc.mint(deployer.address, ethers.parseUnits("10000", 6));
  console.log("   Minted 10,000 test USDC to deployer");

  // ── Step 2: Deploy PolyAlphaVault ─────────────────────────────────────────
  console.log("\n[2/3] Deploying PolyAlphaVault...");
  const agentAddress = deployer.address; // Set this to your separate agent wallet later
  const PolyAlphaVault = await ethers.getContractFactory("PolyAlphaVault");
  const vault = await PolyAlphaVault.deploy(usdcAddress, agentAddress);
  await vault.waitForDeployment();
  const vaultAddress = await vault.getAddress();
  console.log("✅ PolyAlphaVault deployed:", vaultAddress);

  // ── Step 3: Quick smoke test ───────────────────────────────────────────────
  console.log("\n[3/3] Running smoke test...");
  const depositAmount = ethers.parseUnits("100", 6); // 100 USDC
  await usdc.approve(vaultAddress, depositAmount);
  const tx = await vault.deposit(depositAmount, deployer.address);
  await tx.wait();
  const shares = await vault.balanceOf(deployer.address);
  console.log("✅ Deposited 100 USDC, received", ethers.formatUnits(shares, 6), "paUSDC shares");

  // Log a test position signal
  const testHash = ethers.keccak256(ethers.toUtf8Bytes("btcOpen:45000,btcNow:45200,polyOdds:5800,ts:1713700000"));
  const logTx = await vault.logPosition(
    "Will BTC be higher in 15 minutes? [Apr 21 2026]",
    7100,   // 71.00% AI probability
    6200,   // 62.00% market price
    "UP",
    750,    // 7.50% kelly fraction
    testHash
  );
  const receipt = await logTx.wait();
  console.log("✅ logPosition() fired — tx hash:", receipt.hash);
  console.log("   Check on Polygonscan Amoy:", `https://amoy.polygonscan.com/tx/${receipt.hash}`);

  // ── Summary ───────────────────────────────────────────────────────────────
  console.log("\n═══════════════════════════════════════════");
  console.log("DEPLOYMENT COMPLETE — Save these addresses:");
  console.log("═══════════════════════════════════════════");
  console.log("MockUSDC:       ", usdcAddress);
  console.log("PolyAlphaVault: ", vaultAddress);
  console.log("Network:         Polygon Amoy (chainId: 80002)");
  console.log("\nAdd to your .env:");
  console.log(`VAULT_CONTRACT_ADDRESS=${vaultAddress}`);
  console.log(`MOCK_USDC_ADDRESS=${usdcAddress}`);
  console.log("\nVerify on Polygonscan:");
  console.log(`npx hardhat verify --network amoy ${vaultAddress} ${usdcAddress} ${agentAddress}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
