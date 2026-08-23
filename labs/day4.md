# Day 4 Quest

법규 Agent와 사이버보안 Agent가 근거를 각각 수집하고 Evidence Verifier가 합친 결과를 검사하도록 완성합니다.

- 두 역할이 검색할 수 있는 문서를 분리합니다.
- Handoff에 답변과 인용 근거를 함께 전달합니다.
- 검증 역할은 허용 문서, 최신 버전, 원문 근거를 확인합니다.
- `make day4-check`가 통과해야 합니다.

## 작업 위치

- 코드: `src/coursekit/day4_multiagent.py`
- 역할: `data/roles.json` 또는 개인 프로젝트의 `roles.json`
- 검사: `tests/test_day4.py`

## 실행 순서

1. `make day4-run`으로 두 역할과 Verifier의 Trace를 확인합니다.
2. 역할별 담당 문서와 전달 필드를 적습니다.
3. 가짜 출처·구버전·원문 누락 Case를 실행합니다.
4. 검증 기준을 수정하고 `make day4-check`를 실행합니다.

## 개인 프로젝트 연결

`roles.json`에서 두 전문 역할과 담당 문서를 지정합니다. 역할을 늘리기 전에 두 역할의 책임이 실제로 다른지 확인합니다.

```bash
make project-day4 PROJECT=projects/my-project QUESTION="내 업무 질문"
```

## 완료 증거

- 역할별 입력·출력·금지 행동을 구분합니다.
- 전달 누락과 최초 오류 역할을 Trace에서 찾습니다.
- `make day4-check`가 통과합니다.
