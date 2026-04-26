// SPDX-License-Identifier: MIT
pragma solidity 0.8.25;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title PolyAlphaDAO
 * @notice On-chain governance for the PolyAlpha Protocol.
 *
 * Any address holding >= 1,000 PALPHA can create a proposal.
 * Token holders vote YES/NO during the 48-hour voting window.
 * Vote weight = caller's PALPHA balance at vote time.
 * (Phase 2 upgrade: migrate to ERC20Votes snapshot weighting.)
 *
 * Execution conditions (after voting window closes):
 *   1. Total votes (for + against) >= 100,000 PALPHA  (quorum)
 *   2. forVotes > againstVotes                         (simple majority)
 *   3. Voting window has fully closed                  (48 h timelock)
 *
 * Proposal lifecycle:
 *   ACTIVE   -- voting window open  (0 to 48 h after creation)
 *   EXPIRED  -- window closed, not yet executed
 *   EXECUTED -- executeProposal() called successfully
 *   CANCELED -- proposer called cancelProposal() before execution
 *
 * Phase 3 integration:
 *   After PALPHAToken.renounceFounderControl(address(this)), this DAO contract
 *   becomes the owner of PALPHAToken. Minting, burning, and risk parameter
 *   changes then require a successful DAO vote.
 */
contract PolyAlphaDAO is ReentrancyGuard {

    IERC20 public immutable palpha;

    // --- Governance constants -------------------------------------------------

    uint256 public constant MIN_PROPOSAL_BALANCE = 1_000e18;   // 1,000 PALPHA to propose
    uint256 public constant QUORUM               = 100_000e18; // minimum votes cast
    uint256 public constant VOTING_PERIOD        = 48 hours;

    // --- Proposal storage -----------------------------------------------------

    struct Proposal {
        address proposer;
        string  description;
        address targetContract;
        bytes   callData;
        uint256 createdAt;      // block.timestamp at creation
        uint256 forVotes;       // PALPHA tokens voted YES
        uint256 againstVotes;   // PALPHA tokens voted NO
        bool    executed;
        bool    canceled;
    }

    uint256 public proposalCount;
    mapping(uint256 => Proposal) public proposals;

    // Tracks whether an address has already voted on a given proposal
    mapping(uint256 => mapping(address => bool)) public hasVoted;

    // --- Events ---------------------------------------------------------------

    event ProposalCreated(
        uint256 indexed proposalId,
        address indexed proposer,
        string          description,
        address         targetContract
    );
    event Voted(
        uint256 indexed proposalId,
        address indexed voter,
        bool            support,
        uint256         weight
    );
    event ProposalExecuted(uint256 indexed proposalId, address indexed executor);
    event ProposalCanceled(uint256 indexed proposalId, address indexed proposer);

    // --- Errors ---------------------------------------------------------------

    error InsufficientBalance();
    error ProposalNotFound();
    error VotingStillOpen();
    error VotingClosed();
    error AlreadyVoted();
    error AlreadyExecuted();
    error AlreadyCanceled();
    error QuorumNotMet();
    error MajorityNotReached();
    error NotProposer();
    error ExecutionFailed(bytes returnData);

    // --- Constructor ----------------------------------------------------------

    constructor(address _palpha) {
        palpha = IERC20(_palpha);
    }

    // --- Core governance functions --------------------------------------------

    /**
     * @notice Create a governance proposal.
     *         Caller must hold >= MIN_PROPOSAL_BALANCE PALPHA.
     *
     * @param description     Human-readable summary of the proposal.
     * @param targetContract  Contract to call if the proposal passes.
     * @param callData        ABI-encoded function call for the target contract.
     *
     * @return proposalId     Incrementing proposal ID.
     */
    function createProposal(
        string  calldata description,
        address targetContract,
        bytes   calldata callData
    ) external returns (uint256 proposalId) {
        if (palpha.balanceOf(msg.sender) < MIN_PROPOSAL_BALANCE) {
            revert InsufficientBalance();
        }

        proposalCount++;
        proposalId = proposalCount;

        proposals[proposalId] = Proposal({
            proposer:       msg.sender,
            description:    description,
            targetContract: targetContract,
            callData:       callData,
            createdAt:      block.timestamp,
            forVotes:       0,
            againstVotes:   0,
            executed:       false,
            canceled:       false
        });

        emit ProposalCreated(proposalId, msg.sender, description, targetContract);
    }

    /**
     * @notice Vote YES or NO on a proposal during its 48-hour window.
     *         Vote weight = caller's current PALPHA balance.
     *         Each address may vote at most once per proposal.
     *
     *         NOTE: Balance is read at vote time (not at proposal creation).
     *         This is sufficient for a Phase 1 prototype. Phase 2 should
     *         migrate PALPHAToken to ERC20Votes and use historical snapshots
     *         to prevent buy-vote-sell manipulation.
     *
     * @param proposalId  ID of the proposal to vote on.
     * @param support     true = YES vote, false = NO vote.
     */
    function vote(uint256 proposalId, bool support) external {
        Proposal storage prop = _requireExists(proposalId);

        if (prop.canceled)  revert AlreadyCanceled();
        if (prop.executed)  revert AlreadyExecuted();
        if (block.timestamp > prop.createdAt + VOTING_PERIOD) revert VotingClosed();
        if (hasVoted[proposalId][msg.sender]) revert AlreadyVoted();

        uint256 weight = palpha.balanceOf(msg.sender);
        hasVoted[proposalId][msg.sender] = true;

        if (support) {
            prop.forVotes += weight;
        } else {
            prop.againstVotes += weight;
        }

        emit Voted(proposalId, msg.sender, support, weight);
    }

    /**
     * @notice Execute a proposal that has passed.
     *         Callable by anyone after the 48-hour timelock expires.
     *         Reverts if quorum is not met or majority not reached.
     *         Reverts if the target contract call fails.
     */
    function executeProposal(uint256 proposalId) external nonReentrant {
        Proposal storage prop = _requireExists(proposalId);

        if (prop.canceled) revert AlreadyCanceled();
        if (prop.executed) revert AlreadyExecuted();
        if (block.timestamp <= prop.createdAt + VOTING_PERIOD) revert VotingStillOpen();

        uint256 totalVotes = prop.forVotes + prop.againstVotes;
        if (totalVotes < QUORUM) revert QuorumNotMet();
        if (prop.forVotes <= prop.againstVotes) revert MajorityNotReached();

        prop.executed = true;

        (bool success, bytes memory returnData) = prop.targetContract.call(prop.callData);
        if (!success) revert ExecutionFailed(returnData);

        emit ProposalExecuted(proposalId, msg.sender);
    }

    /**
     * @notice Cancel a proposal before it is executed.
     *         Only the original proposer can cancel.
     *         Cannot cancel an already-executed proposal.
     */
    function cancelProposal(uint256 proposalId) external {
        Proposal storage prop = _requireExists(proposalId);

        if (prop.executed)         revert AlreadyExecuted();
        if (prop.canceled)         revert AlreadyCanceled();
        if (msg.sender != prop.proposer) revert NotProposer();

        prop.canceled = true;
        emit ProposalCanceled(proposalId, msg.sender);
    }

    // --- View helpers ---------------------------------------------------------

    /**
     * @notice Full state of a proposal.
     */
    function getProposal(uint256 proposalId) external view returns (
        address proposer,
        string  memory description,
        address targetContract,
        uint256 createdAt,
        uint256 votingDeadline,
        uint256 forVotes,
        uint256 againstVotes,
        bool    executed,
        bool    canceled
    ) {
        Proposal storage prop = proposals[proposalId];
        if (prop.createdAt == 0) revert ProposalNotFound();
        return (
            prop.proposer,
            prop.description,
            prop.targetContract,
            prop.createdAt,
            prop.createdAt + VOTING_PERIOD,
            prop.forVotes,
            prop.againstVotes,
            prop.executed,
            prop.canceled
        );
    }

    /**
     * @notice True if the 48-hour voting window is still open.
     */
    function isVotingOpen(uint256 proposalId) external view returns (bool) {
        Proposal storage prop = proposals[proposalId];
        return prop.createdAt != 0
            && !prop.executed
            && !prop.canceled
            && block.timestamp <= prop.createdAt + VOTING_PERIOD;
    }

    /**
     * @notice True if the proposal has passed quorum AND simple majority.
     *         Does NOT check whether the voting window has closed.
     */
    function hasPassed(uint256 proposalId) external view returns (bool) {
        Proposal storage prop = proposals[proposalId];
        uint256 totalVotes = prop.forVotes + prop.againstVotes;
        return totalVotes >= QUORUM && prop.forVotes > prop.againstVotes;
    }

    // --- Internal -------------------------------------------------------------

    function _requireExists(uint256 proposalId) internal view returns (Proposal storage prop) {
        prop = proposals[proposalId];
        if (prop.createdAt == 0) revert ProposalNotFound();
    }
}
