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

