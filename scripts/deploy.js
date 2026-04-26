/**
 * PolyAlpha deployment script -- Polygon Amoy testnet
 * Deploys all 6 core contracts in dependency order.
 *
 * Order:
 *   1. MockUSDC          (ERC-20 test collateral)
 *   2. PALPHAToken       (governance + utility token)
 *   3. PolyAlphaVault    (ERC-4626 vault, AI signal log)
 *   4. ALPHAStakingPool  (10% APY PALPHA staking)
 *   5. PALPHABuybackBurn (off-chain buyback + on-chain burn)
 *   6. PolyAlphaDAO      (48-h timelock governance)
 *
 * After deployment, copy all addresses into frontend/src/config.js
 * and into your .env (VAULT_CONTRACT_ADDRESS).
 */

const { ethers } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying with:", deployer.address);
  console.log("Balance:", ethers.formatEther(await ethers.provider.getBalance(deployer.address)), "MATIC");

  // 1. Deploy MockUSDC
  console.log("\n[1/6] Deploying MockUSDC...");
  const MockUSDC = await ethers.getContractFactory("MockUSDC");
  const usdc = await MockUSDC.deploy();
  await usdc.waitForDeployment();
  const usdcAddress = await usdc.getAddress();
  console.log("  MockUSDC deployed:", usdcAddress);

  // 2. Deploy PALPHAToken (mints 3,000,000 PALPHA to deployer)
  console.log("\n[2/6] Deploying PALPHAToken...");
  const PALPHAToken = await ethers.getContractFactory("PALPHAToken");
  const palpha = await PALPHAToken.deploy();
  await palpha.waitForDeployment();
  const palphaAddress = await palpha.getAddress();
  console.log("  PALPHAToken deployed:", palphaAddress);

  // 3. Deploy PolyAlphaVault (deployer doubles as AI agent address for testnet)
  console.log("\n[3/6] Deploying PolyAlphaVault...");
  const agentAddress = deployer.address;
  const PolyAlphaVault = await ethers.getContractFactory("PolyAlphaVault");
  const vault = await PolyAlphaVault.deploy(usdcAddress, agentAddress);
  await vault.waitForDeployment();
  const vaultAddress = await vault.getAddress();
  console.log("  PolyAlphaVault deployed:", vaultAddress);

  // 4. Deploy ALPHAStakingPool
  console.log("\n[4/6] Deploying ALPHAStakingPool...");
  const ALPHAStakingPool = await ethers.getContractFactory("ALPHAStakingPool");
  const staking = await ALPHAStakingPool.deploy(palphaAddress);
  await staking.waitForDeployment();
  const stakingAddress = await staking.getAddress();
  console.log("  ALPHAStakingPool deployed:", stakingAddress);

  // 5. Deploy PALPHABuybackBurn (accepts PALPHA for off-chain buyback burns)
  console.log("\n[5/6] Deploying PALPHABuybackBurn...");
  const PALPHABuybackBurn = await ethers.getContractFactory("PALPHABuybackBurn");
  const buyback = await PALPHABuybackBurn.deploy(palphaAddress);   // 1 arg: PALPHA address
  await buyback.waitForDeployment();
  const buybackAddress = await buyback.getAddress();
  console.log("  PALPHABuybackBurn deployed:", buybackAddress);

  // 6. Deploy PolyAlphaDAO (governance; Phase 3: call palpha.renounceFounderControl(daoAddress))
  console.log("\n[6/6] Deploying PolyAlphaDAO...");
  const PolyAlphaDAO = await ethers.getContractFactory("PolyAlphaDAO");
  const dao = await PolyAlphaDAO.deploy(palphaAddress);
  await dao.waitForDeployment();
  const daoAddress = await dao.getAddress();
  console.log("  PolyAlphaDAO deployed:", daoAddress);

  // Smoke test: mint 10,000 USDC to deployer for manual testing
  console.log("\n[Smoke Test] Minting 10,000 USDC to deployer...");
  await usdc.mint(deployer.address, ethers.parseUnits("10000", 6));
  console.log("  Done.");

  // Summary
  console.log("\n=====================================================");
  console.log("DEPLOYMENT COMPLETE -- Save these addresses:");
  console.log("=====================================================");
  console.log("MockUSDC:          ", usdcAddress);
  console.log("PALPHAToken:       ", palphaAddress);
  console.log("PolyAlphaVault:    ", vaultAddress);
  console.log("ALPHAStakingPool:  ", stakingAddress);
  console.log("PALPHABuybackBurn: ", buybackAddress);
  console.log("PolyAlphaDAO:      ", daoAddress);
  console.log("=====================================================");
  console.log("\nNext steps:");
  console.log("  1. Copy PolyAlphaVault address to .env -> VAULT_CONTRACT_ADDRESS");
  console.log("  2. Copy all addresses to frontend/src/config.js");
  console.log("  3. Run: npx hardhat verify --network amoy <address> <args>");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
