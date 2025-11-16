import type { BacktestItem } from "../types/backtest";

interface Props {
  items?: BacktestItem[];
}

export function BacktestTable({ items }: Props) {
  return (
    <div className="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>代码</th>
            <th>名称</th>
            <th>买入日</th>
            <th>卖出日</th>
            <th>收益</th>
            <th>超额</th>
            <th>年化</th>
            <th>Sharpe</th>
            <th>MDD</th>
            <th>Calmar</th>
            <th>评级</th>
            <th>Flags</th>
          </tr>
        </thead>
        <tbody>
          {(items ?? []).map((item) => (
            <tr key={`${item.code}-${item.buy_date}`}>
              <td>{item.code}</td>
              <td>{item.name}</td>
              <td>{item.buy_date}</td>
              <td>{item.sell_date ?? "--"}</td>
              <td>{formatPercent(item.ret)}</td>
              <td>{formatPercent(item.excess)}</td>
              <td>{formatPercent(item.ann)}</td>
              <td>{formatNumber(item.sharpe)}</td>
              <td>{formatPercent(item.mdd)}</td>
              <td>{formatNumber(item.calmar)}</td>
              <td>{item.grade ?? "--"}</td>
              <td>{item.flags?.join(", ") ?? "--"}</td>
            </tr>
          ))}
          {(items?.length ?? 0) === 0 && (
            <tr>
              <td colSpan={12} className="muted">
                暂无回测明细
              </td>
            </tr>
          )}
        </tbody>
      </table>
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

