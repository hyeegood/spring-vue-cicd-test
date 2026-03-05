# =======================================
# 정량 투자 스코어링 엔진 (Quantitative Investment Scoring Engine)
# =======================================
#
# 5개 카테고리: Value, Growth, Quality, Sentiment, Risk
# 최종 공식:
#   InvestmentScore =
#     ValueScore * 0.25 +
#     GrowthScore * 0.25 +
#     QualityScore * 0.20 +
#     SentimentScore * 0.15 +
#     RiskAdjustment * 0.15
#
# 모든 점수 범위: 0 ~ 100
# 출력: value_score, growth_score, quality_score, sentiment_score, risk_adjustment, investment_score
#
# =======================================

from typing import Optional, Dict, Any


# =======================================
# Value Score (0-100)
# 지표: PER, PBR, EV/EBITDA, FCF Yield
# 밸류에이션이 낮을수록(저평가) 점수 높음
# =======================================

def compute_value_score(
    per: Optional[float] = None,
    pbr: Optional[float] = None,
    ev_ebitda: Optional[float] = None,
    fcf_yield: Optional[float] = None,
) -> float:
    """
    밸류 점수: PER, PBR, EV/EBITDA, FCF Yield 기반.
    - PER 10~20 구간이 이상적이면 가점, 50 초과면 감점
    - PBR 0~2 구간이면 가점
    - EV/EBITDA 낮을수록 가치 매력도 높음
    - FCF Yield 높을수록 가치 매력도 높음 (데이터 없으면 50 기준)
    """
    score = 50.0  # 기본 중립

    # PER: 10~20 최적, 20~30 보통, 50+ 고평가
    if per is not None and per > 0:
        if 8 <= per <= 15:
            score += 15
        elif 15 < per <= 25:
            score += 8
        elif 25 < per <= 40:
            score += 0
        elif per > 50:
            score -= 20
        elif per < 5:  # 극단적 저PER(위험 가능성)
            score += 5

    # PBR: 0~2 매력적, 2~4 보통
    if pbr is not None and pbr > 0:
        if 0 < pbr <= 1.5:
            score += 12
        elif 1.5 < pbr <= 3:
            score += 5
        elif pbr > 5:
            score -= 10

    # EV/EBITDA: 낮을수록 저평가
    if ev_ebitda is not None and ev_ebitda > 0:
        if ev_ebitda <= 8:
            score += 12
        elif ev_ebitda <= 15:
            score += 6
        elif ev_ebitda > 25:
            score -= 10

    # FCF Yield (%): 높을수록 좋음. 5% 이상이면 가점
    if fcf_yield is not None:
        if fcf_yield >= 10:
            score += 10
        elif fcf_yield >= 5:
            score += 5
        elif fcf_yield < 0:
            score -= 10

    return round(max(0.0, min(100.0, score)), 1)


# =======================================
# Growth Score (0-100)
# 지표: Revenue growth, EPS growth, Forward growth
# 성장률이 높을수록 점수 높음
# =======================================

def compute_growth_score(
    revenue_growth: Optional[float] = None,
    eps_growth: Optional[float] = None,
    forward_growth: Optional[float] = None,
    roe: Optional[float] = None,
    peg: Optional[float] = None,
) -> float:
    """
    성장 점수: 매출 성장, EPS 성장, 포워드 성장.
    - revenue_growth, eps_growth: % (예: 15 = 15%)
    - forward_growth: 예상 성장률 %
    - roe, peg: 데이터 없을 때 대리 지표로 사용 (ROE 높으면 성장성 프록시, PEG 낮으면 성장 대비 저평가)
    """
    score = 50.0

    # 매출 성장률 (%)
    if revenue_growth is not None:
        if revenue_growth >= 20:
            score += 20
        elif revenue_growth >= 10:
            score += 12
        elif revenue_growth >= 5:
            score += 5
        elif revenue_growth < 0:
            score -= 15

    # EPS 성장률 (%)
    if eps_growth is not None:
        if eps_growth >= 25:
            score += 15
        elif eps_growth >= 15:
            score += 10
        elif eps_growth >= 5:
            score += 3
        elif eps_growth < 0:
            score -= 12

    # 포워드(예상) 성장률 (%)
    if forward_growth is not None:
        if forward_growth >= 20:
            score += 10
        elif forward_growth >= 10:
            score += 5
        elif forward_growth < 0:
            score -= 8

    # 대리 지표: ROE(수익성 성장 프록시), PEG(성장 대비 밸류)
    if revenue_growth is None and eps_growth is None and roe is not None:
        if roe >= 20:
            score += 15
        elif roe >= 15:
            score += 8
        elif roe >= 10:
            score += 3
    if peg is not None and peg > 0 and peg <= 2:
        score += 5  # PEG 2 이하면 성장 대비 저평가

    return round(max(0.0, min(100.0, score)), 1)


