# 파이썬 스크립트 개발 계획

## 1. 설정 관리 (`config.py` 또는 환경 변수)
*   API 키, Supabase 접속 정보(URL, anon key) 등 민감한 정보를 안전하게 관리합니다.
*   아스널 팀 ID, 프리미어리그 ID, 챔피언스리그 ID를 저장합니다. (실제 ID는 사용자가 직접 찾아 업데이트해야 합니다.)
*   데이터를 가져올 날짜 범위(시작일, 종료일)를 설정합니다.
*   *중요:* 실제 운영 환경에서는 보안을 위해 코드에 직접 API 키나 Supabase 키 등을 작성하지 않고 환경 변수나 별도의 보안 설정 관리 도구를 사용하는 것이 좋습니다.

## 2. API 연동 기능 (별도 파일 또는 메인 스크립트 내 함수)
*   `fetch_matches` 함수: 특정 팀 ID, 대회 ID, API 키, 날짜 범위를 입력받아 Football-Data.org API를 호출합니다.
*   `requests` 라이브러리를 사용하여 GET 요청을 보내고, 헤더에 API 키(`X-Auth-Token`)를 포함합니다.
*   네트워크 오류, 인증 실패, API 사용량 초과 등 발생 가능한 오류를 확인하고 처리합니다.
*   성공적으로 응답을 받으면 JSON 데이터를 파싱하여 경기 목록을 반환합니다. 오류 발생 시 적절한 값(예: `None`)을 반환하거나 오류를 알립니다.

## 3. Supabase 연동 기능 (별도 파일 또는 메인 스크립트 내 함수)
*   **데이터 모델:** API 응답 데이터를 정규화하여 여러 관련 테이블에 저장합니다. (아래 테이블 스키마 정의 참고)
*   `initialize_supabase_client` 함수: 설정 정보를 바탕으로 Supabase 클라이언트를 초기화하고 반환합니다. 초기화 실패 시 오류를 처리합니다.
*   **데이터 Upsert 함수들:** API 응답에서 관련 데이터를 추출하고 각 테이블에 맞게 가공하여 삽입/업데이트(upsert)하는 함수들을 구현합니다.
    *   `upsert_area(data)`: 지역 정보 저장 (`areas` 테이블)
    *   `upsert_competition(data)`: 대회 정보 저장 (`competitions` 테이블)
    *   `upsert_season(data)`: 시즌 정보 저장 (`seasons` 테이블)
    *   `upsert_team(data)`: 팀 정보 저장 (`teams` 테이블)
    *   `upsert_person(data)`: 선수/감독/심판 정보 저장 (`persons` 테이블)
    *   `upsert_match(data)`: 경기 기본 정보 저장 (`matches` 테이블)
    *   `upsert_goal(data)`: 득점 정보 저장 (`goals` 테이블)
    *   `upsert_referee(data)`: 심판 배정 정보 저장 (`referees` 테이블)
    *   (필요시 추가: `upsert_booking`, `upsert_substitution` 등)
*   **데이터 파싱 및 관계 처리:**
    *   `fetch_matches` 함수에서 반환된 복잡한 JSON 데이터를 파싱하여 각 테이블에 필요한 정보를 추출합니다.
    *   테이블 간의 외래 키(FK) 관계를 고려하여 데이터 삽입 순서를 관리합니다. 예를 들어, `matches` 테이블에 데이터를 삽입하기 전에 해당 경기의 `competitions`, `seasons`, `teams` 데이터가 각 테이블에 먼저 존재해야 합니다.
    *   `supabase` 라이브러리의 `upsert` 메서드를 사용하여 각 테이블의 기본 키(PK)를 기준으로 중복 데이터는 업데이트하고 새 데이터는 삽입합니다.
*   **오류 처리:** 각 테이블에 대한 데이터 삽입/업데이트 중 발생하는 Supabase 관련 오류를 처리합니다.

## 4. 메인 스크립트 (`main.py`)
*   전체 작업 흐름을 제어합니다.
*   설정 정보를 불러옵니다.
*   Supabase 클라이언트를 초기화합니다.
*   API 연동 함수를 호출하여 프리미어리그와 챔피언스리그 경기 데이터를 각각 가져옵니다.
*   가져온 데이터를 하나로 합칩니다.
*   **데이터 파싱 및 정제:** 가져온 경기 데이터 목록을 순회하며 각 테이블에 필요한 데이터를 추출하고 가공합니다. (중복 제거 포함)
*   **데이터베이스 저장:** `db_client.py`의 `upsert_...` 함수들을 **올바른 순서**로 호출하여 정제된 데이터를 각 테이블에 저장합니다.
    *   순서 예시: areas -> competitions -> seasons -> teams -> persons -> matches -> goals -> referees
