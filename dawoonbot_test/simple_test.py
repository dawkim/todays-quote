print("Importing json...")
import json
print("Imported json.")

print("Importing random...")
import random
print("Imported random.")

print("Importing torch...")
import torch
print("Imported torch.")

print("Importing from transformers...")
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
print("Imported from transformers.")

# --- 설정 ---
# 사용할 사전 학습된 모델 이름
MODEL_NAME = "skt/kogpt2-base-v2" # sentencepiece 불필요 모델로 변경
# 이전에 생성한 전처리된 데이터 파일 경로 (dawoonbot 폴더 기준)
# 데이터 파일 경로를 절대 경로로 명시 (환경에 맞게 수정 필요 시 알려주세요)
DATA_FILE_PATH = r"d:/CODECODE/dawoonbot/kakaotalk_finetuning_data.jsonl"
# 프롬프트에 사용할 대화 예시 개수
NUM_EXAMPLES = 5
# 생성할 최대 토큰 수
MAX_NEW_TOKENS = 50
# ----------------

def load_examples(file_path, num_examples):
    """JSON Lines 파일에서 무작위 대화 예시를 로드합니다."""
    examples = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        if len(lines) < num_examples:
            print(f"경고: 데이터 파일에 예시가 {len(lines)}개밖에 없습니다. ({num_examples}개 요청)")
            examples = [json.loads(line) for line in lines]
        else:
            selected_lines = random.sample(lines, num_examples)
            examples = [json.loads(line) for line in selected_lines]
    except FileNotFoundError:
        print(f"오류: 데이터 파일 '{file_path}'를 찾을 수 없습니다.")
    except Exception as e:
        print(f"데이터 로드 중 오류 발생: {e}")
    return examples

def build_prompt(examples, user_input):
    """대화 예시와 사용자 입력을 바탕으로 프롬프트를 구성합니다."""
    prompt = "다음은 나와 여자친구의 대화 예시입니다. 나의 말투를 따라 응답해주세요.\n\n"
    for ex in examples:
        # 예시 형식: 여자친구: [여자친구 말]\n나: [내 말]\n
        prompt += f"여자친구: {ex['input']}\n"
        prompt += f"나: {ex['output']}\n\n"

    # 실제 질문 추가
    prompt += f"여자친구: {user_input}\n"
    prompt += "나:" # 모델이 이어서 답변하도록 유도
    return prompt

def main():
    print("간단 말투 테스트 시작...")

    # 1. 대화 예시 로드
    print(f"'{DATA_FILE_PATH}'에서 대화 예시 로드 중...")
    examples = load_examples(DATA_FILE_PATH, NUM_EXAMPLES)
    if not examples:
        print("테스트를 위한 대화 예시를 로드할 수 없습니다. 스크립트를 종료합니다.")
        return

    # 2. 모델 및 토크나이저 로드
    print(f"모델 및 토크나이저 로드 중: {MODEL_NAME}")
    try:
        # CPU에서 실행하도록 device_map 설정 (GPU 없어도 가능)
        # 만약 GPU 사용 가능하다면 device_map="auto" 또는 device=0 등으로 변경 가능
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        # 모델 로드 시 메모리 절약을 위해 낮은 정밀도(float16) 사용 시도
        # CPU에서는 bfloat16 지원 안 할 수 있으므로 float32 기본 사용
        model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.float32, device_map="cpu")
        # text-generation 파이프라인 생성
        # generator = pipeline('text-generation', model=model, tokenizer=tokenizer) # pipeline 대신 generate 사용
        print("모델 로드 완료.")
    except ImportError as e: # 오류 객체 'e'를 받도록 수정
        print(f"\nImportError 발생: {e}") # 구체적인 오류 메시지 출력
        print("필요한 라이브러리(torch, transformers 등)가 설치되었는지 확인해주세요.")
        return
    except Exception as e:
        print(f"모델 로드 중 오류 발생: {e}")
        return

    # 3. 사용자 입력 및 응답 생성 루프
    print("\n테스트를 시작합니다. 여자친구의 말을 입력하세요 (종료하려면 'quit' 입력).")
    while True:
        user_input = input("여자친구: ")
        if user_input.lower() == 'quit':
            break
        if not user_input:
            continue

        # 프롬프트 생성
        prompt = build_prompt(examples, user_input)
        # print("\n--- 생성된 프롬프트 ---") # 디버깅용
        # print(prompt)
        # print("----------------------\n")

        # 응답 생성
        print("나 (챗봇 응답 생성 중...)")
        try:
            # pipeline 대신 직접 generate 메서드 사용
            input_ids = tokenizer.encode(prompt, return_tensors='pt').to(model.device)
            # Truncation 경고 방지 및 명시적 설정
            attention_mask = torch.ones(input_ids.shape, dtype=torch.long, device=model.device)

            # 생성 파라미터 추가 (반복 줄이기, 적절한 온도 설정 등)
            outputs = model.generate(
                input_ids,
                attention_mask=attention_mask, # attention_mask 추가
                max_new_tokens=MAX_NEW_TOKENS,
                num_return_sequences=1,
                pad_token_id=tokenizer.eos_token_id,
                do_sample=True, # 샘플링 사용 (더 자연스러운 텍스트 생성)
                temperature=0.7, # 온도 조절 (낮을수록 결정적, 높을수록 다양)
                top_k=50, # Top-k 샘플링
                top_p=0.95, # Top-p (nucleus) 샘플링
                repetition_penalty=1.2, # 반복 페널티 (1.0 이상)
                no_repeat_ngram_size=2 # 2-gram 반복 방지
            )
            # 생성된 전체 텍스트 디코딩
            full_generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

            # 프롬프트 부분을 제외하고 실제 생성된 답변만 추출 (더 견고한 방식)
            # 프롬프트가 생성된 텍스트의 시작 부분과 일치하는지 확인
            if full_generated_text.startswith(prompt):
                 response = full_generated_text[len(prompt):].strip()
            else:
                 # 가끔 프롬프트가 약간 다르게 포함될 수 있으므로, 마지막 "나:" 기준으로 다시 시도
                 if "나:" in full_generated_text:
                      response = full_generated_text.split("나:")[-1].strip()
                 else: # 그래도 못 찾으면 전체 출력 (디버깅용)
                      response = full_generated_text # 또는 "응답 추출 실패" 등

            # 추가적인 후처리: 응답이 다음 "여자친구:" 로 시작하면 그 전까지만 사용
            if "여자친구:" in response:
                response = response.split("여자친구:")[0].strip()

            print(f"나 (챗봇): {response}")

        except Exception as e:
            print(f"응답 생성 중 오류 발생: {e}")

    print("테스트를 종료합니다.")

if __name__ == "__main__":
    main()
# 스크립트 사용 방법은 채팅창의 설명을 참고하세요.