## 🗓️ Day 1 - 데이터 인프라 구축 및 원천 데이터 수집
### 🔍 목표
    프로젝트를 위한 독립적인 개발 환경 구축 및 기초 데이터 수집 파이프라인 구현

### 🛠️ 실행 및 해결 과정
1. Database: Docker 기반 인프라 구축
    환경 분리: Docker를 활용해 PostgreSQL 컨테이너를 기동하여 로컬 환경과 분리된 독립적 데이터 저장소 구축.

    연결 효율화: SQLAlchemy 엔진을 생성하여 Pandas와 DB 간의 데이터 전송 효율성 증대.

2. Collector: 원천 데이터 수집 로직 구현
    데이터 소스: yfinance API를 활용하여 미국(SCHD, JEPI 등) 주요 배당 종목의 데이터 수집.

    처리 자동화: 10년치 배당 내역을 Pandas DataFrame으로 변환 후 DB에 to_sql 방식으로 대량 적재(Bulk Insert) 구현.

3. Schema 설계 및 데이터 무결성
    테이블 구조: dividend_history 테이블 설계.

    무결성 보장: ticker와 date 컬럼에 UNIQUE 제약 조건을 설정하여, 동일 종목의 중복 데이터가 수집되는 것을 원천 차단(Data Integrity).

### ⚠️ Trouble Shooting (기술적 해결 사례)
Issue: SQLAlchemy 2.0 버전의 ObjectNotExecutableError 발생

    문제: 기존 방식(conn.execute("SQL문"))으로 쿼리 실행 시 문자열 객체 실행 불가 에러 발생.

    원인: SQLAlchemy 2.0의 엄격한 타입 체크로 인해 단순 문자열은 실행 객체로 인정되지 않음.

    해결: sqlalchemy.text를 임포트하여 쿼리를 감싸주었고, conn.commit()을 명시적으로 호출하여 트랜잭션 처리를 완료함.

### ⚠️Git 설정: 운영체제 간 줄바꿈 호환성(CRLF/LF) 문제를 인지하고, DB 데이터 보존 및 보안을 위해 postgres_data와 .env 파일을 .gitignore 처리함.

## 🗓️ Day 2 - Pandas를 활용한 재무 지표 분석 엔진 개발
### 🔍 목표
    수집된 Raw Data를 정제하여 투자 인사이트를 위한 핵심 재무 지표(CAGR, 연속성) 산출

### 🛠️ 실행 및 해결 과정
1. 시계열 분석 모듈 구현:
    Pandas의 resample 기능을 통해 불규칙한 배당 지급 데이터를 연간 단위로 표준화.

    Vectorization 연산을 사용하여 전 종목의 5년 CAGR 및 연속 성장 연수를 초고속으로 산출.

2. 데이터 타입 최적화:
    NumPy 자료형을 Python Native 타입으로 변환하여 시스템 간 데이터 호환성 확보.

### ⚠️ Trouble Shooting: 시계열 데이터 불완전성 해결
    문제: 분석 결과 CAGR이 -25% 내외의 비정상적 수치로 산출됨.

    원인: 현재 연도(2026년)의 미완성 배당 합계가 계산에 포함되어 직전 연도 대비 급락한 것으로 오인.

    해결: pd.Timestamp.now().year를 기준으로 현재 연도 데이터를 분석 대상에서 자동 제외하는 필터링 로직을 추가하여 지표의 신뢰도 회복.

### 💡 핵심 성과

    SCHD(8.7%), AAPL(4.46%) 등 시장 실적과 일치하는 정확한 분석 수치 도출 성공.

    수치 데이터를 '인사이트'로 변환하는 자동화 파이프라인 구축 완료.

## 🗓️ Day 3 - Gemini LLM 연동 및 API 서비스 레이어 통합
### 🔍 목표
    수집된 Raw Data를 정제하여 투자 인사이트를 위한 핵심 재무 지표(CAGR, 연속성) 산출

