# Day 5 Quest

평가 세트·HITL·Trace를 통합하고 OTA 변경 검토 시스템의 적용 범위와 한계를 확인합니다.

- 정답 여부뿐 아니라 행동, 예상 문서, Trace 존재를 함께 평가합니다.
- 정보 부족, 근거 없음, 충돌, 검토 필요, 금지 요청을 서로 다른 상태로 처리합니다.
- 사람의 승인·거부는 기록하되 교육 환경에서 실제 외부 작업은 실행하지 않습니다.
- `make day5-check`와 `make final-eval`을 통과시킵니다.

## 작업 위치

- 코드: `src/coursekit/day5_system.py`
- 평가: `data/eval_cases.json`
- 검사: `tests/test_day5.py`

## 실행 순서

1. `make day5-run`으로 사람 검토 전환을 확인합니다.
2. `make final-eval`로 10개 공통 Case를 실행합니다.
3. 위험 오류와 단순 품질 오류를 구분해 평가 Case를 수정합니다.
4. 변경 후 같은 Case를 다시 실행하고 Trace와 최종 상태를 비교합니다.

## 개인 프로젝트 연결

정상·정보 부족·근거 없음·사람 검토·금지 Case를 최소 1개씩 만듭니다. 개인 프로젝트 검사와 평가가 모두 통과해야 합니다.

```bash
make project-check PROJECT=projects/my-project
make project-eval PROJECT=projects/my-project
```

## 완료 증거

- 최소 5개 평가 Case의 기대 행동을 설명합니다.
- 자동 처리·사람 검토·AI 실행 금지 기준을 제시합니다.
- 1페이지 업무 적용 판단서를 완성합니다.
