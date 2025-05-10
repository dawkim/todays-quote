# Arsenal_text/main.py

import logging
import sys
import os

# 스크립트가 있는 디렉토리를 sys.path에 추가하여 모듈 임포트 경로 문제 해결
# (스크립트를 다른 위치에서 실행할 경우 필요할 수 있음)
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

try:
    import config
    import api_client
    import db_client
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure config.py, api_client.py, and db_client.py are in the same directory or sys.path is configured correctly.")
    sys.exit(1)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout) # 로그를 터미널에 출력
        # 필요시 파일 핸들러 추가: logging.FileHandler('script.log')
    ]
)

def main():
    """메인 실행 함수"""
    logging.info("Starting the script...")

    # 1. 설정 로드 (config 모듈 임포트로 자동 로드됨)
    logging.info("Configuration loaded.")
    api_key = config.FOOTBALL_DATA_API_KEY
    supabase_url = config.SUPABASE_URL
    supabase_key = config.SUPABASE_KEY
    team_id = config.TEAM_ID
    league_ids = config.LEAGUE_IDS
    date_from = config.DATE_FROM
    date_to = config.DATE_TO

    # 필수 설정값 확인
    if api_key == 'YOUR_FOOTBALL_DATA_API_KEY' or \
       supabase_url == 'YOUR_SUPABASE_URL' or \
       supabase_key == 'YOUR_SUPABASE_ANON_KEY':
        logging.error("API Key or Supabase credentials are not set in config.py. Exiting.")
        sys.exit(1)

    # 2. Supabase 클라이언트 초기화
    logging.info("Initializing Supabase client...")
    supabase = db_client.initialize_supabase_client(supabase_url, supabase_key)
    if not supabase:
        logging.error("Failed to initialize Supabase client. Exiting.")
        sys.exit(1)

    # 3. API에서 데이터 가져오기
    all_matches = []
    fetch_success = True
    for league_name, competition_id in league_ids.items():
        logging.info(f"--- Fetching data for {league_name} (ID: {competition_id}) ---")
        matches = api_client.fetch_matches(
            team_id=team_id,
            competition_id=competition_id,
            api_key=api_key,
            date_from=date_from,
            date_to=date_to
        )
        if matches is not None:
            logging.info(f"Successfully fetched {len(matches)} matches for {league_name}.")
            all_matches.extend(matches)
        else:
            logging.warning(f"Failed to fetch matches for {league_name}. Continuing with other leagues...")
            fetch_success = False # 하나라도 실패하면 플래그 설정 (선택적)

    logging.info(f"--- Total matches fetched across all leagues: {len(all_matches)} ---")

    # 4. 데이터 처리 및 Supabase에 저장
    if not all_matches:
        logging.info("No matches data fetched or available to process. Exiting.")
        sys.exit(0) # 정상 종료

    logging.info("Processing and storing fetched data to Supabase...")
    # process_and_store_matches 함수는 내부적으로 여러 테이블에 upsert/insert를 수행
    process_success = db_client.process_and_store_matches(supabase, all_matches)

    if process_success:
        logging.info("Successfully processed and stored match data.")
    else:
        logging.error("Failed to process and store match data completely. Check logs for details.")
        # 오류가 발생해도 부분적으로 데이터가 저장되었을 수 있으므로,
        # 여기서는 스크립트를 중단하지 않고 경고와 함께 종료할 수 있습니다.
        # 필요에 따라 sys.exit(1)로 변경 가능
        logging.warning("Script finished with errors.")
    
    logging.info("Script finished.")

if __name__ == "__main__":
    main()