### 🛠️ 실행 및 해결 과정
1. AI Insight: Gemini API 기반 리포터 구현
    Persona Prompting: Gemini 1.5 Flash 모델에 '배당 성장주 전문 퀀트 분석가' 페르소나를 부여하여 단순 수치 나열이 아닌 정성적 해석(배당 신뢰도, 리스크 평가) 로직 구현.

    Metrics Integration: Day 2에서 산출한 CAGR($$CAGR = (\frac{V_{final}}{V_{begin}})^{\frac{1}{n-1}} - 1$$)과 연속 성장 연수 데이터를 Prompt에 주입하여 데이터 근거형 답변 유도.

2. Backend: FastAPI 서비스 레이어 통합
    Pipeline Orchestration: Collector(수집) -> Analyzer(분석) -> AIReporter(해석)로 이어지는 전체 워크플로우를 /analyze/{ticker} 하나의 API로 통합.

    Async/Await: LLM API 호출 및 DB I/O 작업 시 비동기 처리를 적용하여 응답 지연 시간 최적화.

3. Infrastructure: 환경 변수 및 의존성 관리
    python-dotenv를 활용해 API Key 및 DB URL 등 민감 정보를 분리 관리.

    docker-compose 설정을 최종 점검하여 db 컨테이너와 앱 환경 간의 네트워크 통신 확인.

### ⚠️ Trouble Shooting: LLM의 금융 도메인 세이프티 필터(Safety Settings)로 인한 응답 거부
    문제: 특정 종목에 대해 '매수' 의견을 요청할 경우, Gemini의 안전 설정에 의해 응답이 차단되거나 가이드라인 준수 문구만 출력됨.

    원인: 금융 투자 조언에 대한 AI 모델의 보수적인 내부 정책 때문으로 판단.

    해결: Prompt를 "투자 권유"가 아닌 "데이터 기반 분석 보고서 작성"으로 목적을 명확히 수정하고, HarmCategory 설정을 조정하여 분석의 자율성을 확보함. 또한 결과값에 "본 리포트는 데이터 분석 결과일 뿐이며 실제 투자의 책임은 본인에게 있음"이라는 면책 조항을 자동 포함하도록 설계

### 💡 핵심 성과

    인사이트 자동화: 단순한 데이터 수집기를 넘어, 수치($8.7\%$)를 문장("과거 평균 대비 높은 성장세로 배당 신뢰도가 높음")으로 변환하는 End-to-End 파이프라인 완성.

    확장성 확보: 신규 종목 티커만 입력하면 DB 적재부터 AI 분석까지 단 5초 내외로 수행되는 고성능 분석 환경 구축.

## Day 4 - 캐싱 시스템 도입 및 다중 분석 UI 구축
### 🔍 목표

    반복적인 API 호출 비용 절감을 위한 AI 리포트 캐싱 구현.

    여러 종목을 한 번에 분석하는 다중 비교(Compare) 엔드포인트 추가.

    Streamlit을 활용하여 백엔드 API와 연동된 시각화 대시보드(UI) 제작.

### 🛠️ 실행 및 해결 과정
1. 1단계: PostgreSQL 기반 AI 리포트 캐싱
    ai_report_cache 테이블을 설계하고, 동일 티커 조회 시 24시간 이내 데이터가 있으면 Gemini API 호출 없이 DB 값을 반환하도록 로직 구현.

    ON CONFLICT (ticker) DO UPDATE 구문을 사용하여 리포트 최신화(Upsert) 처리.                                                                          

2. 2단계: 다중 종목 분석 및 에러 핸들링
    쉼표(,)로 구분된 티커 리스트를 파싱하여 순차적으로 분석하는 /analyze/compare 엔드포인트 개발.

    yfinance의 Python 3.13 호환성 이슈(AttributeError)를 해결하기 위해 ticker.history()를 통한 데이터 강제 로드(Force-Loading) 방식 적용.

3. 3단계: Streamlit UI 연결 및 시각화
    requests 라이브러리를 통해 FastAPI 백엔드와 통신하는 전용 대시보드(dashboard.py) 구축.

    st.metric과 st.expander를 활용하여 각 종목의 CAGR, 연속 성장 연수, AI 인사이트를 카드 형태로 가독성 있게 배치.

