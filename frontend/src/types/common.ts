export interface RankItem {
  code: string;
  name: string;
  score?: number;
  grade?: string;
  reason?: string;
}

export interface RankResponse {
  type: "hot" | "best" | "worst";
  days: number;
  k?: number;
  limit: number;
  items: RankItem[];
}

export interface QuotaResponse {
  guest_remaining: number;
  login_remaining: number;
}

export interface RandomPickResponse {
  code: string;
  name: string;
  grade?: string;
  bt_id?: string;
}

