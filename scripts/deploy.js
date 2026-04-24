/**
 * PolyAlpha deployment script — Polygon Amoy testnet
 * Deploys all 5 core contracts in order.
 */

const { ethers } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying with:", deployer.address);
  console.log("Balance:", ethers.formatEther(await ethers.provider.getBalance(deployer.address)), "MATIC");

  // 1. Deploy MockUSDC
  console.log("\n[1/5] Deploying MockUSDC...");
  const MockUSDC = await ethers.getContractFactory("MockUSDC");
  const usdc = await MockUSDC.deploy();
  await usdc.waitForDeployment();
  const usdcAddress = await usdc.getAddress();
  console.log("✅ MockUSDC deployed:", usdcAddress);

  // 2. Deploy PALPHAToken
  console.log("\n[2/5] Deploying PALPHAToken...");
  const PALPHAToken = await ethers.getContractFactory("PALPHAToken");
  const palpha = await PALPHAToken.deploy();
  await palpha.waitForDeployment();
  const palphaAddress = await palpha.getAddress();
  console.log("✅ PALPHAToken deployed:", palphaAddress);

  // 3. Deploy PolyAlphaVault
  console.log("\n[3/5] Deploying PolyAlphaVault...");
  const agentAddress = deployer.address; 
  const PolyAlphaVault = await ethers.getContractFactory("PolyAlphaVault");
  const vault = await PolyAlphaVault.deploy(usdcAddress, agentAddress);
  await vault.waitForDeployment();
  const vaultAddress = await vault.getAddress();
  console.log("✅ PolyAlphaVault deployed:", vaultAddress);

  // 4. Deploy ALPHAStakingPool
  console.log("\n[4/5] Deploying ALPHAStakingPool...");
  const ALPHAStakingPool = await ethers.getContractFactory("ALPHAStakingPool");
  const staking = await ALPHAStakingPool.deploy(palphaAddress);
  await staking.waitForDeployment();
  const stakingAddress = await staking.getAddress();
  console.log("✅ ALPHAStakingPool deployed:", stakingAddress);

  // 5. Deploy PALPHABuybackBurn
  console.log("\n[5/5] Deploying PALPHABuybackBurn...");
  const PALPHABuybackBurn = await ethers.getContractFactory("PALPHABuybackBurn");
  const buyback = await PALPHABuybackBurn.deploy(palphaAddress, usdcAddress);
  await buyback.waitForDeployment();
  const buybackAddress = await buyback.getAddress();
  console.log("✅ PALPHABuybackBurn deployed:", buybackAddress);

  // Summary
  console.log("\n═══════════════════════════════════════════");
  console.log("DEPLOYMENT COMPLETE — Save these addresses:");
  console.log("═══════════════════════════════════════════");
  console.log("MockUSDC:          ", usdcAddress);
  console.log("PALPHAToken:       ", palphaAddress);
  console.log("PolyAlphaVault:    ", vaultAddress);
  console.log("ALPHAStakingPool:  ", stakingAddress);
  console.log("PALPHABuybackBurn: ", buybackAddress);
  console.log("═══════════════════════════════════════════");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
