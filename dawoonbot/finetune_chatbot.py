import os
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    pipeline,
    logging,
)
from peft import LoraConfig, PeftModel, get_peft_model
from trl import SFTTrainer # Supervised Fine-tuning Trainer

# --- 모델 및 데이터 경로 설정 ---
base_model_name = "EleutherAI/polyglot-ko-1.3b"
# 이전 단계에서 생성한 전처리된 데이터 파일 경로
dataset_path = "kakaotalk_finetuning_data.jsonl"
# Fine-tuning된 LoRA 어댑터를 저장할 경로
output_dir = "./results-polyglot-ko-1.3b-finetuned"
# -----------------------------

# --- QLoRA 설정 ---
# 4-bit 양자화 설정
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4", # NF4 (Normal Float 4) 양자화 사용
    bnb_4bit_compute_dtype=torch.bfloat16, # 계산 시 bfloat16 사용 (GPU 지원 시)
    bnb_4bit_use_double_quant=False, # 이중 양자화 사용 안 함
)

# LoRA 설정
lora_config = LoraConfig(
    lora_alpha=16, # LoRA 스케일링 파라미터
    lora_dropout=0.1, # LoRA 레이어 드롭아웃 비율
    r=64, # LoRA 랭크 (차원 축소 정도)
    bias="none",
    task_type="CAUSAL_LM",
    # 일반적으로 query, key, value 프로젝션 레이어에 적용
    target_modules=[
        "query_key_value",
        # 모델 구조에 따라 다를 수 있으므로 확인 필요 (polyglot-ko의 경우 보통 query_key_value)
        # "dense",
        # "dense_h_to_4h",
        # "dense_4h_to_h",
    ]
)
# --------------------

# --- 모델 및 토크나이저 로드 ---
print(f"기반 모델 로드 중: {base_model_name}")
model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    quantization_config=bnb_config,
    device_map="auto" # 자동으로 GPU 할당 ("" 또는 "cuda:0" 등으로 명시 가능)
)
model.config.use_cache = False # 그래디언트 체크포인팅과 호환성을 위해 비활성화
model.config.pretraining_tp = 1 # TP 설정 (필요시 조정)

print(f"토크나이저 로드 중: {base_model_name}")
tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
# Polyglot-ko 모델은 pad_token이 없을 수 있음. eos_token으로 설정.
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right" # 패딩을 오른쪽에 추가

# PEFT 모델 준비 (LoRA 적용)
print("LoRA 어댑터 적용 중...")
model = get_peft_model(model, lora_config)
model.print_trainable_parameters() # 학습 가능한 파라미터 수 출력
# -----------------------------

# --- 데이터셋 로드 및 전처리 ---
print(f"데이터셋 로드 중: {dataset_path}")
# JSON Lines 파일 로드
dataset = load_dataset("json", data_files=dataset_path, split="train")

# 데이터셋 형식 확인 (필요시 조정)
# SFTTrainer는 기본적으로 'text' 컬럼을 사용하거나,
# instruction, input, output 형식의 컬럼을 조합하여 프롬프트 형식으로 만듦.
# 여기서는 instruction, input, output 컬럼이 있다고 가정.
# 만약 다른 컬럼명이라면 SFTTrainer의 dataset_text_field 등을 설정해야 함.

# 데이터셋 예시 출력 (디버깅용)
print("데이터셋 예시:")
print(dataset[0])
# -----------------------------

# --- 학습 파라미터 설정 ---
# RTX 3060 Ti (8GB VRAM) 환경을 고려한 설정
training_arguments = TrainingArguments(
    output_dir=output_dir,              # 결과 저장 디렉토리
    num_train_epochs=1,                 # 에포크 수 (데이터 양이 적으므로 1~3 추천)
    per_device_train_batch_size=2,      # 배치 크기 (VRAM 부족 시 1로 줄이기)
    gradient_accumulation_steps=8,      # 그래디언트 축적 스텝 (실질 배치 크기 = batch_size * accumulation_steps)
    optim="paged_adamw_32bit",          # 메모리 효율적인 옵티마이저
    save_steps=100,                     # 100 스텝마다 체크포인트 저장 (데이터 양에 따라 조절)
    logging_steps=10,                   # 10 스텝마다 로그 출력
    learning_rate=2e-4,                 # 학습률
    weight_decay=0.001,                 # 가중치 감쇠
    fp16=False,                         # bf16 사용 시 False (bnb_config에서 bf16 사용)
    bf16=True,                          # bfloat16 사용 (GPU 지원 시, Ampere 이상 권장)
    max_grad_norm=0.3,                  # 그래디언트 클리핑
    max_steps=-1,                       # 최대 스텝 수 (-1이면 num_train_epochs 기준)
    warmup_ratio=0.03,                  # 웜업 비율
    group_by_length=True,               # 비슷한 길이의 시퀀스끼리 배치 구성 (메모리 효율 증가)
    lr_scheduler_type="cosine",         # 학습률 스케줄러
    report_to="tensorboard"             # TensorBoard 로깅 사용 (선택 사항)
)
# -------------------------

# --- SFTTrainer 설정 및 학습 시작 ---
# SFTTrainer 사용 (Instruction/Response 형식 데이터에 편리)
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    peft_config=lora_config, # PEFT 설정 전달 (get_peft_model 했어도 전달 필요할 수 있음)
    # dataset_text_field="text", # 만약 데이터셋에 'text' 컬럼만 있다면 지정
    max_seq_length=512,         # 최대 시퀀스 길이 (VRAM 따라 조절)
    tokenizer=tokenizer,
    args=training_arguments,
    packing=False,              # 여러 짧은 시퀀스를 하나로 묶지 않음
)

print("Fine-tuning 시작...")
trainer.train()
# -----------------------------

# --- 학습 완료 후 모델 저장 ---
print("학습 완료. 모델 저장 중...")
# LoRA 어댑터만 저장
trainer.save_model(output_dir)
print(f"모델이 '{output_dir}'에 성공적으로 저장되었습니다.")

# (선택 사항) 토크나이저도 함께 저장
tokenizer.save_pretrained(output_dir)
print(f"토크나이저가 '{output_dir}'에 성공적으로 저장되었습니다.")

# (선택 사항) 학습 후 간단한 추론 테스트
# logging.set_verbosity(logging.CRITICAL)
# pipe = pipeline(task="text-generation", model=model, tokenizer=tokenizer, max_length=200)
# prompt = "여자친구가 이렇게 말했어: 오늘 뭐해?" # 테스트 프롬프트
# result = pipe(f"<s>[INST] {prompt} [/INST]")
# print("\n--- 추론 테스트 ---")
# print(result[0]['generated_text'])
# print("------------------")
# -------------------------
# 스크립트 사용 방법은 채팅창의 설명을 참고하세요.