"""副本计时与速通系统"""
from dataclasses import dataclass, field

# 难度系数：用于跨难度对比时的归一化（排名本身按难度分层）
DIFFICULTY_COEFFICIENT = {"normal": 1.0, "hard": 1.5, "nightmare": 2.0}

# 允许暂停计时的安全点
SAFE_PAUSE_LOCATIONS = {"safe_room", "checkpoint", "camp"}

# 中途退出重进的最大次数
MAX_REENTER_COUNT = 3


@dataclass
class RunRecord:
    rid: str
    player: str
    dungeon: str
    difficulty: str
    total_time: float
    segment_times: dict = field(default_factory=dict)  # 各BOSS/区域的分段时间
    best_segments: dict = field(default_factory=dict)  # 历史最佳分段，用于对比


class SpeedrunSystem:
    def __init__(self):
        self.records: list[RunRecord] = []
        self.timer_start: float = 0
        self.combat_started: bool = False
        self.paused: bool = False
        self.reenter_count: int = 0

    # bug1: 计时从第一个战斗触发开始；加载/过场不计时
    def should_start_timer(self, event: str) -> bool:
        if event == "combat_start":
            self.combat_started = True
            return True
        # enter_dungeon / loading / cutscene 均不启动计时
        return False

    # bug2: 排名按难度分层，不同难度分开排名
    def get_rank(self, record: RunRecord) -> int:
        same_tier = [r for r in self.records if r.difficulty == record.difficulty]
        same_tier.sort(key=lambda r: r.total_time)
        return same_tier.index(record) + 1

    def normalized_time(self, record: RunRecord) -> float:
        """难度系数归一化时间，用于跨难度参考对比。"""
        coef = DIFFICULTY_COEFFICIENT.get(record.difficulty, 1.0)
        return record.total_time / coef

    # bug3: 只能在安全点暂停，战斗中（如boss房）不能暂停
    def can_pause_timer(self, location: str) -> bool:
        return location in SAFE_PAUSE_LOCATIONS

    # bug4: 中途退出计时保留，重进继续累计，且有次数限制
    def keep_time_on_reenter(self) -> bool:
        return True

    def can_reenter(self) -> bool:
        return self.reenter_count < MAX_REENTER_COUNT

    def reenter(self) -> bool:
        if not self.can_reenter():
            return False
        self.reenter_count += 1
        return True

    # bug5: 奖励按排名阶梯发放，前10有特殊奖励
    def get_reward(self, rank: int) -> dict:
        if rank <= 0:
            raise ValueError("rank must be positive")
        if rank == 1:
            return {"gold": 10000, "gems": 500, "title": "speed_demon", "special": "unique_mount"}
        if rank <= 3:
            return {"gold": 5000, "gems": 300, "title": "speedster", "special": "rare_skin"}
        if rank <= 10:
            return {"gold": 2000, "gems": 100, "special": "top10_badge"}
        if rank <= 50:
            return {"gold": 800, "gems": 30}
        if rank <= 100:
            return {"gold": 300, "gems": 10}
        return {"gold": 100}

    # bug6: 分段记录每个BOSS/区域的时间，可对比最佳分段
    def get_segment_times(self, run: RunRecord) -> dict:
        return dict(run.segment_times)

    def compare_with_best(self, run: RunRecord) -> dict:
        """返回每个分段与最佳分段的差值（正数表示慢了）。"""
        return {
            name: run.segment_times.get(name, 0) - best
            for name, best in run.best_segments.items()
        }

    # bug7: 团队计时按团队状态，全员掉线暂停，有人在线继续
    def pause_on_disconnect(self, online_count: int) -> bool:
        return online_count <= 0
