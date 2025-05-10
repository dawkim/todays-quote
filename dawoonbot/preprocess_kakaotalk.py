import re
import json
import os
from tqdm import tqdm

# --- 사용자 설정 ---
# 사용자가 제공한 카카오톡 원본 텍스트 파일 경로
# 윈도우 경로의 경우 백슬래시(\)를 슬래시(/)로 변경하거나 이스케이프 처리(\\)해야 합니다.
KAKAO_FILE_PATH = r"C:/Users/Dawoon/Documents/KakaoTalk_20250503_1013_10_855_김뚜민.txt"
# 여자친구 이름 (카카오톡에 표시되는 이름)
GIRLFRIEND_NAME = "김뚜민"
# 사용자 이름 (카카오톡에 표시되는 이름)
MY_NAME = "김다운"
# 결과 데이터 저장 경로 (스크립트 실행 위치 기준)
OUTPUT_DIR = "."
OUTPUT_FILENAME = "kakaotalk_finetuning_data.jsonl"
# -----------------

# 정규표현식 패턴
# 날짜 구분선 (예: --------------- 2024년 5월 3일 금요일 ---------------)
date_pattern = re.compile(r"^-+ (\d{4}년 \d{1,2}월 \d{1,2}일) ")
# 일반 메시지 (예: [김다운] [오후 3:14] 안녕하세요)
# 그룹 채팅방의 경우 이름 앞에 (카톡방 이름) 이 붙을 수 있어 non-capturing group 사용
# 시간 형식은 오전/오후 HH:MM 또는 HH:MM AM/PM 등 다양할 수 있음을 고려
message_pattern = re.compile(r"^\[(?:.*?)?(.+?)\] \[(오전|오후|AM|PM)?\s?(\d{1,2}:\d{2})\] (.+)")
# 시스템 메시지 (입장, 퇴장 등) - 간단하게 대괄호로 시작하지 않는 라인으로 간주 (개선 필요)
# 사진, 동영상, 이모티콘 등 건너뛰기 위한 패턴
skip_patterns = ["사진", "동영상", "이모티콘", "파일:"]

def parse_kakao_talk(file_path, my_name, girlfriend_name):
    """
    카카오톡 대화 파일을 파싱하여 (여자친구 발화, 내 발화) 쌍 리스트를 반환합니다.
    """
    if not os.path.exists(file_path):
        print(f"오류: 파일 '{file_path}'를 찾을 수 없습니다.")
        return []

    chat_pairs = []
    last_speaker = None
    last_message = ""

    print(f"'{file_path}' 파일 파싱 시작...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in tqdm(lines, desc="파싱 진행률"):
            line = line.strip()
            if not line:
                continue

            # 날짜 구분선 건너뛰기
            if date_pattern.match(line):
                last_speaker = None # 날짜 바뀌면 문맥 초기화
                continue

            # 일반 메시지 파싱
            msg_match = message_pattern.match(line)
            if msg_match:
                speaker = msg_match.group(1).strip()
                message_time = msg_match.group(3).strip() # 시간 정보는 사용하지 않지만 추출은 해둠
                message_content = msg_match.group(4).strip()

                # 건너뛸 메시지 확인 (사진, 동영상 등)
                if any(skip in message_content for skip in skip_patterns):
                    last_speaker = None # 관련 없는 메시지는 문맥 끊기
                    continue

                # 여자친구 -> 나 순서의 발화 쌍 찾기
                if last_speaker == girlfriend_name and speaker == my_name:
                    # 너무 짧거나 의미 없는 대화는 제외 (필요시 기준 강화)
                    if len(last_message) > 1 and len(message_content) > 1:
                         chat_pairs.append({
                            "instruction": "여자친구가 이렇게 말했어:",
                            "input": last_message,
                            "output": message_content
                        })

                last_speaker = speaker
                last_message = message_content
            else:
                # 메시지 패턴에 맞지 않는 라인 (시스템 메시지 등)은 건너뛰고 문맥 초기화
                last_speaker = None
                continue # 시스템 메시지 등으로 간주하고 건너뜀

    except FileNotFoundError:
        print(f"오류: 파일 '{file_path}'를 찾을 수 없습니다.")
        return []
    except Exception as e:
        print(f"파싱 중 오류 발생: {e}")
        # 오류 발생 시 현재까지 처리된 내용이라도 반환할 수 있도록 고려
        # return chat_pairs
        return [] # 또는 오류 시 빈 리스트 반환

    print(f"파싱 완료. 총 {len(chat_pairs)}개의 (여자친구 -> 나) 대화 쌍을 찾았습니다.")
    return chat_pairs

def save_to_jsonl(data, output_path):
    """
    파싱된 데이터를 JSON Lines 파일로 저장합니다.
    """
    print(f"결과를 '{output_path}' 파일로 저장 중...")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for item in tqdm(data, desc="저장 진행률"):
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        print(f"저장 완료.")
    except Exception as e:
        print(f"파일 저장 중 오류 발생: {e}")

if __name__ == "__main__":
    # 출력 디렉토리 생성 (없으면)
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    output_file_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)

    # --- 중요 경고 메시지 ---
    print("*" * 50)
    print("경고: 이 스크립트는 기본적인 카카오톡 대화 파싱 기능만 제공합니다.")
    print("개인정보(이름, 전화번호, 주소, 계좌번호 등)가 완벽히 제거되지 않을 수 있습니다.")
    print(f"스크립트 실행 후 생성되는 '{output_file_path}' 파일을 반드시 직접 확인하고,")
    print("남아있는 모든 민감 정보를 수동으로 제거하거나 마스킹해야 합니다.")
    print("개인정보 유출에 대한 책임은 사용자 본인에게 있습니다.")
    print("*" * 50)
    # -----------------------

    # 사용자 확인 절차 (선택 사항)
    # proceed = input("위 경고를 확인했으며, 스크립트 실행에 동의하십니까? (y/n): ")
    # if proceed.lower() != 'y':
    #     print("스크립트 실행을 취소합니다.")
    #     exit()

    parsed_data = parse_kakao_talk(KAKAO_FILE_PATH, MY_NAME, GIRLFRIEND_NAME)

    if parsed_data:
        save_to_jsonl(parsed_data, output_file_path)
    else:
        print("처리할 데이터가 없거나 오류가 발생하여 파일을 저장하지 않았습니다.")

# 스크립트 사용 방법은 채팅창의 설명을 참고하세요.