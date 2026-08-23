import streamlit as st

st.set_page_config(page_title="RAG + Multi-Agent", layout="wide")
st.title("현대자동차 RAG + Multi-Agent 실습")
st.info("저장소의 일차별 브랜치를 선택해 실습합니다. 현재 브랜치의 기능은 터미널 명령으로 확인하세요.")
st.code("make day1-run\nmake day1-check", language="bash")

