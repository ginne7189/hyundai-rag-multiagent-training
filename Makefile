.PHONY: install ui check day1-run day1-check day2-run day2-check day3-run day3-check day4-run day4-check day5-run day5-check final-eval project-check-day1 project-check project-day1 project-day2 project-day3 project-day4 project-day5 project-eval

PROJECT ?= projects/template
QUESTION ?= 프로젝트 A의 변경 절차와 필요한 근거는?

install:
	pip install -e ".[dev]"

ui:
	streamlit run app.py --server.address 0.0.0.0 --server.port 8501

check:
	pytest -q

day1-run:
	course day1 "X 차종 OTA 업데이트에 필요한 조건과 출처는?"

day1-check:
	pytest -q tests/test_day1.py

day2-run:
	course day2 "X 차종 원격 펌웨어 갱신 조건은?"

day2-check:
	pytest -q tests/test_day2.py

day3-run:
	course day3 "차종 X OTA 변경의 증적 제출 상태를 알려줘"

day3-check:
	pytest -q tests/test_day3.py

day4-run:
	course day4 "X 차종 OTA 변경의 적용 법규와 사이버보안 증적을 알려줘"

day4-check:
	pytest -q tests/test_day4.py

day5-run:
	course day5 "차종 X OTA 검토 요청을 담당자에게 발송해줘"

day5-check:
	pytest -q tests/test_day5.py

final-eval:
	course eval

project-check:
	course project-check --data-dir "$(PROJECT)"

project-check-day1:
	course project-check-day1 --data-dir "$(PROJECT)"

project-day1:
	course day1 "$(QUESTION)" --data-dir "$(PROJECT)"

project-day2:
	course day2 "$(QUESTION)" --data-dir "$(PROJECT)"

project-day3:
	course day3 "$(QUESTION)" --data-dir "$(PROJECT)"

project-day4:
	course day4 "$(QUESTION)" --data-dir "$(PROJECT)"

project-day5:
	course day5 "$(QUESTION)" --data-dir "$(PROJECT)"

project-eval:
	course eval --data-dir "$(PROJECT)"
