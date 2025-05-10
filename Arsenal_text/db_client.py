# Arsenal_text/db_client.py

import logging
from supabase import create_client, Client
from postgrest import APIError  # Correct import path if needed based on library structure
from typing import List, Dict, Any, Optional, Set

try:
    from . import config
except ImportError:
    import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

# --- Supabase Client Initialization ---

def initialize_supabase_client(url: str, key: str) -> Optional[Client]:
    """Initializes the Supabase client."""
    if not url or url == 'YOUR_SUPABASE_URL' or not key or key == 'YOUR_SUPABASE_ANON_KEY':
        logging.error("Supabase URL or Key is not configured in config.py.")
        return None
    try:
        supabase: Client = create_client(url, key)
        logging.info("Supabase client initialized successfully.")
        return supabase
    except Exception as e:
        logging.error(f"Failed to initialize Supabase client: {e}")
        return None

# --- Generic Upsert/Insert Helpers ---

def _upsert_data(supabase: Client, table_name: str, data: List[Dict[str, Any]], pk_column: str = 'id') -> bool:
    """Helper function to upsert data into a Supabase table."""
    if not data:
        # logging.debug(f"No data to upsert for table '{table_name}'. Skipping.")
        return True
    # logging.debug(f"Attempting to upsert {len(data)} records to '{table_name}'. First record keys: {data[0].keys() if data else 'N/A'}")
    try:
        # Note: Supabase upsert uses the primary key defined in the DB.
        # The 'on_conflict' parameter is implicitly the PK.
        # For tables with composite keys, ensure they are defined correctly in Supabase.
        response = supabase.table(table_name).upsert(data).execute()
        # Check for API level errors if the library provides them in the response
        if hasattr(response, 'error') and response.error:
             logging.error(f"Supabase API error during upsert to '{table_name}': {response.error}")
             return False
        # logging.info(f"Successfully upserted {len(data)} records to '{table_name}'.")
        return True
    except APIError as api_err:
        logging.error(f"Supabase APIError during upsert to '{table_name}': {getattr(api_err, 'message', api_err)}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error during upsert to '{table_name}': {e}")
        return False

def _insert_data(supabase: Client, table_name: str, data: List[Dict[str, Any]]) -> bool:
    """Helper function to insert data into a Supabase table."""
    if not data:
        # logging.debug(f"No data to insert for table '{table_name}'. Skipping.")
        return True
    # logging.debug(f"Attempting to insert {len(data)} records to '{table_name}'. First record keys: {data[0].keys() if data else 'N/A'}")
    try:
        response = supabase.table(table_name).insert(data).execute()
        if hasattr(response, 'error') and response.error:
             logging.error(f"Supabase API error during insert to '{table_name}': {response.error}")
             return False
        # logging.info(f"Successfully inserted {len(data)} records to '{table_name}'.")
        return True
    except APIError as api_err:
        logging.error(f"Supabase APIError during insert to '{table_name}': {getattr(api_err, 'message', api_err)}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error during insert to '{table_name}': {e}")
        return False

# --- Main Data Processing and Storage Function ---

