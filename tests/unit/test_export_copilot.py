from __future__ import annotations

import json

from scripts.export_copilot import export_copilot


def test_export_writes_static_payload_and_weekly_briefing(tmp_path) -> None:
    payload_path = tmp_path / "public" / "growth-analytics.json"
    weekly_path = tmp_path / "output" / "weekly-briefing.md"
    sample_weekly_path = tmp_path / "docs" / "sample-weekly-briefing.md"
    result = export_copilot(
        payload_path=payload_path,
        weekly_path=weekly_path,
        sample_weekly_path=sample_weekly_path,
    )
    assert result == {
        "payload": payload_path,
        "weekly": weekly_path,
        "sample_weekly": sample_weekly_path,
    }
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    weekly = weekly_path.read_text(encoding="utf-8")
    sample_weekly = sample_weekly_path.read_text(encoding="utf-8")
    assert "evals" not in payload
    assert "老带新增长决策周报" in weekly
    assert "新用户留存诊断周报" in weekly
    assert "无法准确量化结构贡献" in weekly
    assert sample_weekly == weekly
    assert weekly.startswith("# 刘希｜增长分析与实验决策作品集 · 自动周报示例")
