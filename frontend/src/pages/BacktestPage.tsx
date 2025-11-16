import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { BacktestTable } from "../components/BacktestTable";
import { EquityChart } from "../components/EquityChart";
import { GradeBoard } from "../components/GradeBoard";
import { SummaryGrid } from "../components/SummaryGrid";
import { useBacktest } from "../hooks/useBacktest";
import type { BacktestResponse } from "../types/backtest";

export function BacktestPage() {
  const { btId } = useParams<{ btId: string }>();
  const location = useLocation();
  const stateData = location.state as BacktestResponse | undefined;
  const { backtest, isLoading, error, refresh } = useBacktest(btId);
  const [selectedCodes, setSelectedCodes] = useState<string[]>([]);
  const [onlySelected, setOnlySelected] = useState(false);
  const initializedRef = useRef(false);
  const data = useMemo(() => backtest ?? stateData, [backtest, stateData]);

  useEffect(() => {
    initializedRef.current = false;
    setSelectedCodes([]);
    setOnlySelected(false);
  }, [btId]);

  useEffect(() => {
    if (!initializedRef.current && data?.items?.length) {
      setSelectedCodes(data.items.map((item) => item.code));
      setOnlySelected(true);
      initializedRef.current = true;
    }
  }, [data]);

  useEffect(() => {
    if (selectedCodes.length === 0 && onlySelected) {
      setOnlySelected(false);
    }
  }, [selectedCodes, onlySelected]);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [btId]);
  const selectedSet = useMemo(() => new Set(selectedCodes), [selectedCodes]);

  const filteredSeries = useMemo(() => {
    if (!data?.item_equities) return [];
    if (onlySelected && selectedSet.size > 0) {
      return data.item_equities.filter((item) => selectedSet.has(item.code));
    }
    return data.item_equities;
  }, [data?.item_equities, onlySelected, selectedSet]);

  const filteredItems = useMemo(() => {
    if (!data?.items) return [];
    if (onlySelected && selectedSet.size > 0) {
      return data.items.filter((item) => selectedSet.has(item.code));
    }
    return data.items;
  }, [data?.items, onlySelected, selectedSet]);

  const handleToggleCode = (code: string) => {
    setSelectedCodes((prev) => (prev.includes(code) ? prev.filter((item) => item !== code) : [...prev, code]));
  };

  const allCodes = useMemo(() => (data?.items ?? []).map((item) => item.code), [data?.items]);
  const isAllSelected = allCodes.length > 0 && selectedCodes.length === allCodes.length;

  const handleToggleAll = () => {
    if (isAllSelected) {
      setSelectedCodes([]);
      setOnlySelected(false);
    } else {
      setSelectedCodes(allCodes);
      setOnlySelected(true);
    }
  };

  const canFilter = selectedCodes.length > 0;

  return (
    <div className="page backtest-page">
      <header className="backtest-header">
        <div className="brand-block">
          <span className="brand-title">准了么 · 回测详情</span>
          <span className="muted">回测编号：{btId}</span>
        </div>
        <div className="backtest-actions">
          <Link to="/" className="ghost button-link">
            返回默认页
          </Link>
          <button onClick={() => refresh()} disabled={isLoading}>
            刷新数据
          </button>
        </div>
      </header>

      {isLoading && <p className="muted status-text">回测结果加载中...</p>}
      {error && <p className="error status-text">{error.message}</p>}

      <div className="meta-panel">
        <div className="meta-item">
          <p className="muted">回测窗口</p>
          <strong>
            {data?.window.start ?? "--"} 至 {data?.window.end ?? "--"}
          </strong>
        </div>
        <div className="meta-item">
          <p className="muted">基准指数</p>
          <strong>{data?.benchmark ?? "--"}</strong>
        </div>
        <div className="meta-item">
          <p className="muted">股票数量</p>
          <strong>{data?.items?.length ?? "--"}</strong>
        </div>
      </div>

      <div className="summary-board">
        <SummaryGrid summary={data?.summary} />
        <GradeBoard items={data?.items} />
      </div>

      <section className="filter-panel">
        <header>
          <div>
            <h3>股票筛选</h3>
            <p className="muted">勾选想对比的股票，再启用开关即可只看被筛选的结果</p>
          </div>
          <div className="filter-actions">
            <button type="button" className="chip-button" onClick={handleToggleAll} disabled={allCodes.length === 0}>
              {isAllSelected ? "全不选" : "全选"}
            </button>
            <label className="filter-toggle">
              <input type="checkbox" checked={onlySelected && canFilter} disabled={!canFilter} onChange={(e) => setOnlySelected(e.target.checked)} />
              <span>仅显示已勾选</span>
            </label>
          </div>
        </header>
        <div className="filter-list">
          {(data?.items ?? []).map((item) => (
            <label key={item.code} className="filter-chip">
              <input type="checkbox" checked={selectedSet.has(item.code)} onChange={() => handleToggleCode(item.code)} />
              <span>
                {item.name} ({item.code})
              </span>
            </label>
          ))}
          {(data?.items?.length ?? 0) === 0 && <p className="muted">暂无回测股票</p>}
        </div>
      </section>

      <section className="chart-box">
        <header>
          <h2>权益曲线</h2>
          <p className="muted">每只股票的收益曲线，悬停可查看当日收益</p>
        </header>
        <EquityChart series={filteredSeries} />
      </section>

      <section className="table-section">
        <header>
          <h2>回测明细</h2>
          <p className="muted">导出与筛选功能将在 M2/M3 迭代</p>
        </header>
        <BacktestTable items={filteredItems} />
      </section>

      <section className="disclosure-panel">
        <h3>方法论披露</h3>
        <ul>
          <li>T+1 开盘价买入，结束日（默认当前交易日）收盘价卖出。</li>
          <li>收益、年化、Sharpe、最大回撤、Calmar 等指标按 PRD 约定计算，交易日按 244 天年化。</li>
          <li>基准默认沪深 300，可在回测时切换上证指数或中证 1000。</li>
          <li>数据源使用同花顺/AKShare，停牌、ST 或异常数据会在明细中标注 flag。</li>
        </ul>
      </section>
    </div>
  );
}
