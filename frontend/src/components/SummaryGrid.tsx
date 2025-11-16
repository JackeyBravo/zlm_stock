import type { BacktestSummary } from "../types/backtest";

const STAT_KEYS: Array<{ key: keyof BacktestSummary; label: string; format?: (v?: number) => string }> = [
  { key: "win_rate", label: "胜率统计", format: formatPercent },
  { key: "mdd", label: "最大回撤", format: formatPercent },
  { key: "ret", label: "回测收益", format: formatPercent },
  { key: "ann", label: "回测年化", format: formatPercent },
  { key: "bench_ret", label: "大盘收益", format: formatPercent },
  { key: "bench_ann", label: "大盘年化", format: formatPercent },
  { key: "sharpe", label: "Sharpe" },
  { key: "calmar", label: "Calmar" },
];

interface Props {
  summary?: BacktestSummary;
}

export function SummaryGrid({ summary }: Props) {
  return (
    <div className="summary-grid">
      {STAT_KEYS.map(({ key, label, format }) => (
        <div key={key} className="summary-card">
          <span>{label}</span>
          <strong>{format ? format(summary?.[key] as number) : formatNumber(summary?.[key] as number)}</strong>
        </div>
      ))}
    </div>
  );
}

function formatPercent(value?: number) {
  if (value === undefined || Number.isNaN(value)) return "--";
  return `${(value * 100).toFixed(1)}%`;
}

function formatNumber(value?: number) {
  if (value === undefined || Number.isNaN(value)) return "--";
  return value.toFixed(2);
}
