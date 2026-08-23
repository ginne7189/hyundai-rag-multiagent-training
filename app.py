import os
from pathlib import Path

import streamlit as st

from coursekit.day1_rag import RAGSystem
from coursekit.day2_graph import AdaptiveRAG
from coursekit.day3_agent import AgentHarness
from coursekit.day4_multiagent import SearchAndVerifySystem
from coursekit.day5_system import OperationalSystem
from coursekit.project import validate_project

st.set_page_config(page_title="RAG + Multi-Agent", layout="wide")
st.title("현대자동차 RAG + Multi-Agent 실습")
data_dir = st.sidebar.text_input("데이터 폴더", os.getenv("COURSE_DATA_DIR", "data"))
document_dir = Path(data_dir) / "documents"
day = st.sidebar.selectbox("실행 단계", ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"])
question = st.text_input("질문", "X 차종 OTA 변경의 적용 법규와 사이버보안 증적을 알려줘")
approval = None
if day == "Day 5":
    approval_label = st.sidebar.selectbox("사람 검토 결과", ["미결정", "승인", "거부"])
    approval = {"승인": "approve", "거부": "reject"}.get(approval_label)
if st.button("실행"):
    systems = {
        "Day 1": lambda: RAGSystem(document_dir=document_dir).ask(question),
        "Day 2": lambda: AdaptiveRAG(document_dir=document_dir).ask(question),
        "Day 3": lambda: AgentHarness(data_dir=data_dir).run(question),
        "Day 4": lambda: SearchAndVerifySystem(data_dir=data_dir).run(question),
        "Day 5": lambda: OperationalSystem(data_dir=data_dir).run(
            question, approval=approval
        ),
    }
    result = systems[day]()
    st.subheader("답변")
    st.write(result.answer)
    st.subheader("전체 결과")
    st.json(result.model_dump())
    st.subheader("Trace")
    st.code("\n".join(result.trace))

if day == "Day 5" and st.sidebar.button("전체 평가 실행"):
    st.sidebar.json(OperationalSystem(data_dir=data_dir).evaluate().model_dump())

if data_dir != "data" and st.sidebar.button("개인 프로젝트 검사"):
    st.sidebar.json(validate_project(data_dir))
