// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract AuditLog {
    struct AccessLog {
        string emergencyId;    // Patient's emergency_id from DB
        string licenseNo;      // Doctor's licenseNo from DB
        uint256 timestamp;
        string accessMethod;   // "QR", "Aadhaar", "mobile"
        string reason;         // "emergency", "accident", etc.
        bytes32 logHash;       // SHA256 hash for integrity verification
    }

    AccessLog[] public accessLogs;
    mapping(bytes32 => bool) public usedHashes;

    event LogRecorded(
        uint256 indexed logId, 
        string indexed emergencyId, 
        string licenseNo,
        bytes32 logHash
    );

    // Main function - called by Flask when doctor accesses patient data
    function recordAccess(
        string memory _emergencyId,
        string memory _licenseNo,
        string memory _accessMethod,
        string memory _reason,
        bytes32 _logHash
    ) public {
        require(bytes(_emergencyId).length > 0, "Emergency ID required");
        require(bytes(_licenseNo).length > 0, "License No required");
        require(!usedHashes[_logHash], "Hash already exists");
        
        accessLogs.push(AccessLog({
            emergencyId: _emergencyId,
            licenseNo: _licenseNo,
            timestamp: block.timestamp,
            accessMethod: _accessMethod,
            reason: _reason,
            logHash: _logHash
        }));
        
        usedHashes[_logHash] = true;
        emit LogRecorded(accessLogs.length - 1, _emergencyId, _licenseNo, _logHash);
    }

    // Get total logs count
    function getLogCount() public view returns (uint256) {
        return accessLogs.length;
    }

    // Get specific log by index
    function getLog(uint256 _index) public view returns (
        string memory emergencyId,
        string memory licenseNo,
        uint256 timestamp,
        string memory accessMethod,
        string memory reason,
        bytes32 logHash
    ) {
        require(_index < accessLogs.length, "Invalid log index");
        AccessLog memory log = accessLogs[_index];
        return (
            log.emergencyId, 
            log.licenseNo, 
            log.timestamp, 
            log.accessMethod, 
            log.reason, 
            log.logHash
        );
    }

    // Verify if a hash exists on-chain
    function verifyHash(bytes32 _logHash) public view returns (bool) {
        return usedHashes[_logHash];
    }
}
