// SPDX-License-Identifier: MIT
pragma solidity 0.8.25;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title MockUSDC
 * @notice Test USDC for Polygon Amoy testnet. 6 decimals (same as real USDC).
 *         On mainnet, replace with real USDC: 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174
 */
contract MockUSDC is ERC20, Ownable {
    constructor() ERC20("USD Coin (Test)", "USDC") Ownable(msg.sender) {}

    function decimals() public pure override returns (uint8) {
        return 6;
    }

    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }
}
