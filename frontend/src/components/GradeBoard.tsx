import type { BacktestItem } from "../types/backtest";

const GRADE_ORDER: Array<{ label: string; value: string; color: string }> = [
  { label: "夯", value: "秀", color: "#ef4444" },
  { label: "顶级", value: "顶级", color: "#fbbf24" },
  { label: "人上人", value: "人上人", color: "#facc15" },
  { label: "NPC", value: "NPC", color: "#e2e8f0" },
  { label: "拉完了", value: "拉完了", color: "#cbd5f5" },
];

interface Props {
  items?: BacktestItem[];
}

export function GradeBoard({ items }: Props) {
  return (
    <div className="grade-board">
      <h3>回测评级</h3>
      <div className="grade-table">
        {GRADE_ORDER.map((grade) => {
          const matched = (items ?? []).filter((item) => item.grade === grade.value);
          return (
            <div key={grade.value} className="grade-row" style={{ backgroundColor: grade.color }}>
              <span className="grade-label">{grade.label}</span>
              <div className="grade-stocks">{matched.length > 0 ? matched.map((item) => item.name || item.code).join("、") : "暂无股票"}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
