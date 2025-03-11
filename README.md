# MistralOCR 테스트

미스트랄 AI에서 새로 출시한 MistralOCR을 빠르게 테스트 해봤습니다. 

MistralOCR은 문서 구조 분석 및 OCR을 제공하는데, PDF 문서에서 텍스트, 표, 이미지가 포함된 구조화된 Markdown으로 변환합니다.

다른 멀티모달 LLM 대비 신뢰도가 높다고 미스트랄은 평가하고 있습니다.

샘플 PDF를 돌려본 결과는 result를 참고하세요.


## 시작하기

### 설치

1. 필요한 패키지를 설치합니다:
   ```
   pip install -r requirements.txt
   ```

2. `.env` 파일에 API 키를 설정합니다:
   ```
   MISTRAL_API_KEY=your_api_key_here
   ```
   
   API 키는 미스트랄 AI 홈페이지에서 발급받을 수 있습니다. 2025년 3월 11일 현재는 무료로 베타테스트 중입니다.

### 사용 방법

PDF 파일을 OCR 처리하려면 다음 명령어를 실행하세요:

```bash
python mistralocr_test.py
```

처리된 결과는 `result` 폴더에 마크다운 파일로 저장되며, 추출된 이미지도 같은 폴더에 저장됩니다.

커스텀파일 테스트를 위해서는 코드의 파일 경로를 수정해야 합니다.

## 결과물

- **마크다운 파일**: 추출된 텍스트와 이미지 참조를 포함합니다.
- **이미지 폴더**: PDF에서 추출된 모든 이미지가 저장됩니다.

## 알려진 한계점

현재 베타 버전에서 발견된 몇 가지 한계점:

- 일부 이미지가 추출 과정에서 누락되는 경우가 있습니다.
- 현재는 OCR 처리를 위한 커스텀 프롬프트 설정이 불가합니다.
- 단락(paragraph)에서 줄바꿈이 자연스럽지 않은 경우가 다수 발견됩니다.

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.