### ⚠️ Trouble Shooting
1. 엔드포인트 우선순위 문제 : /analyze/compare와 /analyze/{ticker} 경로가 겹쳐 compare 자체를 티커로 인식하는 현상 발생.

    Solution: FastAPI 라우팅 선언 순서를 변경하여 특수 경로(compare)에 높은 우선순위 부여.

2. CORS(Cross-Origin Resource Sharing) 에러 : 서로 다른 포트(8000 vs 8501)를 사용하는 프론트와 백엔드 간 통신 차단.

    Solution: FastAPI에 CORSMiddleware를 추가하여 모든 로컬 도메인의 접근 허용.

3. yfinance 라이브러리 내부 버그 : _dividends 속성 부재로 인한 AttributeError 발생.

    Solution: ticker.dividends 대신 ticker.history(period="max")를 먼저 호출하여 객체 내부를 수동으로 초기화하는 우회 로직 적용.

### 💡 핵심 성과

    Backend: 캐싱 기능을 포함한 안정적인 배당 분석 REST API.

    Frontend: 사용자 친화적인 실시간 배당 성장 분석 대시보드.

    Efficiency: 캐시 도입을 통해 반복 조회 시 응답 속도 약 30배 개선 및 API 호출 비용 절감.

## Day 5 - 금융 분석 엔진 고도화 및 AI 리포트 캐싱 시스템 구축
### 🔍 목표

    전문 금융 지표 확장: 단순 배당금 나열을 넘어 배당 성향, 총수익률 등 퀀트 분석 지표 추가.

    성능 및 비용 최적화: API 호출 비용 절감과 응답 속도 개선을 위한 24시간 캐싱 전략 수립.

    실전형 UI/UX 완성: 시각적 가독성을 높인 대시보드 레이아웃 및 데이터 출처 관리 기능 구현.

### 🛠️ 실행 및 해결 과정
1. 금융 도메인 지표 산출 엔진 고도화 (analyzer.py)

    기존의 배당 성장률 계산 로직에 배당 성향(Payout Ratio)과 배당락일(Ex-Date) 수집 로직을 추가하여 기업의 배당 지속 가능성을 판단할 근거를 마련

    주가 변동과 배당 수익을 합산한 1년 총수익률(Total Return) 계산 로직을 구현하여 실제 투자 수익 관점의 분석을 강화

2. 서버 사이드 캐싱 로직 설계 및 구현 (main.py)

    동일 종목 재조회 시 불필요한 Gemini API 호출과 yfinance 수집을 방지하기 위해 PostgreSQL 기반의 리포트 캐시 테이블을 구축

    timedelta(hours=24)를 기준으로 캐시 만료를 관리하고, 새로운 분석이 발생할 때만 DB를 갱신하는 UPSERT(Insert or Update) 패턴을 적용

3. 응답 데이터 구조 최적화 및 UI 연동, 리포트 문서화 및 내보내기 기능 (models.py, dashboard.py)

    분석 결과가 어디서 왔는지(source: api vs source: cache) 명시하여 데이터 신뢰도를 높임

    Streamlit의 st.metric과 st.expander를 활용해 복잡한 금융 데이터를 카드 형태로 한눈에 들어오게 배치

    분석된 지표와 AI 인사이트를 PDF/Text 형식으로 변환하여 사용자가 소장할 수 있도록 `st.download_button`을 활용한 리포트 추출 기능 구현.
    
    단순 화면 열람을 넘어 실제 투자 참고 자료로 활용될 수 있도록 데이터 포맷팅 최적화.

### 💡 핵심 성과

    비용 효율적인 아키텍처: LLM API 호출은 비용과 시간이 발생하므로, 적절한 캐싱 전략이 실제 서비스 운영에서 얼마나 중요한지 체감

    데이터 무결성과 예외 처리: 금융 데이터 특성상 특정 지표가 누락(None)되는 경우가 잦은데, 이를 get() 메서드와 Optional 필드로 방어하여 시스템 안정성을 높이는 법을 배움

    도메인 지식의 중요성: 기술적인 구현 외에도 배당주 투자자가 실제로 궁금해하는 지표(배당락일, 성향 등)를 고민하고 반영하면서 서비스의 완성도는 기술력이 아닌 '사용자 이해'에서 나온다는 것을 느낌