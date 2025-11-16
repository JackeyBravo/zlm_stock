import { useMemo } from "react";
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ItemEquitySeries } from "../types/backtest";

interface Props {
  series?: ItemEquitySeries[];
}

const COLORS = ["#ef4444", "#2563eb", "#f59e0b", "#0ea5e9", "#14b8a6", "#a855f7", "#f97316", "#10b981"];

export function EquityChart({ series }: Props) {
  const validSeries = useMemo(() => (series ?? []).filter((item) => item.points?.length), [series]);

  const data = useMemo(() => {
    const map = new Map<string, Record<string, number | string>>();
    for (const line of validSeries) {
      for (const point of line.points) {
        const dateKey = point.date;
        if (!map.has(dateKey)) {
          map.set(dateKey, { date: dateKey });
        }
        const entry = map.get(dateKey)!;
        entry[line.code] = Number((point.ret * 100).toFixed(2));
      }
    }
    return Array.from(map.values()).sort((a, b) => String(a.date).localeCompare(String(b.date)));
  }, [validSeries]);

  const nameMap = useMemo(() => {
    const mapping: Record<string, string> = {};
    for (const item of validSeries) {
      mapping[item.code] = item.name || item.code;
    }
    return mapping;
  }, [validSeries]);

  if (!validSeries.length || data.length === 0) {
    return <div className="chart-placeholder">暂无权益数据</div>;
  }

  return (
    <div className="equity-chart">
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data} margin={{ left: 8, right: 24, top: 8, bottom: 0 }}>
          <CartesianGrid stroke="#e2e8f0" vertical={false} />
          <XAxis dataKey="date" tickFormatter={formatDate} />
          <YAxis tickFormatter={(value) => `${value.toFixed(0)}%`} width={60} />
          <Tooltip content={<EquityTooltip nameMap={nameMap} />} />
          <Legend />
          {validSeries.map((line, idx) => (
            <Line
              key={line.code}
              type="monotone"
              dataKey={line.code}
              name={line.name || line.code}
              stroke={COLORS[idx % COLORS.length]}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

function formatPercent(value?: number) {
  if (value === undefined || Number.isNaN(value)) return "--";
  return `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;
}

function formatDate(value?: string | number) {
  if (!value) return "";
  const text = String(value);
  return text.slice(5);
}

interface TooltipEntry {
  color?: string;
  dataKey?: string | number;
  value?: number | string;
  name?: string;
}

function EquityTooltip({
  active,
  payload,
  label,
  nameMap,
}: {
  active?: boolean;
  payload?: TooltipEntry[];
  label?: string;
  nameMap: Record<string, string>;
}) {
  if (!active || !payload || payload.length === 0) return null;
  return (
    <div className="chart-tooltip">
      <strong>{label}</strong>
      <ul>
        {payload.map((entry) => (
          <li key={entry.dataKey as string} style={{ color: entry.color || "#111" }}>
            {nameMap[String(entry.dataKey)] ?? entry.name}: {formatPercent(entry.value as number)}
          </li>
        ))}
      </ul>
    </div>
  );
}
