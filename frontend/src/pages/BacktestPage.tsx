import { useEffect, useMemo } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { BacktestTable } from "../components/BacktestTable";
import { SummaryGrid } from "../components/SummaryGrid";
import { GradeBoard } from "../components/GradeBoard";
import { useBacktest } from "../hooks/useBacktest";
import type { BacktestResponse } from "../types/backtest";

export function BacktestPage() {
  const { btId } = useParams<{ btId: string }>();
  const location = useLocation();
  const stateData = location.state as BacktestResponse | undefined;
  const { backtest, isLoading, error, refresh } = useBacktest(btId);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [btId]);

  const data = useMemo(() => backtest ?? stateData, [backtest, stateData]);

  return (
    <div className="page backtest-page">
      <header className="backtest-header">
        <div>
          <p className="eyebrow">回测编号：{btId}</p>
          <h1>核心指标汇总</h1>
          <p className="muted">
            窗口 {data?.window.start ?? "--"} 至 {data?.window.end ?? "--"} · 基准 {data?.benchmark ?? "--"}
          </p>
        </div>
        <div className="backtest-actions">
          <Link to="/" className="ghost">
            返回默认页
          </Link>
          <button onClick={() => refresh()} disabled={isLoading}>
            刷新数据
          </button>
        </div>
      </header>

      {isLoading && <p className="muted">回测结果加载中...</p>}
      {error && <p className="error">{error.message}</p>}

      <div className="summary-wrapper">
        <SummaryGrid summary={data?.summary} />
        <GradeBoard items={data?.items} />
      </div>

      <section className="chart-section">
        <header>
          <h2>权益曲线</h2>
          <p className="muted">TODO：接入图表库（ECharts/Recharts），展示组合 vs 基准的归一化净值。</p>
        </header>
        <div className="chart-placeholder">敬请期待</div>
      </section>

      <section>
        <header>
          <h2>回测明细</h2>
          <p className="muted">支持导出 / 筛选将在 M2/M3 中实现</p>
        </header>
        <BacktestTable items={data?.items} />
      </section>

      <section className="disclosure">
        <h3>方法论披露</h3>
        <ul>
          <li>T+1 开盘价买入，E 日（默认当前日）收盘价卖出。</li>
          <li>收益、年化、Sharpe、最大回撤、Calmar 按 PRD 公式计算，交易日数按 244 天年化。</li>
          <li>基准默认沪深 300，可切换上证指数/中证 1000。</li>
          <li>数据源使用同花顺/AKShare，若存在停牌/ST/无法成交的情况将标注 flag。</li>
        </ul>
      </section>
    </div>
  );
}
