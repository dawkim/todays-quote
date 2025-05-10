# Arsenal_text/config.py

# --- Football-Data.org API 설정 ---
# https://www.football-data.org/ 에서 API 키를 발급받아 입력하세요.
FOOTBALL_DATA_API_KEY = '1fea04d1bf094a649ba8f71a2b8ceb59'

# --- Supabase 설정 ---
# Supabase 프로젝트의 URL과 anon key를 입력하세요.
# 환경 변수 사용을 강력히 권장합니다. (예: os.getenv('SUPABASE_URL'))
SUPABASE_URL = 'https://rmdqhiwuitptqseswctu.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJtZHFoaXd1aXRwdHFzZXN3Y3R1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDYxODYyNDEsImV4cCI6MjA2MTc2MjI0MX0.PEbKu4UYhVHg5cdXlD3bXGrub7bQrExoeeX16qxvHKc'
SUPABASE_TABLE_NAME = 'arsenal_matches' # Supabase에 생성할 테이블 이름 (plan.md 참고)

# --- 조회 대상 설정 ---
# Football-Data.org에서 조회할 팀 및 리그 ID를 입력하세요.
# 예시: 아스널 FC (팀 ID: 57), 프리미어리그 (리그 ID: 2021), 챔피언스리그 (리그 ID: 2001)
# 실제 ID는 Football-Data.org 문서를 참조하여 확인해야 합니다.
TEAM_ID = 57  # 예시: 아스널 FC
LEAGUE_IDS = {
    'PL': 2021,  # 예시: 프리미어리그
    'CL': 2001   # 예시: 챔피언스리그
}

# --- 데이터 조회 기간 설정 ---
# 데이터를 가져올 시작 날짜와 종료 날짜를 'YYYY-MM-DD' 형식으로 입력하세요.
# None으로 설정하면 API 기본값을 따릅니다.
DATE_FROM = '2025-04-01'  # 예시: 2023-24 시즌 시작일
DATE_TO = '2025-05-31'    # 예시: 2023-24 시즌 종료일

# --- 기타 설정 ---
# API 요청 시 타임아웃 (초)
REQUEST_TIMEOUT = 30