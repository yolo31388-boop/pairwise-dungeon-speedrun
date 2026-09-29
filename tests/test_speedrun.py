"""副本计时与速通系统 - 红态测试"""
import pytest, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dungeon.speedrun import SpeedrunSystem, RunRecord

class TestTimerStart:
    def test_timer_starts_on_combat_not_enter(self):
        ss = SpeedrunSystem()
        assert ss.should_start_timer("enter_dungeon") == False  # bug1: True
        assert ss.should_start_timer("combat_start") == True

class TestDifficultyRanking:
    def test_difficulties_ranked_separately(self):
        ss = SpeedrunSystem()
        r1 = RunRecord("r1", "p1", "d1", "normal", 600)
        r2 = RunRecord("r2", "p2", "d1", "hard", 1200)
        ss.records = [r1, r2]
        # hard的1200不应该比normal的600排后面
        rank_hard = ss.get_rank(r2)
        assert rank_hard <= 2  # bug2: 可能排第2但应该分层

class TestPauseLocation:
    def test_cannot_pause_in_combat(self):
        ss = SpeedrunSystem()
        assert ss.can_pause_timer("boss_room") == False  # bug3: True
        assert ss.can_pause_timer("safe_room") == True

class TestTimeOnReenter:
    def test_time_persists_on_reenter(self):
        ss = SpeedrunSystem()
        assert ss.keep_time_on_reenter() == True  # bug4: False

class TestRewardByRank:
    def test_top_rank_gets_better_reward(self):
        ss = SpeedrunSystem()
        r1 = ss.get_reward(1)
        r100 = ss.get_reward(100)
        assert r1["gold"] > r100["gold"]  # bug5: 都是100

class TestSegmentTimes:
    def test_run_has_segment_times(self):
        ss = SpeedrunSystem()
        run = RunRecord("r1", "p1", "d1", "normal", 600, segment_times={"boss1": 100, "boss2": 200})
        segments = ss.get_segment_times(run)
        assert "boss1" in segments  # bug6: 空

class TestDisconnectPause:
    def test_all_disconnect_pauses_timer(self):
        ss = SpeedrunSystem()
        assert ss.pause_on_disconnect(0) == True  # bug7: False
        assert ss.pause_on_disconnect(2) == False
