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
    <section className="rank-card" style={{ borderColor: color, boxShadow: `6px 6px 0 ${hexToRgba(color)}` }}>
      <header>
        <h3>{title}</h3>
        <span className="muted">最近 {data?.days ?? "-"} 日 · Top {data?.limit ?? "-"}</span>
      </header>
      {isLoading && <p className="muted status-text">加载中...</p>}
      {error && <p className="error status-text">{error.message}</p>}
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

function hexToRgba(hex: string) {
  const normalized = hex.replace("#", "");
  const bigint = parseInt(normalized, 16);
  const r = (bigint >> 16) & 255;
  const g = (bigint >> 8) & 255;
  const b = bigint & 255;
  return `rgba(${r}, ${g}, ${b}, 0.15)`;
}
