# Arsenal_text/api_client.py

import requests
import logging
# config 모듈을 상대 경로로 임포트합니다.
# 스크립트를 패키지 외부에서 직접 실행할 경우 문제가 될 수 있으므로,
# main.py에서 호출하는 것을 기준으로 합니다.
try:
    from . import config
except ImportError:
    # 패키지 외부에서 직접 실행 시 (예: 테스트)
    import config

# 로깅 설정 (메인 스크립트에서 설정하는 것이 더 일반적이지만, 모듈 테스트를 위해 추가)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_matches(team_id: int, competition_id: int, api_key: str,
                  date_from: str | None = None, date_to: str | None = None,
                  timeout: int = config.REQUEST_TIMEOUT) -> list | None:
    """
    Football-Data.org API를 호출하여 특정 팀의 특정 대회 경기 목록을 가져옵니다.

    Args:
        team_id (int): 조회할 팀의 ID.
        competition_id (int): 조회할 대회의 ID.
        api_key (str): Football-Data.org API 키.
        date_from (str | None, optional): 조회 시작 날짜 ('YYYY-MM-DD'). Defaults to None.
        date_to (str | None, optional): 조회 종료 날짜 ('YYYY-MM-DD'). Defaults to None.
        timeout (int, optional): API 요청 타임아웃 (초). Defaults to config.REQUEST_TIMEOUT.

    Returns:
        list | None: 성공 시 경기 데이터 목록 (list of dicts), 실패 시 None.
    """
    base_url = f"https://api.football-data.org/v4/teams/{team_id}/matches"
    headers = {'X-Auth-Token': api_key}
    params = {'competitions': competition_id}

    # 날짜 파라미터 추가 (값이 있을 경우)
    if date_from:
        params['dateFrom'] = date_from
    if date_to:
        params['dateTo'] = date_to

    logging.info(f"Fetching matches for team {team_id}, competition {competition_id} from {date_from} to {date_to}...")

    try:
        response = requests.get(base_url, headers=headers, params=params, timeout=timeout)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생 (4xx, 5xx)

        data = response.json()
        matches = data.get('matches', [])
        logging.info(f"Successfully fetched {len(matches)} matches for competition {competition_id}.")
        return matches # 'matches' 키가 없을 경우 빈 리스트 반환

    except requests.exceptions.Timeout:
        logging.error(f"API request timed out after {timeout} seconds for competition {competition_id}.")
        return None
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err} - Status Code: {response.status_code}")
        try:
            error_details = response.json()
            logging.error(f"API error details: {error_details}")
        except ValueError:
            logging.error("Could not parse error response from API.")
        return None
    except requests.exceptions.RequestException as req_err:
        logging.error(f"API request failed: {req_err}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred during API fetch for competition {competition_id}: {e}")
        return None

# --- 모듈 테스트용 코드 ---
if __name__ == '__main__':
    # 이 블록은 'python Arsenal_text/api_client.py'와 같이 직접 실행될 때만 동작합니다.
    logging.info("Testing api_client.py module...")

    # config.py에 실제 API 키와 Supabase 정보가 입력되었는지 확인
    api_key_set = config.FOOTBALL_DATA_API_KEY != 'YOUR_FOOTBALL_DATA_API_KEY'

    if not api_key_set:
        logging.warning("API Key is not set in config.py. Skipping API call test.")
    else:
        logging.info("Attempting to fetch test data from API...")
        # 설정 파일의 첫 번째 리그 ID로 테스트
        test_league_id = list(config.LEAGUE_IDS.values())[0]
        test_matches = fetch_matches(
            team_id=config.TEAM_ID,
            competition_id=test_league_id,
            api_key=config.FOOTBALL_DATA_API_KEY,
            date_from=config.DATE_FROM,
            date_to=config.DATE_TO
        )

        if test_matches is not None:
            logging.info(f"Test fetch successful. Found {len(test_matches)} matches for competition {test_league_id}.")
            # 예시 데이터 출력 (첫 2개 경기)
            if test_matches:
                logging.info("First 2 matches data:")
                for match in test_matches[:2]:
                    logging.info(f"  Match ID: {match.get('id')}, Date: {match.get('utcDate')}, "
                                 f"Score: {match.get('score', {}).get('fullTime')}, "
                                 f"Home: {match.get('homeTeam', {}).get('name')}, "
                                 f"Away: {match.get('awayTeam', {}).get('name')}")
            else:
                logging.info("No matches found for the specified criteria in the test.")
        else:
            logging.error("Test fetch failed. Check API key, IDs, and network connection.")