# =======================================
# Quality Score (0-100)
# 지표: ROE, Operating margin, Debt ratio, Cash flow stability
# 수익성·재무 안정성이 높을수록 점수 높음
# =======================================

def compute_quality_score(
    roe: Optional[float] = None,
    operating_margin: Optional[float] = None,
    debt_ratio: Optional[float] = None,
    cash_flow_stability: Optional[float] = None,
    fcf: Optional[float] = None,
) -> float:
    """
    퀄리티 점수: ROE, 영업이익률, 부채비율, 현금흐름 안정성.
    - ROE: 자기자본이익률, 높을수록 좋음
    - operating_margin: 영업이익률 %, 높을수록 좋음
    - debt_ratio: 부채비율, 낮을수록 좋음 (100 이하 안전, 200 초과 위험)
    - cash_flow_stability: 0~100 스코어 또는 FCF 일관성. 없으면 fcf(성장)로 대체
    """
    score = 50.0

    # ROE (%)
    if roe is not None:
        if roe >= 20:
            score += 18
        elif roe >= 15:
            score += 12
        elif roe >= 10:
            score += 6
        elif roe < 0:
            score -= 15

    # 영업이익률 (%)
    if operating_margin is not None:
        if operating_margin >= 25:
            score += 15
        elif operating_margin >= 15:
            score += 10
        elif operating_margin >= 5:
            score += 3
        elif operating_margin < 0:
            score -= 15

    # 부채비율 (%): 낮을수록 안정
    if debt_ratio is not None:
        if debt_ratio <= 50:
            score += 12
        elif debt_ratio <= 100:
            score += 5
        elif debt_ratio <= 150:
            score -= 5
        elif debt_ratio > 200:
            score -= 20

    # 현금흐름 안정성: 0~100 또는 FCF 성장/존재 여부
    if cash_flow_stability is not None:
        score += (cash_flow_stability - 50) * 0.2  # 50 기준 ±10
    elif fcf is not None and fcf > 0:
        score += 5  # FCF 양수면 가점

    return round(max(0.0, min(100.0, score)), 1)


# =======================================
# Sentiment Score (0-100)
# 지표: News sentiment, Analyst ratings, Social sentiment
# 뉴스 감성(-1~1), 애널리스트, 소셜은 0~100 또는 -1~1로 통일 후 0~100 변환
# =======================================

def compute_sentiment_score(
    news_sentiment: Optional[float] = None,
    analyst_rating: Optional[float] = None,
    social_sentiment: Optional[float] = None,
) -> float:
    """
    감성 점수: 뉴스 감성, 애널리스트 평점, 소셜 감성.
    - news_sentiment: -1~1 (뉴스 감성) → 0~100으로 매핑
    - analyst_rating: 1~5 또는 0~100. 5점 만점이면 5*20=100
    - social_sentiment: -1~1 또는 0~100
    """
    score = 50.0

    # 뉴스 감성 (-1 ~ 1) → 0~100
    if news_sentiment is not None:
        news_contrib = (float(news_sentiment) + 1) * 50  # -1→0, 0→50, 1→100
        score = 0.5 * score + 0.5 * news_contrib  # 50% 반영

    # 애널리스트 평점: 0~100 스케일이면 그대로 반영, 1~5 스케일이면 5점=100으로 환산
    if analyst_rating is not None:
        if 0 <= analyst_rating <= 100 and analyst_rating > 5:
            score = 0.5 * score + 0.5 * analyst_rating
        else:
            # 1~5 스케일 가정 (5점=매수 강력)
            if analyst_rating >= 4.5:
                score += 15
            elif analyst_rating >= 4:
                score += 8
            elif analyst_rating >= 3:
                score += 0
            elif analyst_rating < 2.5:
                score -= 15

    # 소셜 감성 (-1~1 또는 0~100)
    if social_sentiment is not None:
        if -1 <= social_sentiment <= 1:
            social_100 = (float(social_sentiment) + 1) * 50
        else:
            social_100 = max(0, min(100, float(social_sentiment)))
        score = 0.6 * score + 0.4 * social_100

    return round(max(0.0, min(100.0, score)), 1)


