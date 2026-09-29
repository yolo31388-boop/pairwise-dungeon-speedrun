"""副本计时与速通系统 - 含7个bug"""
from dataclasses import dataclass, field

@dataclass
class RunRecord:
    rid: str
    player: str
    dungeon: str
    difficulty: str
    total_time: float
    segment_times: dict = field(default_factory=dict)  # bug6: 无分段

class SpeedrunSystem:
    def __init__(self):
        self.records: list[RunRecord] = []
        self.timer_start: float = 0
        self.combat_started: bool = False  # bug1: 进本就计时

    def should_start_timer(self, event: str) -> bool:
        # bug1: 进本就开始
        return True

    def get_rank(self, record: RunRecord) -> int:
        # bug2: 不看难度
        sorted_records = sorted(self.records, key=lambda r: r.total_time)
        return sorted_records.index(record) + 1

    def can_pause_timer(self, location: str) -> bool:
        # bug3: 到处能暂停
        return True

    def keep_time_on_reenter(self) -> bool:
        # bug4: 重进重置
        return False

    def get_reward(self, rank: int) -> dict:
        # bug5: 固定奖励
        return {"gold": 100}

    def get_segment_times(self, run: RunRecord) -> dict:
        # bug6: 无分段
        return {}

    def pause_on_disconnect(self, online_count: int) -> bool:
        # bug7: 掉线不暂停
        return False
