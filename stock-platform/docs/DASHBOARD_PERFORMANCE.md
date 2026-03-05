# 대시보드 성능 개선 요약

## 1. FastAPI 대시보드 API 예시 (단일 통합 API)

대시보드는 **하나의 API** (`GET /api/dashboard`)로 통합되어 있습니다.

```python
# main.py
@app.get("/api/dashboard")
async def dashboard(
    db: Session = Depends(get_db),
    minimal: bool = Query(False, description="True면 DB만 반환(빠른 첫 렌더)"),
):
    # 1) 응답 캐시 (60초)
    if _dashboard_cache.get(cache_key) and (now - _dashboard_cache.get(f"{cache_key}_ts", 0)) < 60:
        return _dashboard_cache[cache_key]

    # 2) DB에서 목록 조회 (한 번에)
    rows = db.query(Stock, StockScore, TradeRecommendation).outerjoin(...).filter(...).limit(100).all()
    out = [build_item(stock, score, rec) for ...]
    out = sorted(out, key=_dashboard_sort_key)

    # 3) minimal=False일 때만 상위 20종목 외부 API 병렬 보정 (asyncio.gather)
    if not minimal:
        patches = await asyncio.gather(
            *[loop.run_in_executor(None, _fill_one_ticker_sync, t) for t in top_tickers],
            return_exceptions=True,
        )
        for i, patch in enumerate(patches):
            if isinstance(patch, dict):
                merge_patch_into(out[i], patch)
        out = sorted(out, key=_dashboard_sort_key)

    return {"items": out, "last_refresh_at": ...}
```

- **minimal=1**: DB만 반환 → 첫 화면 빠르게 렌더링
- **minimal=0 (기본)**: DB + 상위 20종목 외부 API 병렬·캐시 보정

---

## 2. 외부 API 병렬 호출 (async/await + asyncio.gather)

외부 API(주가, 추천가, 기관보유율, 공매도, 직원증가율)는 **캐시**를 먼저 보고, 없으면 **스레드 풀에서 동시 실행**합니다.

```python
# main.py - 상위 20종목에 대해 병렬로 한 종목씩 보정
def _fill_one_ticker_sync(ticker: str) -> dict:
    """캐시(10분 TTL) 사용. run_in_executor로 스레드에서 실행."""
    rec = cache_get_or_set(("rec", ticker), lambda: _safe(compute_recommendation, ticker), ttl=600) or {}
    return {
        "current_price": cache_get_or_set(("price", ticker), lambda: _safe(get_current_price, ticker), ttl=600),
        "entry_price": rec.get("entry_price"),
        "stop_loss": rec.get("stop_loss"),
        "target_price": rec.get("target_price"),
        "institutional_ownership": cache_get_or_set(("inst", ticker), lambda: _safe(fetch_institutional_ownership, ticker), ttl=600),
        "short_interest": cache_get_or_set(("short", ticker), lambda: _safe(fetch_short_interest, ticker), ttl=600),
        "employee_growth": cache_get_or_set(("emp", ticker), lambda: _safe(fetch_employee_growth, ticker), ttl=600),
    }

# 엔드포인트 내부
loop = asyncio.get_event_loop()
patches = await asyncio.gather(
    *[loop.run_in_executor(None, _fill_one_ticker_sync, t) for t in top_tickers],
    return_exceptions=True,
)
```

- 동기 함수(yfinance 등)는 `run_in_executor`로 스레드에서 실행해 이벤트 루프를 막지 않음.
- 20개 종목을 **동시에** 처리하고, 각 결과는 10분 캐시에 저장.

---

## 3. 간단한 캐시 구현 (10분 TTL)

