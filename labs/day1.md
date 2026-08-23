# Day 1 Quest

OTA 변경 문서를 검색하는 `RAGSystem.ask()`를 완성해 `answer`, `citations`, `status`를 반환하세요.

- 검색 문서의 ID·버전·시장·차종·페이지·섹션·원문 근거를 보존합니다.
- 승인 상태의 문서만 검색 대상으로 사용합니다.
- 문서에 없는 질문은 `insufficient_evidence`로 종료합니다.
- `make day1-check`가 통과해야 합니다.

완료 결과는 “답변을 잘 생성했다”가 아니라, 어떤 승인 문서의 어느 근거로 답했는지 설명할 수 있어야 합니다.
