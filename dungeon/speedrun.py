"""副本计时与速通系统"""
from dataclasses import dataclass, field

# 允许暂停计时的安全点
SAFE_PAUSE_LOCATIONS = {"safe_room", "checkpoint", "camp"}
# 战斗中禁止暂停
COMBAT_LOCATIONS = {"boss_room", "combat_zone", "arena"}
# 暂停计时的事件（加载、过场动画）
PAUSE_EVENTS = {"loading", "cutscene"}
# 难度系数：越高难度系数越大，用于跨难度换算参考
DIFFICULTY_COEFFICIENTS = {"normal": 1.0, "hard": 1.5, "nightmare": 2.0}
# 中途重进次数上限
MAX_REENTER_COUNT = 3


@dataclass
class RunRecord:
    rid: str
    player: str
    dungeon: str
    difficulty: str
    total_time: float
    segment_times: dict = field(default_factory=dict)
    reenter_count: int = 0

    @property
    def weighted_time(self) -> float:
        """按难度系数换算后的时间，用于跨难度参考。"""
        coef = DIFFICULTY_COEFFICIENTS.get(self.difficulty, 1.0)
        return self.total_time / coef


class SpeedrunSystem:
    def __init__(self):
        self.records: list[RunRecord] = []
        self.timer_start: float = 0
        self.combat_started: bool = False
        self.timer_paused: bool = True  # 进本未触发战斗前计时未启动
        self.best_segments: dict = {}  # 每段历史最佳，用于分段对比

    # bug1: 计时从第一个战斗触发开始；加载/过场暂停计时
    def should_start_timer(self, event: str) -> bool:
        if event == "combat_start":
            self.combat_started = True
            self.timer_paused = False
            return True
        if event in PAUSE_EVENTS:
            self.timer_paused = True
            return False
        return False

    # bug2: 排名按难度分层，同难度内按时间排序
    def get_rank(self, record: RunRecord) -> int:
        same_tier = [r for r in self.records if r.difficulty == record.difficulty]
        if record not in same_tier:
            same_tier = list(self.records)
        sorted_records = sorted(same_tier, key=lambda r: r.total_time)
        return sorted_records.index(record) + 1

    # bug3: 只能在安全点暂停，战斗中不能暂停
    def can_pause_timer(self, location: str) -> bool:
        if location in COMBAT_LOCATIONS:
            return False
        return location in SAFE_PAUSE_LOCATIONS

    # bug4: 中途退出计时保留，重进继续累计，且有次数限制
    def keep_time_on_reenter(self) -> bool:
        return True

    def can_reenter(self, run: RunRecord) -> bool:
        return run.reenter_count < MAX_REENTER_COUNT

    # bug5: 奖励按排名阶梯发放，前10有特殊奖励
    def get_reward(self, rank: int) -> dict:
        if rank <= 0:
            rank = 1
        if rank == 1:
            return {"gold": 10000, "gems": 500, "title": "speed_demon", "special": "top10_skin"}
        if rank <= 3:
            return {"gold": 5000, "gems": 300, "special": "top10_skin"}
        if rank <= 10:
            return {"gold": 2000, "gems": 100, "special": "top10_skin"}
        if rank <= 50:
            return {"gold": 800, "gems": 30}
        if rank <= 100:
            return {"gold": 300, "gems": 10}
        return {"gold": 50}

    # bug6: 分段记录每个BOSS/区域时间，并对比历史最佳分段
    def get_segment_times(self, run: RunRecord) -> dict:
        return dict(run.segment_times)

    def compare_with_best(self, run: RunRecord) -> dict:
        """返回每段与历史最佳的差值（正数表示比最佳慢）。"""
        diff = {}
        for name, t in run.segment_times.items():
            best = self.best_segments.get(name)
            diff[name] = None if best is None else t - best
        return diff

    def record_run(self, run: RunRecord) -> None:
        self.records.append(run)
        for name, t in run.segment_times.items():
            if name not in self.best_segments or t < self.best_segments[name]:
                self.best_segments[name] = t

    # bug7: 团队计时按团队状态，全员掉线暂停，有人在线继续
    def pause_on_disconnect(self, online_count: int) -> bool:
        return online_count <= 0