# =======================================
# Risk Adjustment (0-100)
# 지표: Volatility, Sector risk, Maximum drawdown
# 위험 낮을수록 점수 높음 → 고점수 = 리스크 조정 후 유리
# =======================================

def compute_risk_adjustment(
    volatility: Optional[float] = None,
    sector_risk: Optional[float] = None,
    max_drawdown: Optional[float] = None,
    rsi: Optional[float] = None,
    beta: Optional[float] = None,
    debt_ratio: Optional[float] = None,
) -> float:
    """
    리스크 조정 점수: 변동성, 섹터 리스크, 최대 낙폭, 부채비율.
    - volatility: 낮을수록 좋음 (예: 연간 변동성 %). 높으면 감점
    - sector_risk: 0~100, 높을수록 위험. 100이면 고위험 섹터
    - max_drawdown: 최대 낙폭 % (음수). -50이면 50% 하락. 적을수록(0에 가까울수록) 좋음
    - rsi: 극단이면 변동성 프록시로 감점 (50 근처가 안정)
    - beta: 1 초과면 시장 대비 변동성 높음 → 감점
    - debt_ratio: 부채비율 %. 높을수록 위험 → 감점
    """
    score = 50.0

    # 부채비율: 낮을수록 안정 (높으면 감점)
    if debt_ratio is not None:
        if debt_ratio <= 50:
            score += 8
        elif debt_ratio <= 100:
            score += 0
        elif debt_ratio > 200:
            score -= 15
        elif debt_ratio > 150:
            score -= 8

    # 변동성: 낮을수록 가점 (volatility 20% 이하면 안정, 40% 초과면 위험)
    if volatility is not None:
        if volatility <= 15:
            score += 15
        elif volatility <= 25:
            score += 5
        elif volatility >= 50:
            score -= 20
        elif volatility >= 35:
            score -= 10
    # RSI로 변동성 프록시: 50 근처가 안정, 30 이하/70 이상은 극단
    elif rsi is not None:
        dev = abs(rsi - 50)
        if dev <= 10:
            score += 10
        elif dev >= 30:
            score -= 15

    # 섹터 리스크: 0(안전)~100(위험). 낮을수록 가점
    if sector_risk is not None:
        if sector_risk <= 30:
            score += 15
        elif sector_risk <= 50:
            score += 5
        elif sector_risk >= 80:
            score -= 20

    # 최대 낙폭 (%): -20 이하면 -20% 하락. 적을수록(0에 가까울수록) 좋음
    if max_drawdown is not None:
        dd = abs(max_drawdown)  # -30 → 30
        if dd <= 10:
            score += 10
        elif dd <= 20:
            score += 3
        elif dd >= 50:
            score -= 20
        elif dd >= 35:
            score -= 10

    # Beta: 1 초과면 시장 대비 변동성 높음
    if beta is not None:
        if beta <= 0.8:
            score += 5
        elif beta >= 1.5:
            score -= 15
        elif beta >= 1.2:
            score -= 5

    return round(max(0.0, min(100.0, score)), 1)


# =======================================
# 최종 투자 점수 (0-100)
# Value*0.25 + Growth*0.25 + Quality*0.20 + Sentiment*0.15 + RiskAdjustment*0.15
# =======================================

def compute_investment_score(
    value_score: float,
    growth_score: float,
    quality_score: float,
    sentiment_score: float,
    risk_adjustment: float,
) -> float:
    """
    최종 투자 점수 = 가중 평균.
    가중치: Value 25%, Growth 25%, Quality 20%, Sentiment 15%, Risk 15%.
    """
    total = (
        value_score * 0.25
        + growth_score * 0.25
        + quality_score * 0.20
        + sentiment_score * 0.15
        + risk_adjustment * 0.15
    )
    return round(max(0.0, min(100.0, total)), 1)


# =======================================
# 일괄 계산: DB/API에서 넘긴 지표로 6개 점수 한 번에 산출
# =======================================

