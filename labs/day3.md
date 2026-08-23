# Day 3 Quest

RAG 검색·증적 상태·버전 비교·검토 요청 초안 Tool을 선택하는 Agent Harness를 완성합니다.

- Tool 이름·입력·출력·권한을 계약으로 고정합니다.
- 법규 질문의 필수 입력을 검사하고, 고영향 요청은 Tool 실행 전에 중단합니다.
- 위험 수용과 출시 승인은 금지하고, 검토 요청은 초안만 생성합니다.
- 선택한 Tool과 중단 이유를 Trace에 남기고 `make day3-check`를 통과시킵니다.

## 작업 위치

- 코드: `src/coursekit/day3_agent.py`
- 정책: `data/policies.json`
- 검사: `tests/test_day3.py`

## 실행 순서

1. `make day3-run`으로 읽기 Tool의 정상 호출을 확인합니다.
2. 허용·사람 검토·금지 요청을 실행해 결과를 비교합니다.
3. Tool 권한·필수 입력·호출 한도를 수정합니다.
4. `make day3-check`로 실행 전 차단과 Trace를 확인합니다.

## 개인 프로젝트 연결

자신의 업무 기능을 읽기·초안·쓰기·승인으로 나누고 `policies.json`의 승인·금지 행동을 수정합니다.

```bash
make project-day3 PROJECT=projects/my-project QUESTION="내 업무의 상태를 알려줘"
```

## 완료 증거

- 각 Tool의 입력·출력·권한을 설명합니다.
- 고영향 행동은 실행 전에 중단됩니다.
- `make day3-check`가 통과합니다.
