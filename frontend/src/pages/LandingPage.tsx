import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createBacktest } from "../hooks/useBacktest";
import { useQuota } from "../hooks/useQuota";
import { useRandomPick } from "../hooks/useRandomPick";
import { useRank } from "../hooks/useRanks";
import { RankCard } from "../components/RankCard";

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
      <section className="hero">
        <div>
          <p className="eyebrow">准了么 · 快速验证推荐是否靠谱的工具</p>
          <h1>输入股票 & 推荐日期，一键回测推荐的真伪</h1>
          <p className="muted">默认以推荐日次日开盘买入，支持多股票批量验证，并提供近 10 日热门/优质/拉胯榜单。</p>
          <p className="quota">{quotaText}</p>
        </div>
      </section>

      <div className="landing-main">
        <section className="form-section narrow">
          <label>
            回测股票（名称或代码，空格/逗号/换行分割）
            <textarea
              value={stocksInput}
              onChange={(e) => setStocksInput(e.target.value)}
              placeholder="例如：平安银行 601318 000001"
            />
            <small>已输入 {parsedStocks.length} 只股票</small>
          </label>
          <div className="form-row">
            <label>
              推荐日期（默认当前日期前 5 个交易日）
              <input type="date" value={recommendDate} onChange={(e) => setRecommendDate(e.target.value)} />
            </label>
            <label>
              对标指数
              <select value={benchmark} onChange={(e) => setBenchmark(e.target.value)}>
                {BENCHMARKS.map((item) => (
                  <option key={item.value} value={item.value}>
                    {item.label}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <div className="actions">
            <button onClick={handleSubmit} disabled={submitting}>
              {submitting ? "回测中..." : "开始回测"}
            </button>
            <button type="button" className="ghost" onClick={fetchRandom} disabled={randomLoading}>
              试试手气（随机股票）
            </button>
          </div>
          {randomPick && (
            <div className="random-card">
              <strong>
                随机推荐：{randomPick.name} ({randomPick.code})
              </strong>
              {randomPick.grade && <span className="tag">{randomPick.grade}</span>}
            </div>
          )}
          {randomError && <p className="error">{randomError}</p>}
        </section>

        <section className="rank-stack">
          <RankCard title="近10日热门回测" color="#2563eb" data={hotRank.data} isLoading={hotRank.isLoading} error={hotRank.error as Error | undefined} />
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
