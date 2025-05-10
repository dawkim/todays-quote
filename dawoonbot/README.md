# 나만의 말투를 따라하는 여자친구 맞춤형 챗봇 (DawoonBot)

## 프로젝트 소개

이 프로젝트는 사용자의 카카오톡 대화 내용을 학습하여 사용자의 말투를 모방하는 개인 맞춤형 챗봇을 개발하는 것을 목표로 합니다. 개발된 챗봇은 웹 인터페이스를 통해 여자친구가 쉽게 접근하고 사용할 수 있도록 배포될 예정입니다.

## 주요 목표

-   **말투 모방:** 사용자와 여자친구 간의 카카오톡 대화 데이터를 기반으로 사용자의 고유한 말투, 자주 사용하는 표현, 감성 등을 학습하여 자연스럽게 모방하는 챗봇 구현.
-   **쉬운 사용성:** 여자친구가 별도의 설치나 복잡한 과정 없이 웹 브라우저를 통해 간편하게 챗봇과 대화할 수 있는 인터페이스 제공.
-   **로컬 환경 활용:** 제한된 로컬 컴퓨팅 자원(RTX 3060 Ti, 8GB VRAM) 내에서 모델 Fine-tuning을 수행하여 비용 효율적인 개발 추구.

## 기술 스택 (예정)

-   **언어:** Python
-   **LLM Fine-tuning:**
    -   Hugging Face `transformers`, `peft` (QLoRA), `bitsandbytes`, `accelerate`
    -   PyTorch
    -   **모델:** 8GB VRAM + QLoRA 환경에 적합한 한국어 특화 소형 LLM (예: KoAlpaca, EEVE-Korean 등)
-   **데이터 처리:** `pandas`, `re`, Hugging Face `datasets`
-   **웹 인터페이스:** Streamlit 또는 Gradio
-   **배포:** Hugging Face Spaces 또는 Streamlit Community Cloud

## 개발 단계 (요약)

1.  **데이터 준비:** 카카오톡 대화 내보내기, 파싱, 정제 (개인정보 보호 필수), 학습 데이터셋 구성.
2.  **모델 선정 및 Fine-tuning:** QLoRA 기법을 활용하여 로컬 환경에서 선택된 소형 LLM Fine-tuning.
3.  **웹 인터페이스 개발:** Streamlit/Gradio를 사용하여 사용자 친화적인 채팅 UI 구현.
4.  **배포:** Hugging Face Spaces 등 PaaS 플랫폼을 활용하여 웹 앱 배포.

## 참고

-   자세한 개발 절차 및 고려사항은 `수행계획서.md` 파일을 참고하세요.