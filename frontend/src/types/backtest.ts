export interface BacktestWindow {
  start: string | null;
  end: string | null;
  trading_days: number;
}

export interface BacktestSummary {
  win_rate?: number;
  ret?: number;
  ann?: number;
  bench_ret?: number;
  bench_ann?: number;
  excess?: number;
  sharpe?: number;
  mdd?: number;
  calmar?: number;
  grade?: string;
}

export interface BacktestItem {
  code: string;
  name: string;
  buy_date: string;
  buy_price?: number;
  sell_date?: string;
  sell_price?: number;
  ret?: number;
  excess?: number;
  ann?: number;
  sharpe?: number;
  mdd?: number;
  calmar?: number;
  score?: number;
  grade?: string;
  flags?: string[];
}

export interface ItemEquityPoint {
  date: string;
  ret: number;
}

export interface ItemEquitySeries {
  code: string;
  name: string;
  points: ItemEquityPoint[];
}

export interface BacktestResponse {
  bt_id: string;
  window: BacktestWindow;
  benchmark: string;
  summary: BacktestSummary;
  equity: Array<{ date: string; portfolio_nv: number; bench_nv: number }>;
  item_equities: ItemEquitySeries[];
  items: BacktestItem[];
}