*   작업 진행 상황을 터미널에 출력합니다(예: "데이터 가져오는 중...", "데이터 삽입 중...", "완료").
(Supabase 클라이언트는 별도 연결 종료 필요 없음)

## 5. 사용자 안내
*   스크립트 사용에 필요한 Football-Data.org의 팀/대회 ID 찾는 방법을 안내합니다.
*   API 키 및 Supabase URL, anon key 설정 방법을 설명합니다 (`config.py` 수정 또는 환경 변수 사용).
*   **Supabase 테이블 스키마 생성 안내:** 스크립트 실행 전에 Supabase 프로젝트에 필요한 테이블들을 생성해야 합니다. Supabase SQL 편집기나 마이그레이션 도구를 사용하여 아래 SQL 예시를 실행합니다. (컬럼 타입은 Supabase/PostgreSQL에 맞게 조정)
    ```sql
    -- 예시 테이블 생성 SQL (필요에 따라 컬럼 추가/수정)
    CREATE TABLE IF NOT EXISTS areas (id INT PRIMARY KEY, name TEXT, code TEXT, flag TEXT);
    CREATE TABLE IF NOT EXISTS competitions (id INT PRIMARY KEY, area_id INT REFERENCES areas(id), name TEXT, code TEXT, type TEXT, emblem TEXT);
    CREATE TABLE IF NOT EXISTS seasons (id INT PRIMARY KEY, competition_id INT REFERENCES competitions(id), startDate DATE, endDate DATE, currentMatchday INT, winner_id INT REFERENCES teams(id));
    CREATE TABLE IF NOT EXISTS teams (id INT PRIMARY KEY, name TEXT, shortName TEXT, tla TEXT, crest TEXT);
    CREATE TABLE IF NOT EXISTS persons (id INT PRIMARY KEY, name TEXT, nationality TEXT, position TEXT); -- 선수, 감독, 심판 통합
    CREATE TABLE IF NOT EXISTS matches (id INT PRIMARY KEY, competition_id INT REFERENCES competitions(id), season_id INT REFERENCES seasons(id), utcDate TIMESTAMPTZ, status TEXT, matchday INT, stage TEXT, "group" TEXT, home_team_id INT REFERENCES teams(id), away_team_id INT REFERENCES teams(id), score_ft_home INT, score_ft_away INT, score_ht_home INT, score_ht_away INT, winner TEXT, duration TEXT);
    CREATE TABLE IF NOT EXISTS goals (id SERIAL PRIMARY KEY, match_id INT REFERENCES matches(id), minute INT, type TEXT, team_id INT REFERENCES teams(id), scorer_id INT REFERENCES persons(id), assist_id INT REFERENCES persons(id), score_home INT, score_away INT);
    CREATE TABLE IF NOT EXISTS referees (id SERIAL PRIMARY KEY, match_id INT REFERENCES matches(id), person_id INT REFERENCES persons(id), type TEXT);
    -- 필요시 lineups, bookings, substitutions 등 추가 테이블 생성
    ```
*   필요한 파이썬 라이브러리(`requests`, `supabase`) 설치 방법을 안내합니다 (`pip install requests supabase`).
*   스크립트 실행 방법을 안내합니다 (`python main.py`).

## 작업 흐름도 (Mermaid)

```mermaid
graph TD
    A[스크립트 시작] --> B(설정 로드)
    B --> C(Supabase 클라이언트 초기화)
    C --> D{API에서 경기 데이터 가져오기 (PL & CL)}
    D -- 성공 --> E(데이터 파싱 및 정제)
    D -- 오류 --> Z(오류 기록/종료)
    E --> F(Area 정보 Upsert)
    F --> G(Competition 정보 Upsert)
    G --> H(Season 정보 Upsert)
    H --> I(Team 정보 Upsert)
    I --> J(Person 정보 Upsert)
    J --> K(Match 기본 정보 Upsert)
    K --> L(Goal 정보 Upsert)
    L --> M(Referee 정보 Upsert)
    M --> N[스크립트 종료]
    F -- 오류 --> Z
    G -- 오류 --> Z
    H -- 오류 --> Z
    I -- 오류 --> Z
    J -- 오류 --> Z
    K -- 오류 --> Z
    L -- 오류 --> Z
    M -- 오류 --> Z

    subgraph 설정 관리
        B
        C
    end
    subgraph API 연동
        D
    end
    subgraph 데이터 처리
        E
    end
    subgraph 데이터베이스 작업
        F
        G
        H
        I
        J
        K
        L
        M
        style F fill:#ccf,stroke:#333,stroke-width:1px
        style M fill:#ccf,stroke:#333,stroke-width:1px
    end
    subgraph 오류 처리
        Z
    end