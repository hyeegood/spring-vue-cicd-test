// 개발 시 같은 PC에서 백엔드(8000)로 직접 요청 (프록시 불필요, CORS 허용됨)
const API_BASE = import.meta.env.VITE_API_BASE || (typeof window !== 'undefined' && /^51[2-9]\d$/.test(window.location.port) ? 'http://localhost:8000' : '');

/** 대시보드 단일 API (통합). minimal=true면 DB만 반환해 첫 렌더 빠르게 */
export async function getDashboard(opts = {}) {
  const { minimal = false } = opts;
  const url = `${API_BASE}/api/dashboard${minimal ? '?minimal=1' : ''}`;
  const r = await fetch(url).catch((e) => {
    throw new Error('백엔드( http://localhost:8000 )에 연결할 수 없습니다. 백엔드를 실행한 뒤 새로고침하세요.');
  });
  const json = await r.json().catch(() => ({}));
  if (!r.ok) {
    let msg = '대시보드 요청 실패';
    if (typeof json?.detail === 'string') msg = json.detail;
    else if (Array.isArray(json?.detail) && json.detail[0]?.msg) msg = json.detail[0].msg;
    else if (json?.error) msg = json.error;
    throw new Error(msg);
  }
  if (Array.isArray(json)) return { items: json, last_refresh_at: null };
  return { items: json.items || [], last_refresh_at: json.last_refresh_at ?? null };
}

/** 빠른 첫 화면용: DB만 (외부 API 보정 없음). 이후 getDashboard()로 풀 데이터 갱신 시 Promise.all 가능 */
export async function getDashboardMinimal() {
  return getDashboard({ minimal: true });
}

export async function refreshFull() {
  const r = await fetch(`${API_BASE}/api/refresh/full`, { method: 'POST' });
  const json = await r.json().catch(() => ({}));
  if (r.status === 429) throw new Error('이미 새로고침이 진행 중입니다.');
  if (!r.ok) throw new Error(json.detail || '새로고침 요청 실패');
  return json;
}

export async function getRefreshStatus() {
  const r = await fetch(`${API_BASE}/api/refresh/status`);
  if (!r.ok) return { running: false, last_completed_at: null };
  return r.json();
}

export async function refreshStock(ticker) {
  const r = await fetch(`${API_BASE}/api/refresh/stock/${encodeURIComponent(ticker)}`, { method: 'POST' });
  const json = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(json.detail || '새로고침 실패');
  return json;
}

/** Wikipedia API로 한글 회사명 조회 후 DB 저장 */
export async function refreshKoreanNames() {
  const r = await fetch(`${API_BASE}/api/refresh-korean-names`, { method: 'POST' });
  const json = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(json.detail || '한글명 가져오기 실패');
  return json;
}

export async function getStockDetail(ticker) {
  const r = await fetch(`${API_BASE}/api/stocks/${encodeURIComponent(ticker)}`);
  const json = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(json.detail || json.error || 'Stock not found');
  return json;
}

export async function getRankings(listType, limit = 50) {
  const r = await fetch(`${API_BASE}/api/rankings/${listType}?limit=${limit}`);
  if (!r.ok) throw new Error('Rankings failed');
  return r.json();
}

export async function getPortfolios() {
  const r = await fetch(`${API_BASE}/api/portfolios`);
  if (!r.ok) throw new Error('List failed');
  return r.json();
}

export async function getPortfolio(id) {
  const r = await fetch(`${API_BASE}/api/portfolio/${id}`);
  if (!r.ok) throw new Error('Portfolio failed');
  return r.json();
}

export async function createPortfolio(name, userId = 'default') {
  const r = await fetch(`${API_BASE}/api/portfolio`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, user_id: userId }),
  });
  if (!r.ok) throw new Error('Create failed');
  return r.json();
}

export async function addPosition(portfolioId, stockId, shares) {
  const r = await fetch(`${API_BASE}/api/portfolio/${portfolioId}/positions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ stock_id: stockId, shares }),
  });
  if (!r.ok) throw new Error('Add position failed');
  return r.json();
}

export async function runBacktest(tickers, startDate, endDate, entryRule = 'ma20') {
  const r = await fetch(`${API_BASE}/api/backtest`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tickers, start_date: startDate, end_date: endDate, entry_rule: entryRule }),
  });
  if (!r.ok) throw new Error('Backtest failed');
  return r.json();
}

export async function registerStock(ticker) {
  const r = await fetch(`${API_BASE}/api/stocks/register?ticker=${encodeURIComponent(ticker)}`, { method: 'POST' });
  if (!r.ok) throw new Error('Register failed');
  return r.json();
}
