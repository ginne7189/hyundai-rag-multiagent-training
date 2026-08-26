# Day 4 — 역할을 나눈 Multi-Agent Harness

## A. 코드 실행 전에 구조 확인하기

### A-1. 단일 Agent Harness 확인

`ai-agent-harness-starter`의 `AGENTS.md`, `knowledge/`, `SKILL.md`, `templates/`가
각각 원칙, 지식, 처리 순서, 결과 형식을 맡는지 확인합니다.

### A-2. Multi-Agent로 역할 나누기

한 Agent의 일을 법규 Specialist, 사이버보안 Specialist, Evidence Verifier로 나눕니다.
`role-design.md`와 `handoff-contract.md`에 각 역할의 입력, 출력, 금지 행동을 적습니다.

### A-3. 개인 프로젝트 설계

자신의 업무에서 자료, 권한 또는 완료 조건이 다른 역할 두 개를 고르고, 두 역할이
전달할 값을 정합니다. 역할을 많이 만드는 것이 아니라 책임이 실제로 다를 때만 나눕니다.

## B. 패키지로 분리된 코드 실행하기

### B-1. 파일별 책임 확인

- `specialists.py`: 역할별 검색 범위
- `contracts.py`: 역할 사이에 전달할 값과 누락 검사
- `verifier.py`: 근거·버전·답변 일치 여부 검사
- `orchestrator.py`: 역할 실행 순서와 다음 경로 결정
- `harness.py`: 역할과 규칙을 준비하고 하나의 실행 입구 제공

### B-2. 정상 실행

```bash
make day4-run
```

Trace에서 `orchestrator=start`, 각 Specialist, Handoff, Verifier,
`route=finalize` 순서를 확인합니다.

### B-3. 실패 조건과 완료 검사

```bash
make day4-check
```

오래된 문서, 근거와 맞지 않는 답변, 인용이 빠진 Handoff가 차단되는지 확인합니다.

## 이 실습에서 선택한 패턴

- Orchestrator: 정해진 순서로 역할을 호출합니다.
- Specialist/Subagent: 법규와 사이버보안 자료 범위를 나눕니다.
- Handoff: 답변, 인용, 상태, Trace를 다음 역할에 전달합니다.
- Verifier: 최종 출력 전에 독립적으로 근거를 검사합니다.
- Parallel: 개념과 확장 항목으로만 다룹니다. 기본 코드는 실행 순서를 보기 쉽게 순차 실행합니다.
- Router: 모든 질문에 두 분야 확인이 필요한 현재 문제에는 사용하지 않습니다.

## 개인 프로젝트 코드 실행

개인 프로젝트의 `roles.json`에서 두 전문 역할과 담당 문서를 지정합니다. 역할을 늘리기 전에 두 역할의 자료와 완료 조건이 실제로 다른지 확인합니다.

```bash
make project-day4 PROJECT=projects/my-project QUESTION="내 업무 질문"
```

완료 증거는 역할별 입력·출력·금지 행동, Handoff 누락 처리, 최초 오류 역할이 표시된 Trace, `make day4-check` 통과입니다.
