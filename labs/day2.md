# Day 2 Quest

Day 1 RAG에 LangGraph의 검색 평가·질문 재작성·재검색·안전 종료를 추가합니다.

- `원격 펌웨어 갱신` 질문이 첫 검색에서 실패하고 `무선 소프트웨어 업데이트`로 재작성되는 Trace를 확인합니다.
- `max_retries`를 넘으면 근거 없이 생성하지 않고 종료합니다.
- `make day2-check`가 통과해야 합니다.

## 작업 위치

- 코드: `src/coursekit/day2_graph.py`
- 정책: `data/policies.json`
- 검사: `tests/test_day2.py`

## 실행 순서

1. `make day2-run`으로 첫 검색·재작성·재검색 Trace를 확인합니다.
2. 보존할 업무 조건과 최대 재시도 횟수를 먼저 정의합니다.
3. 재작성·중단 규칙을 변경한 뒤 `make day2-check`를 실행합니다.
4. 무한 반복·조건 손실·근거 없음 Case를 각각 확인합니다.

## 개인 프로젝트 연결

개인 질문 중 표현 차이로 실패하는 질문 하나를 선택하고, 재작성 후에도 보존할 조건과 중단 기준을 기록합니다.

```bash
make project-day2 PROJECT=projects/my-project QUESTION="검색에 실패하는 내 질문"
```

## 완료 증거

- 정상·재검색·중단 경로를 Trace로 구분합니다.
- 재시도 한도를 넘으면 근거 없이 생성하지 않습니다.
- `make day2-check`가 통과합니다.
