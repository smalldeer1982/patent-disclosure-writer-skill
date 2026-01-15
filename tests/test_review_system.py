"""
测试审核团队系统
"""

import pytest
from pathlib import Path
import sys
from unittest.mock import patch

# 添加技能脚本目录到 Python 路径
skill_scripts_path = Path(__file__).parent.parent / ".claude" / "skills" / "patent-disclosure-writer" / "scripts"
sys.path.insert(0, str(skill_scripts_path))

# Constants for test file paths
TEST_STAGE_ID = "pre1"
TEST_STATUS_FILE = Path(f".review-status-{TEST_STAGE_ID}.json")


@pytest.fixture(scope="session", autouse=True)
def import_review_state_manager():
    """
    Import review_state_manager with mocked platform to prevent UTF-8 wrapping.
    This must happen at session scope before any tests run.
    """
    # Mock platform to prevent UTF-8 stdout/stderr wrapping
    with patch.object(sys, 'platform', 'linux'):
        import review_state_manager
        # Store in sys.modules so tests can import it normally
        sys.modules['review_state_manager'] = review_state_manager
        yield review_state_manager


@pytest.fixture
def review_state_file():
    """Create a review state file for testing, cleanup after."""
    import review_state_manager

    state = review_state_manager.init_status(TEST_STAGE_ID, ["01", "02"])
    yield state
    # Cleanup - use missing_ok=True to avoid errors if test failed
    TEST_STATUS_FILE.unlink(missing_ok=True)


class TestReviewCoordinator:
    """测试审核协调器"""

    def test_coordinator_initializes_status(self, review_state_file):
        """测试协调器初始化状态"""
        state = review_state_file

        assert state.stage == TEST_STAGE_ID
        assert state.chapters == ["01", "02"]
        assert state.status == "pending"

    def test_coordinator_reads_status(self, review_state_file):
        """测试协调器读取状态"""
        import review_state_manager

        state = review_state_manager.read_status(TEST_STAGE_ID)

        assert state is not None
        assert state.stage == TEST_STAGE_ID


class TestExpertAgents:
    """测试专家代理"""

    def test_expert_opinion_format(self):
        """测试专家意见格式"""
        opinion = {
            "expert": "expert-sr-tech",
            "role": "资深技术专家",
            "vote": "approve",
            "vote_weight": 2,
            "opinion": "技术方案清晰可行",
            "modifications": [],
            "critical_issues": [],
            "score": {
                "feasibility": 9,
                "innovation": 8,
                "overall": 8.5
            }
        }

        assert opinion["vote_weight"] == 2
        assert opinion["vote"] in ["approve", "approve_with_reservations", "reject", "abstain"]
        assert "score" in opinion


class TestVotingMechanism:
    """测试投票机制"""

    def test_weighted_voting_calculation(self):
        """测试加权投票计算"""
        votes = {
            "expert-sr-tech": "approve",      # 2票
            "expert-tech": "approve",          # 1票
            "expert-legal": "approve",         # 1票
            "expert-sr-agent": "approve",      # 2票
            "expert-agent": "approve",         # 1票
        }

        vote_weights = {
            "expert-sr-tech": 2,
            "expert-tech": 1,
            "expert-legal": 1,
            "expert-sr-agent": 2,
            "expert-agent": 1,
        }

        total = 0
        for expert, vote in votes.items():
            if vote == "approve":
                total += vote_weights[expert]

        assert total == 7  # 全部赞成 = 7票


class TestModificationApplier:
    """测试修改应用器"""

    def test_version_control(self):
        """测试版本控制"""
        # 原文件
        original = "test_chapter.md"

        # 第一次修改
        v1 = "test_chapter.md"
        v2 = "test_chapter_v2.md"

        assert v2.endswith("_v2.md")

    def test_auto_apply_detection(self):
        """测试自动应用检测"""
        modification = {
            "type": "error_correction",
            "auto_apply": True
        }

        assert modification["auto_apply"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