```python
# cache_utils.py
import threading
import time
from typing import Any, Optional, Tuple

_cache: dict = {}  # (key_tuple -> (value, expires_at))
_lock = threading.Lock()
_DEFAULT_TTL = 600  # 10분

def cache_get(key: Tuple[str, ...], ttl: int = _DEFAULT_TTL) -> Optional[Any]:
    with _lock:
        entry = _cache.get(key)
        if entry is None:
            return None
        val, expires_at = entry
        if time.time() > expires_at:
            del _cache[key]
            return None
        return val

def cache_set(key: Tuple[str, ...], value: Any, ttl: int = _DEFAULT_TTL) -> None:
    with _lock:
        _cache[key] = (value, time.time() + ttl)

def cache_get_or_set(key: Tuple[str, ...], fetch_fn, *args, ttl: int = _DEFAULT_TTL, **kwargs) -> Any:
    val = cache_get(key, ttl)
    if val is not None:
        return val
    try:
        val = fetch_fn(*args, **kwargs)
        if val is not None:
            cache_set(key, val, ttl)
        return val
    except Exception:
        return None
```

- 키 예: `("price", "AAPL")`, `("rec", "AAPL")`.
- 스레드 안전, TTL 만료 시 자동 제거.

---

## 4. 프론트(React)에서 대시보드 데이터 가져오기

현재 프로젝트는 **React**입니다. Vue라면 `axios`/`fetch` + `Promise.all` 패턴으로 동일하게 적용하면 됩니다.

### 단일 API로 통합 호출 (기본)

```javascript
// api.js
export async function getDashboard(opts = {}) {
  const { minimal = false } = opts;
  const url = `${API_BASE}/api/dashboard${minimal ? '?minimal=1' : ''}`;
  const r = await fetch(url);
  const json = await r.json();
  if (!r.ok) throw new Error(json.detail || '대시보드 요청 실패');
  return { items: json.items || [], last_refresh_at: json.last_refresh_at ?? null };
}

export async function getDashboardMinimal() {
  return getDashboard({ minimal: true });
}
```

### 빠른 첫 렌더 + 부가 데이터 비동기 업데이트

```javascript
// Dashboard.jsx
const load = useCallback(() => {
  setLoading(true);
  setError(null);
  // 1) 빠른 첫 렌더: DB만
  getDashboardMinimal()
    .then((res) => {
      setData(sortDashboardRows(res.items || []));
      setLastRefreshAt(res.last_refresh_at ?? null);
    })
    .catch((e) => setError(e?.message))
    .finally(() => setLoading(false));
  // 2) 부가 데이터(평점, 뉴스 등 보정) 비동기 업데이트
  getDashboard()
    .then((res) => {
      setData(sortDashboardRows(res.items || []));
      setLastRefreshAt(res.last_refresh_at ?? null);
    })
    .catch(() => {});
}, []);
```

### 여러 API를 동시에 호출할 때 (Promise.all)

대시보드와 새로고침 상태를 한 번에 받는 예시입니다.

```javascript
// 예: 대시보드 + 새로고침 상태를 병렬로 요청
const [dashboardRes, statusRes] = await Promise.all([
  getDashboard(),
  getRefreshStatus(),
]);
setData(sortDashboardRows(dashboardRes.items || []));
setLastRefreshAt(dashboardRes.last_refresh_at ?? statusRes?.last_completed_at ?? null);
```

Vue 예시 (동일 패턴):

```javascript
// Vue 3 Composition API
const load = async () => {
  loading.value = true;
  const [dashboardRes, statusRes] = await Promise.all([
    getDashboard(),
    getRefreshStatus(),
  ]).catch(() => [{ items: [] }, {}]);
  items.value = dashboardRes.items || [];
  lastRefreshAt.value = dashboardRes.last_refresh_at ?? statusRes?.last_completed_at ?? null;
  loading.value = false;
};
```

---

## 요약

| 항목 | 적용 내용 |
|------|-----------|
| 단일 API | `GET /api/dashboard` 하나로 통합 (minimal 쿼리로 빠른 응답 옵션) |
| 병렬 처리 | 상위 20종목에 대해 `asyncio.gather` + `run_in_executor`로 동시 보정 |
| 캐시 | 응답 60초, 외부 API 결과 10분 TTL (`cache_utils.py`) |
| 프론트 | `getDashboard()` 단일 호출, 선택적으로 minimal 먼저 → full 비동기 업데이트 |
| Promise.all | 대시보드 + 새로고침 상태 등 여러 요청 시 병렬 호출 예시 제공 |
