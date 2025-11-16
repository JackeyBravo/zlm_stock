import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { RankCard } from "../components/RankCard";
import { createBacktest } from "../hooks/useBacktest";
import { useQuota } from "../hooks/useQuota";
import { useRandomPick } from "../hooks/useRandomPick";
import { useRank } from "../hooks/useRanks";

const BENCHMARKS = [
  { label: "沪深300", value: "HS300" },
  { label: "上证指数", value: "SSE" },
  { label: "中证1000", value: "CSI1000" },
];

export function LandingPage() {
  const navigate = useNavigate();
  const [stocksInput, setStocksInput] = useState("");
  const [recommendDate, setRecommendDate] = useState(defaultRecommendDate());
  const [benchmark, setBenchmark] = useState("HS300");
  const [submitting, setSubmitting] = useState(false);

  const { quota, isLoading: quotaLoading } = useQuota();
  const { randomPick, isLoading: randomLoading, error: randomError, fetchRandom } = useRandomPick();
  const hotRank = useRank("hot");
  const bestRank = useRank("best");
  const worstRank = useRank("worst");

  const parsedStocks = useMemo(
    () =>
      stocksInput
        .split(/[\s,，；;]+/)
        .map((item) => item.trim())
        .filter(Boolean),
    [stocksInput],
  );

  const handleSubmit = async () => {
    if (parsedStocks.length === 0) {
      alert("请至少输入一只股票或代码");
      return;
    }
    setSubmitting(true);
    try {
      const payload = {
        stocks: parsedStocks,
        recommend_date: recommendDate,
        end_date: null,
        benchmark,
        price_adjust: "post",
      };
      const result = await createBacktest(payload);
      navigate(`/backtest/${result.bt_id}`, { state: result });
    } catch (error) {
      alert((error as Error).message);
    } finally {
      setSubmitting(false);
    }
  };

  const quotaText = quotaLoading ? "配额查询中..." : `游客剩余 ${quota?.guest_remaining ?? "-"} / 登录剩余 ${quota?.login_remaining ?? "-"}`;

  return (
    <div className="page landing-page">
      <header className="app-header">
        <div className="brand-block">
          <span className="brand-title">准了么</span>
          <span className="brand-tagline">快速验证推荐是否靠谱的工具</span>
        </div>
        <span className="quota-chip">{quotaText}</span>
      </header>

      <div className="landing-layout">
        <section className="panel form-panel">
          <div className="panel-title">
            <h2>回测配置</h2>
            <p className="muted">默认以推荐日次日开盘价买入，可批量粘贴股票名称或代码</p>
          </div>
          <label className="field">
            <span>回测股票（空格/逗号/换行分割）</span>
            <textarea value={stocksInput} onChange={(e) => setStocksInput(e.target.value)} placeholder="例如：平安银行 601318 万科A 000002" />
            <small className="muted">已输入 {parsedStocks.length} 只股票</small>
          </label>
          <div className="form-row">
            <label className="field">
              <span>推荐日期</span>
              <input type="date" value={recommendDate} onChange={(e) => setRecommendDate(e.target.value)} />
            </label>
            <label className="field">
              <span>基准指数</span>
              <select value={benchmark} onChange={(e) => setBenchmark(e.target.value)}>
                {BENCHMARKS.map((item) => (
                  <option key={item.value} value={item.value}>
                    {item.label}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <div className="panel-actions">
            <button onClick={handleSubmit} disabled={submitting}>
              {submitting ? "回测中..." : "开始回测"}
            </button>
            <button type="button" className="ghost" onClick={fetchRandom} disabled={randomLoading}>
              试试手气（随机股票）
            </button>
          </div>
          {randomPick && (
            <div className="random-card">
              <div>
                <strong>
                  随机推荐：{randomPick.name} ({randomPick.code})
                </strong>
                <p className="muted">可直接复制填入输入框快速回测</p>
              </div>
              {randomPick.grade && <span className="tag">{randomPick.grade}</span>}
            </div>
          )}
          {randomError && <p className="error">{randomError}</p>}
        </section>

        <section className="rank-columns">
          <RankCard title="近10日热门回测" color="#1d4ed8" data={hotRank.data} isLoading={hotRank.isLoading} error={hotRank.error as Error | undefined} />
          <RankCard title="近10日最夯回测" color="#d97706" data={bestRank.data} isLoading={bestRank.isLoading} error={bestRank.error as Error | undefined} />
          <RankCard title="近10日最拉回测" color="#dc2626" data={worstRank.data} isLoading={worstRank.isLoading} error={worstRank.error as Error | undefined} />
        </section>
      </div>
    </div>
  );
}

function defaultRecommendDate() {
  const date = new Date();
  date.setDate(date.getDate() - 7);
  return date.toISOString().slice(0, 10);
}
