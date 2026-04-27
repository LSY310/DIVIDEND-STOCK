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