def compute_all_scores(
    # Value
    per: Optional[float] = None,
    pbr: Optional[float] = None,
    ev_ebitda: Optional[float] = None,
    fcf_yield: Optional[float] = None,
    # Growth
    revenue_growth: Optional[float] = None,
    eps_growth: Optional[float] = None,
    forward_growth: Optional[float] = None,
    roe: Optional[float] = None,
    peg: Optional[float] = None,
    # Quality
    operating_margin: Optional[float] = None,
    debt_ratio: Optional[float] = None,
    cash_flow_stability: Optional[float] = None,
    fcf: Optional[float] = None,
    # Sentiment
    news_sentiment: Optional[float] = None,
    analyst_rating: Optional[float] = None,
    social_sentiment: Optional[float] = None,
    # Risk
    volatility: Optional[float] = None,
    sector_risk: Optional[float] = None,
    max_drawdown: Optional[float] = None,
    rsi: Optional[float] = None,
    beta: Optional[float] = None,
) -> Dict[str, float]:
    """
    모든 카테고리 점수와 최종 투자 점수를 한 번에 계산.
    반환: value_score, growth_score, quality_score, sentiment_score, risk_adjustment, investment_score
    """
    value_score = compute_value_score(per=per, pbr=pbr, ev_ebitda=ev_ebitda, fcf_yield=fcf_yield)
    growth_score = compute_growth_score(
        revenue_growth=revenue_growth,
        eps_growth=eps_growth,
        forward_growth=forward_growth,
        roe=roe,
        peg=peg,
    )
    quality_score = compute_quality_score(
        roe=roe,
        operating_margin=operating_margin,
        debt_ratio=debt_ratio,
        cash_flow_stability=cash_flow_stability,
        fcf=fcf,
    )
    sentiment_score = compute_sentiment_score(
        news_sentiment=news_sentiment,
        analyst_rating=analyst_rating,
        social_sentiment=social_sentiment,
    )
    risk_adjustment = compute_risk_adjustment(
        volatility=volatility,
        sector_risk=sector_risk,
        max_drawdown=max_drawdown,
        rsi=rsi,
        beta=beta,
    )
    investment_score = compute_investment_score(
        value_score=value_score,
        growth_score=growth_score,
        quality_score=quality_score,
        sentiment_score=sentiment_score,
        risk_adjustment=risk_adjustment,
    )
    return {
        "value_score": value_score,
        "growth_score": growth_score,
        "quality_score": quality_score,
        "sentiment_score": sentiment_score,
        "risk_adjustment": risk_adjustment,
        "investment_score": investment_score,
    }


def sector_to_risk(sector: Optional[str]) -> float:
    """
    섹터 문자열 → 리스크 점수 (0=안전, 100=위험).
    reliability_engine의 섹터 신뢰도(높을수록 안전)를 반전해 사용.
    """
    try:
        from reliability_engine import get_sector_reliability
        rel = get_sector_reliability(sector)
        return round(100.0 - rel, 1)  # 신뢰도 90 → 리스크 10
    except Exception:
        return 50.0


def compute_all_scores_from_stock_score(stock_entity, score_entity, sector_risk: Optional[float] = None) -> Dict[str, float]:
    """
    DB의 Stock + StockScore(또는 유사 모델)에서 필드를 읽어 compute_all_scores 호출.
    sector_risk 없으면 stock.sector로 sector_to_risk() 사용.
    """
    per = getattr(score_entity, "per", None)
    pbr = getattr(score_entity, "pbr", None)
    ev_ebitda = getattr(score_entity, "ev_ebitda", None)
    fcf = getattr(score_entity, "fcf", None)
    roe = getattr(score_entity, "roe", None)
    peg = getattr(score_entity, "peg", None)
    operating_margin = getattr(score_entity, "operating_margin", None)
    debt_ratio = getattr(score_entity, "debt_ratio", None)
    sentiment_score_raw = getattr(score_entity, "sentiment_score", None)
    rsi = getattr(score_entity, "rsi", None)
    if sector_risk is None and stock_entity is not None:
        sector_risk = sector_to_risk(getattr(stock_entity, "sector", None))
    fcf_yield = None
    return compute_all_scores(
        per=per,
        pbr=pbr,
        ev_ebitda=ev_ebitda,
        fcf_yield=fcf_yield,
        revenue_growth=None,
        eps_growth=None,
        forward_growth=None,
        roe=roe,
        peg=peg,
        operating_margin=operating_margin,
        debt_ratio=debt_ratio,
        cash_flow_stability=None,
        fcf=fcf,
        news_sentiment=sentiment_score_raw,
        analyst_rating=None,
        social_sentiment=None,
        volatility=None,
        sector_risk=sector_risk,
        max_drawdown=None,
        rsi=rsi,
        beta=None,
    )
