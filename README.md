# 현대자동차 RAG + Multi-Agent 실습

5일 동안 OTA 변경 검토 업무지원 시스템을 단계적으로 확장하는 교육용 저장소입니다. 교육용 법규·CSMS·TARA·증적 문서를 사용하며, 실제 법규 판단이나 출시 승인을 대신하지 않습니다.

## 5일 결과물

| 일차 | 결과물 |
|---|---|
| Day 1 | 근거·출처·답변 거부가 있는 RAG |
| Day 2 | 평가·재작성·재검색·종료 조건이 있는 LangGraph RAG |
| Day 3 | 요청 검증·권한·Tool 계약·Trace가 있는 Agent Harness |
| Day 4 | 법규·사이버보안 Agent와 Evidence Verifier 협업 |
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

## 원격 SSH — 강사 점검용

교육생의 기본 실습은 웹 Codespaces만으로 진행할 수 있습니다. 강사가 원격으로 환경을 점검할 때는 저장소의 devcontainer에 포함된 SSH 서버 기능을 사용합니다.

기존 Codespace가 SSH 기능 추가 전에 만들어졌다면 컨테이너를 다시 빌드해야 합니다.

```bash
gh codespace list
gh codespace rebuild --full -c <CODESPACE_NAME>
gh codespace ssh -c <CODESPACE_NAME>
```

웹 화면에서는 명령 팔레트의 `Codespaces: Rebuild Container`를 실행하거나 새 Codespace를 만들 수 있습니다. 재빌드 직후 터널 연결이 지연되면 Codespace를 중지한 뒤 다시 시작합니다.

Full Rebuild가 끝난 뒤에도 `postCreateCommand`가 Python 패키지를 설치하는 동안에는 `make check`가 실패할 수 있습니다. Codespaces 화면의 **Running postCreateCommand**가 완료된 뒤 실행하세요.

SSH 접속 후 Codespaces Secret의 주입 여부를 확인합니다.

```bash
gh codespace ssh -c <CODESPACE_NAME>
test -n "$OPENAI_API_KEY" && echo OPENAI_API_KEY_PRESENT
```

Secret의 실제 값은 출력하지 마세요. `OPENAI_API_KEY_PRESENT`만 확인합니다.

## 실습 기준 버전

현재 OTA·법규·CSMS·TARA 시나리오는 `main`을 기준으로 진행합니다. 교육생은 완성 시스템을 먼저 실행한 뒤 `labs/dayN.md`의 요구사항에 따라 해당 일차 코드를 변경하고 자동검사를 실행합니다. 저장소의 기존 `dayN-start`·`dayN-complete` 브랜치는 초기 일반 차량 예제의 이력 보존용이며 이번 과정의 시작점으로 사용하지 않습니다.

## 교육생 작업 방식

1. 완성 시스템을 먼저 실행합니다.
2. 질문·검색 문서·State·Tool·Agent 전달과 중단 이유를 확인합니다.
3. `labs/dayN.md`의 요구사항을 AI에게 전달합니다.
4. 코드를 수정한 뒤 `make dayN-check`를 실행합니다.
5. 새로운 OTA 변경 조건과 문서에 재적용합니다.

## 개인 프로젝트

기본 OTA 데이터를 수정하지 않고 `projects/` 아래의 별도 데이터로 자신의 업무 Case를 실행할 수 있습니다.

```bash
cp -R projects/template projects/my-project
make project-check PROJECT=projects/my-project
make project-day1 PROJECT=projects/my-project QUESTION="내 업무 질문"
make project-eval PROJECT=projects/my-project
```

개인 프로젝트는 문서·정책·역할·평가 Case를 분리해 보존합니다. 상세 단계와 완료 기준은 `projects/README.md`를 확인합니다.

## 복구와 합류

- 기본 교육 코드는 `main`을 기준으로 하며 `git status`로 변경 파일을 확인합니다.
- 개인 프로젝트는 새 폴더에 템플릿을 다시 복사해 복구할 수 있습니다.
- Day별 자동검사가 실패해도 다음 Day에는 완성된 `main` 기준으로 다시 합류할 수 있습니다.
- 실제 기밀·개인정보·API 키는 저장소 파일에 넣지 않습니다.

## 교안과 Codespaces의 역할

- Notion: 개념의 정의, 필요한 이유, 구조 선택 기준, 실행 흐름과 실습 요구사항을 설명합니다.
- Codespaces: 동일한 구조를 실행하고 Trace·근거·정책 결과를 확인하며 코드를 변경합니다.
- `labs/dayN.md`: Notion의 메인 실습을 코드 파일과 자동 검사에 연결합니다.

Codespaces는 교안 전체를 복제하지 않습니다. 개념을 읽은 뒤 실행으로 확인할 수 있는 최소 설명과 완료 기준만 둡니다.

## 안전 범위

- `Mock` 모드는 API 키 없이 결정론적으로 실행됩니다.
- `OpenAI` 모드는 생성과 검색 판단에 API를 사용하지만 정책 판정과 고영향 작업 차단은 코드가 담당합니다.
- 검토 요청은 초안만 만들며 외부 전송, 위험 수용, 법규 적용 상태 변경, 출시 승인을 실행하지 않습니다.
