# 개인 프로젝트

기본 OTA 예제를 보존한 채 자신의 업무 Case를 별도 데이터로 실행하는 공간입니다.

## 시작

```bash
cp -R projects/template projects/my-project
make project-check PROJECT=projects/my-project
```

다음 파일만 자신의 업무에 맞게 바꿉니다.

- `project_brief.md`: 해결할 문제·사용자·자동화 금지 범위
- `documents/*.md`: 비식별 교육용 업무 문서
- `policies.json`: 재시도·승인·금지 행동
- `roles.json`: 두 전문 역할과 담당 문서
- `eval_cases.json`: 정상·정보 부족·거절·사람 검토·금지 Case

## Day별 실행

```bash
make project-day1 PROJECT=projects/my-project QUESTION="내 질문"
make project-day2 PROJECT=projects/my-project QUESTION="내 질문"
make project-day3 PROJECT=projects/my-project QUESTION="내 질문"
make project-day4 PROJECT=projects/my-project QUESTION="내 질문"
make project-day5 PROJECT=projects/my-project QUESTION="내 질문"
make project-eval PROJECT=projects/my-project
```

## 완료 기준

- 문서 2개 이상과 평가 Case 5개 이상이 있다.
- 답변의 주장을 원문·문서 ID·버전·페이지로 추적할 수 있다.
- 재검색·중단·사람 검토 조건이 Trace에 남는다.
- 역할별 담당 문서와 전달 책임이 겹치지 않는다.
- 실제 외부 전송·승인·상태 변경은 실행하지 않는다.

## 복구

개인 프로젝트가 망가져도 기본 교육 데이터와 코드는 영향을 받지 않습니다. 다시 시작하려면 새 폴더 이름으로 템플릿을 복사합니다. 기존 개인 폴더를 삭제하거나 덮어쓰기 전에는 필요한 산출물을 먼저 내려받으세요.