def process_and_store_matches(supabase: Client, matches_data: List[Dict[str, Any]]) -> bool:
    """
    Parses raw match data from API and stores it in normalized Supabase tables.

    Args:
        supabase (Client): Initialized Supabase client.
        matches_data (list): List of match dictionaries from the API.

    Returns:
        bool: True if processing and storage were successful (or partially successful), False otherwise.
    """
    if not supabase:
        logging.error("Supabase client is not initialized.")
        return False
    if not matches_data:
        logging.info("No match data provided to process.")
        return True

    processed_area_ids: Set[int] = set()
    processed_competition_ids: Set[int] = set()
    processed_season_ids: Set[int] = set()
    processed_team_ids: Set[int] = set()
    processed_person_ids: Set[int] = set()
    processed_match_ids: Set[int] = set()

    # Data lists for bulk upsert/insert
    areas_to_upsert: List[Dict[str, Any]] = []
    competitions_to_upsert: List[Dict[str, Any]] = []
    seasons_to_upsert: List[Dict[str, Any]] = []
    teams_to_upsert: List[Dict[str, Any]] = []
    persons_to_upsert: List[Dict[str, Any]] = []
    matches_to_upsert: List[Dict[str, Any]] = []
    goals_to_insert: List[Dict[str, Any]] = []
    referees_to_insert: List[Dict[str, Any]] = []

    logging.info(f"Processing {len(matches_data)} matches...")

    for match in matches_data:
        try:
            match_id = match.get('id')
            if not match_id:
                logging.warning("Skipping match with no ID.")
                continue

            # --- Extract related entities ---
            area = match.get('area')
            competition = match.get('competition')
            season = match.get('season')
            home_team = match.get('homeTeam')
            away_team = match.get('awayTeam')
            score = match.get('score', {})
            full_time = score.get('fullTime', {})
            half_time = score.get('halfTime', {})
            goals = match.get('goals', [])
            referees = match.get('referees', [])

            # --- Prepare data for related tables (if not already processed) ---

            # 1. Area
            if area and area.get('id') and area['id'] not in processed_area_ids:
                areas_to_upsert.append({
                    'id': area.get('id'),
                    'name': area.get('name'),
                    'code': area.get('code'),
                    'flag': area.get('flag')
                })
                processed_area_ids.add(area['id'])

            # 2. Competition
            if competition and competition.get('id') and competition['id'] not in processed_competition_ids:
                competitions_to_upsert.append({
                    'id': competition.get('id'),
                    'area_id': area.get('id') if area else None, # FK
                    'name': competition.get('name'),
                    'code': competition.get('code'),
                    'type': competition.get('type'),
                    'emblem': competition.get('emblem')
                })
                processed_competition_ids.add(competition['id'])

            # 3. Season
            if season and season.get('id') and season['id'] not in processed_season_ids:
                # API winner might be a team object, extract ID
                winner_id = None
                winner_data = season.get('winner')
                if isinstance(winner_data, dict):
                    winner_id = winner_data.get('id')

                seasons_to_upsert.append({
                    'id': season.get('id'),
                    'competition_id': competition.get('id') if competition else None, # FK
                    'startDate': season.get('startDate'),
                    'endDate': season.get('endDate'),
                    'currentMatchday': season.get('currentMatchday'),
                    'winner_id': winner_id # FK (nullable)
                })
                processed_season_ids.add(season['id'])

            # 4. Teams (Home & Away)
            if home_team and home_team.get('id') and home_team['id'] not in processed_team_ids:
                teams_to_upsert.append({
                    'id': home_team.get('id'),
                    'name': home_team.get('name'),
                    'shortName': home_team.get('shortName'),
                    'tla': home_team.get('tla'),
                    'crest': home_team.get('crest')
                })
                processed_team_ids.add(home_team['id'])
            if away_team and away_team.get('id') and away_team['id'] not in processed_team_ids:
                teams_to_upsert.append({
                    'id': away_team.get('id'),
                    'name': away_team.get('name'),
                    'shortName': away_team.get('shortName'),
                    'tla': away_team.get('tla'),
                    'crest': away_team.get('crest')
                })
                processed_team_ids.add(away_team['id'])

            # 5. Persons (Coaches, Scorers, Assists, Referees)
            persons_in_match: List[Dict[str, Any]] = []
            if home_team and home_team.get('coach') and home_team['coach'].get('id'): persons_in_match.append(home_team['coach'])
            if away_team and away_team.get('coach') and away_team['coach'].get('id'): persons_in_match.append(away_team['coach'])
            for goal in goals:
                if goal.get('scorer') and goal['scorer'].get('id'): persons_in_match.append(goal['scorer'])
                if goal.get('assist') and goal['assist'].get('id'): persons_in_match.append(goal['assist'])
            for referee in referees:
                 if referee and referee.get('id'): persons_in_match.append(referee)

            for person in persons_in_match:
                 person_id = person.get('id')
                 if person_id and person_id not in processed_person_ids:
                    persons_to_upsert.append({
                        'id': person_id,
                        'name': person.get('name'),
                        'nationality': person.get('nationality'),
                        # Position might not always be present (e.g., for referees)
                        'position': person.get('position')
                    })
                    processed_person_ids.add(person_id)

            # --- Prepare data for main match table (if not already processed) ---
            if match_id not in processed_match_ids:
                matches_to_upsert.append({
                    'id': match_id,
                    'competition_id': competition.get('id') if competition else None, # FK
                    'season_id': season.get('id') if season else None, # FK
                    'utcDate': match.get('utcDate'),
                    'status': match.get('status'),
                    'matchday': match.get('matchday'),
                    'stage': match.get('stage'),
                    'group': match.get('group'), # Ensure DB column name is quoted if "group"
                    'home_team_id': home_team.get('id') if home_team else None, # FK
                    'away_team_id': away_team.get('id') if away_team else None, # FK
                    'score_ft_home': full_time.get('home'),
                    'score_ft_away': full_time.get('away'),
                    'score_ht_home': half_time.get('home'),
                    'score_ht_away': half_time.get('away'),
                    'winner': score.get('winner'),
                    'duration': score.get('duration')
                })
                processed_match_ids.add(match_id)

                # --- Prepare data for dependent tables (Goals, Referees) for this match ---
                # These are inserted per match to ensure match_id exists
                for goal in goals:
                     scorer = goal.get('scorer', {})
                     assist = goal.get('assist', {})
                     team = goal.get('team', {})
                     goal_score = goal.get('score', {})
                     goals_to_insert.append({
                         'match_id': match_id, # FK
                         'minute': goal.get('minute'),
                         'type': goal.get('type'),
                         'team_id': team.get('id'), # FK
                         'scorer_id': scorer.get('id'), # FK
                         'assist_id': assist.get('id') if assist else None, # FK (nullable)
                         'score_home': goal_score.get('home'),
                         'score_away': goal_score.get('away')
                     })

                for referee in referees:
                     if referee and referee.get('id'):
                        referees_to_insert.append({
                            'match_id': match_id, # FK
                            'person_id': referee.get('id'), # FK
                            'type': referee.get('type')
                        })

        except Exception as e:
            logging.error(f"Error processing match ID {match.get('id', 'N/A')}: {e}", exc_info=True)
            # Continue processing other matches

    # --- Bulk Upsert/Insert Data (in dependency order) ---
    overall_success = True
    logging.info("Starting database operations...")

    # Upsert independent or parent entities first
    logging.info(f"Upserting {len(areas_to_upsert)} areas...")
    if not _upsert_data(supabase, 'areas', areas_to_upsert): overall_success = False
    logging.info(f"Upserting {len(teams_to_upsert)} teams...")
    if not _upsert_data(supabase, 'teams', teams_to_upsert): overall_success = False
    logging.info(f"Upserting {len(persons_to_upsert)} persons...")
    if not _upsert_data(supabase, 'persons', persons_to_upsert): overall_success = False
    logging.info(f"Upserting {len(competitions_to_upsert)} competitions...")
    if not _upsert_data(supabase, 'competitions', competitions_to_upsert): overall_success = False
    logging.info(f"Upserting {len(seasons_to_upsert)} seasons...")
    if not _upsert_data(supabase, 'seasons', seasons_to_upsert): overall_success = False

    # Upsert matches (depends on competitions, seasons, teams)
    logging.info(f"Upserting {len(matches_to_upsert)} matches...")
    if not _upsert_data(supabase, 'matches', matches_to_upsert): overall_success = False

    # Insert dependent data (goals, referees - depend on matches, persons, teams)
    # Using INSERT because no stable unique key from API besides generated PK
    logging.info(f"Inserting {len(goals_to_insert)} goals...")
    if not _insert_data(supabase, 'goals', goals_to_insert): overall_success = False
    logging.info(f"Inserting {len(referees_to_insert)} referees...")
    if not _insert_data(supabase, 'referees', referees_to_insert): overall_success = False

    if overall_success:
        logging.info("Database operations completed.")
    else:
        logging.warning("Some database operations may have failed. Check logs for details.")

    return overall_success

# No test code in __main__ block for this complex refactoring