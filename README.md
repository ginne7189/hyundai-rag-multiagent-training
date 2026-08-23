# 현대자동차 RAG + Multi-Agent 실습

5일 동안 하나의 문서 기반 업무지원 시스템을 단계적으로 확장하는 교육용 저장소입니다.

## 5일 결과물

| 일차 | 결과물 |
|---|---|
| Day 1 | 근거·출처·답변 거부가 있는 RAG |
| Day 2 | 평가·재작성·재검색·종료 조건이 있는 LangGraph RAG |
| Day 3 | RAG와 업무 Tool을 안전하게 선택하는 Agent |
| Day 4 | Search Agent와 Evidence Verifier 협업 |
| Day 5 | 평가·HITL·Trace를 포함한 통합 시스템 |

## Codespaces 시작

1. `Code` → `Codespaces` → `Create codespace`를 선택합니다.
2. 설치가 끝나면 `make check`를 실행합니다.
3. 화면형 데모는 `make ui`로 실행합니다.

## 실행 모드

기본값은 API 키가 없어도 실행되는 Mock 모드입니다.

```bash
cp .env.example .env
make check
make ui
```

OpenAI API를 사용할 때는 Codespaces Secret에 `OPENAI_API_KEY`를 등록하고 다음 값을 설정합니다.

```bash
export COURSE_MODE=openai
export OPENAI_MODEL=gpt-5.4-mini
export OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

API 키를 `.env`나 Git에 커밋하지 마세요.

## 일차별 브랜치

```text
day1-start  → day1-complete
day2-start  → day2-complete
day3-start  → day3-complete
day4-start  → day4-complete
day5-start  → day5-complete
```

전날 실습을 완료하지 못해도 다음 날 `dayN-start`에서 시작할 수 있습니다.

## 교육생 작업 방식

1. 완성 시스템을 먼저 실행합니다.
2. 질문·검색 문서·State·Tool·Agent 전달 내용을 확인합니다.
3. `labs/dayN.md`의 요구사항을 AI에게 전달합니다.
4. 코드를 수정한 뒤 `make dayN-check`를 실행합니다.
5. 비공개 질문과 새 문서에 재적용합니다.

