.PHONY: install ui check day1-run day1-check day2-run day2-check day3-run day3-check day4-run day4-check day5-run final-eval

install:
	pip install -e ".[dev]"

ui:
	streamlit run app.py --server.address 0.0.0.0 --server.port 8501

check:
	pytest -q

day1-run:
	course day1 "회생제동 단계는 어떻게 조절하나요?"

day1-check:
	pytest -q tests/test_day1.py

day2-run:
	course day2 "브레이크 에너지 회수 세기를 바꾸는 방법은?"

day2-check:
	pytest -q tests/test_day2.py

day3-run:
	course day3 "차량 ID 101의 점검 상태를 알려줘"

day3-check:
	pytest -q tests/test_day3.py

day4-run:
	course day4 "회생제동 단계 변경 방법과 출처를 알려줘"

day4-check:
	pytest -q tests/test_day4.py

day5-run:
	course day5 "차량 ID 101의 제어 값을 변경해줘"

final-eval:
	course eval

