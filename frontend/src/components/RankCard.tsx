import type { RankResponse } from "../types/common";

interface Props {
  title: string;
  color: string;
  data?: RankResponse;
  isLoading?: boolean;
  error?: Error;
}

export function RankCard({ title, color, data, isLoading, error }: Props) {
  return (
    <section className="rank-card" style={{ borderColor: color }}>
      <header>
        <h3>{title}</h3>
        <span className="rank-meta">
          最近 {data?.days ?? "-"} 日 · Top {data?.limit ?? "-"}
        </span>
      </header>
      {isLoading && <p className="muted">加载中...</p>}
      {error && <p className="error">{error.message}</p>}
      {!isLoading && !error && (
        <ol>
          {(data?.items ?? []).map((item, idx) => (
            <li key={`${item.code}-${idx}`}>
              <span>
                {idx + 1}. {item.name}
              </span>
              {item.grade && <span className="tag">{item.grade}</span>}
            </li>
          ))}
          {(data?.items?.length ?? 0) === 0 && <li className="muted">暂无数据</li>}
        </ol>
      )}
    </section>
  );
}

