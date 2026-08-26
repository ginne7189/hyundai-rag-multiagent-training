"""Day 4 multi-agent harness package.

The package separates role execution, handoff validation, verification,
orchestration, and the outer harness so learners can see who owns each rule.
"""

from coursekit.day4_harness.harness import MultiAgentHarness, SearchAndVerifySystem
from coursekit.day4_harness.verifier import EvidenceVerifier

__all__ = ["EvidenceVerifier", "MultiAgentHarness", "SearchAndVerifySystem"]
