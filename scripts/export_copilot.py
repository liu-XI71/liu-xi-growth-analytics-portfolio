from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from analytics.copilot import build_copilot_payload

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAYLOAD_PATH = PROJECT_ROOT / "web" / "public" / "data" / "growth-analytics.json"
DEFAULT_WEEKLY_PATH = PROJECT_ROOT / "output" / "weekly-briefing.md"
DEFAULT_SAMPLE_WEEKLY_PATH = PROJECT_ROOT / "docs" / "sample-weekly-briefing.md"


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f"{path.suffix}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def _render_weekly_briefing(payload: dict[str, Any]) -> str:
    meta = payload["meta"]
    lines = [
        "# 刘希｜增长与实验 · 自动周报示例",
        "",
        f"- 快照：`{meta['snapshot_id']}`",
        f"- 生成时间：`{meta['generated_at']}`",
        f"- 叙事模式：`{meta['narrative_mode']}`",
        f"- 数据边界：{meta['data_boundary']}",
        f"- 计算边界：{meta['calculation_boundary']}",
        "",
    ]
    for report in payload["weekly_reports"]:
        lines.extend(
            [
                f"## {report['title']}",
                "",
                f"- 当前：{report['period']}",
                f"- 对比：{report['previous_period']}",
                f"- 边界：{report['data_boundary']}",
                "",
                f"**一句话结论：** {report['headline']}",
                "",
                report["narrative"]["text"],
                "",
                "### 核心指标",
                "",
            ]
        )
        lines.extend(f"- {item['metric_id']}：{item['display']}" for item in report["kpis"])
        for title, key in (
            ("异常", "anomalies"),
            ("负证据", "negative_evidence"),
            ("待验证假设", "hypotheses"),
            ("建议动作", "recommendations"),
            ("结论边界", "limitations"),
        ):
            lines.extend(["", f"### {title}", ""])
            lines.extend(f"- {item}" for item in report[key])
        lines.extend(
            [
                "",
                f"**实验状态：** {report['experiment_status']}",
                "",
                f"**证据编号：** {', '.join(report['evidence_ids'])}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def export_copilot(
    *,
    payload_path: Path = DEFAULT_PAYLOAD_PATH,
    weekly_path: Path = DEFAULT_WEEKLY_PATH,
    sample_weekly_path: Path = DEFAULT_SAMPLE_WEEKLY_PATH,
    narrative_mode: str = "deterministic",
    ollama_base_url: str = "http://127.0.0.1:11434",
    ollama_model: str = "qwen2.5:7b",
    ollama_timeout_seconds: float = 8.0,
) -> dict[str, Path]:
    payload = build_copilot_payload(
        narrative_mode=narrative_mode,
        ollama_base_url=ollama_base_url,
        ollama_model=ollama_model,
        ollama_timeout_seconds=ollama_timeout_seconds,
    )
    weekly_content = _render_weekly_briefing(payload)
    _write_text(payload_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    _write_text(weekly_path, weekly_content)
    _write_text(sample_weekly_path, weekly_content)
    return {
        "payload": payload_path,
        "weekly": weekly_path,
        "sample_weekly": sample_weekly_path,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export deterministic growth analytics artifacts")
    parser.add_argument("--payload-path", type=Path, default=DEFAULT_PAYLOAD_PATH)
    parser.add_argument("--weekly-path", type=Path, default=DEFAULT_WEEKLY_PATH)
    parser.add_argument("--sample-weekly-path", type=Path, default=DEFAULT_SAMPLE_WEEKLY_PATH)
    parser.add_argument(
        "--narrative-mode",
        choices=["deterministic", "ollama"],
        default="deterministic",
    )
    parser.add_argument("--ollama-base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--ollama-model", default="qwen2.5:7b")
    parser.add_argument("--ollama-timeout-seconds", type=float, default=8.0)
    args = parser.parse_args()
    try:
        paths = export_copilot(
            payload_path=args.payload_path,
            weekly_path=args.weekly_path,
            sample_weekly_path=args.sample_weekly_path,
            narrative_mode=args.narrative_mode,
            ollama_base_url=args.ollama_base_url,
            ollama_model=args.ollama_model,
            ollama_timeout_seconds=args.ollama_timeout_seconds,
        )
    except Exception as error:
        print(f"Growth analytics export failed: {error}", file=sys.stderr)
        return 1
    for name, path in paths.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
