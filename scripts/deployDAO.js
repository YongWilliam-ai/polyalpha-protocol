/**
 * Deploy PolyAlphaDAO only.
 * Uses the already-deployed PALPHAToken address from CLAUDE.md / config.js.
 * Run: npx hardhat run scripts/deployDAO.js --network chainlab
 */

const { ethers } = require("hardhat");

const PALPHA_ADDRESS = "0x36381Cd13C9030Eb7dfa7C274837115370FEcdbF";

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying PolyAlphaDAO with:", deployer.address);
  console.log("Balance:", ethers.formatEther(await ethers.provider.getBalance(deployer.address)), "MATIC");
  console.log("PALPHAToken:", PALPHA_ADDRESS);

  const PolyAlphaDAO = await ethers.getContractFactory("PolyAlphaDAO");
  const dao = await PolyAlphaDAO.deploy(PALPHA_ADDRESS);
  await dao.waitForDeployment();
  const daoAddress = await dao.getAddress();

  console.log("\n=====================================================");
  console.log("PolyAlphaDAO deployed:", daoAddress);
  console.log("=====================================================");
  console.log("Next step: add to frontend/src/config.js:");
  console.log('  export const DAO_ADDRESS = "' + daoAddress + '";');
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
