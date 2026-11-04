"""
Linux 计划任务索引校正桩代码 (schedule_index_sync)
Linux 环境下计划任务统一由外部 systemd/cron 管理，无需校正 Windows 任务计划 COM/XML。
保留接口定义以保持对上层调用（MainWindow、ScheduleTaskTab）的契约兼容。
"""

from typing import Optional, Sequence


def reset_sync_guard():
    pass


def resolve_current_schedule_task():
    pass


def sync_schedule_task_indexes(onetime_tasks: Optional[Sequence] = None, *, rewrite_argv=True) -> int:
    return 0
