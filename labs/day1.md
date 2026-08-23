# Day 1 Quest

OTA 변경 문서를 검색하는 `RAGSystem.ask()`를 완성해 `answer`, `citations`, `status`를 반환하세요.

- 검색 문서의 ID·버전·시장·차종·페이지·섹션·원문 근거를 보존합니다.
- 승인 상태의 문서만 검색 대상으로 사용합니다.
- 문서에 없는 질문은 `insufficient_evidence`로 종료합니다.
- `make day1-check`가 통과해야 합니다.

완료 결과는 “답변을 잘 생성했다”가 아니라, 어떤 승인 문서의 어느 근거로 답했는지 설명할 수 있어야 합니다.

## 작업 위치

- 코드: `src/coursekit/day1_rag.py`, `src/coursekit/documents.py`
- 데이터: `data/documents/`
- 검사: `tests/test_day1.py`

## 실행 순서

1. `make day1-run`으로 완성 결과를 먼저 확인합니다.
2. 정상 질문과 문서에 없는 질문의 `status`·`citations`·`trace`를 비교합니다.
3. AI에게 위 요구사항과 수정할 파일을 전달하고 변경 계획을 먼저 받습니다.
4. 변경 후 `make day1-check`를 실행합니다.

## 개인 프로젝트 연결

`projects/template`을 별도 폴더로 복사하고 업무 문서 2개, 정상 질문 하나, 근거 없음 질문 하나를 준비합니다. 기본 `data/`는 수정하지 않습니다. Day 1에는 `project_brief.md`와 `documents/`만 자신의 소재로 바꿉니다.

```bash
make project-check-day1 PROJECT=projects/my-project
make project-day1 PROJECT=projects/my-project QUESTION="내 업무 질문"
```

## 완료 증거

- 답변 주장 하나를 원문·문서 ID·버전·페이지로 연결할 수 있습니다.
- 근거가 없는 질문은 답변하지 않습니다.
- `make day1-check`가 통과합니다.
