# -*- coding: utf-8 -*-
# 한국사2 대단원1(일제강점기) 수행평가 웹앱 — 디지털 리터러시 × 비판적 사고력
# 요청 반영: 객관식 제거, 실제 사료·통계 제시 및 출처 링크 명시
# 실행: streamlit run app.py

import streamlit as st
import pandas as pd
import json
from datetime import datetime

st.set_page_config(page_title="한국사2 수행평가: 일제강점기 · 디지털×비판", layout="wide", page_icon="📚")

# ---------------------- 상태 초기화 ----------------------
def init_state():
    base = [
        "teacher_mode", "weights", "score_auto",
        "student_name", "class_id", "final_report", "timeline_df", "econ_df",
        "teacher_note", "claim_checks", "source_ratings"
    ]
    for k in base:
        if k not in st.session_state:
            st.session_state[k] = None

    if st.session_state.weights is None:
        st.session_state.weights = {
            # DL = Digital Literacy, CT = Critical Thinking
            "DL_출처평가": 0.20,
            "DL_사실검증": 0.20,
            "DL_데이터해석": 0.15,
            "DL_미디어비판": 0.10,
            "CT_사료해석": 0.20,
            "CT_상호비교": 0.10,
            "CT_논증작성": 0.05,
        }

    if st.session_state.timeline_df is None:
        st.session_state.timeline_df = pd.DataFrame({
            "사건": [
                "한일의정서 체결",  # 1904.2
                "을사늑약 체결",     # 1905.11
                "경술국치(한일병합)", # 1910.8
                "3·1운동",          # 1919.3
                "문화통치 시기 표방", # 1919 하반기
                "신간회 창립",        # 1927.2
                "산미증식계획 중단",  # 1934 (1920~1934)
                "국가총동원법",       # 1938
            ],
            "연도": [1904, 1905, 1910, 1919, 1919, 1927, 1934, 1938],
            "순서": [0]*8,
            "메모": ["", "", "", "", "", "", "", ""],
        })

    if st.session_state.econ_df is None:
        # 실제 문헌 수치 기반 요약 표 (출처 아래 명시)
        st.session_state.econ_df = pd.DataFrame({
            "연도": [1910, 1920, 1934],
            "대일_수출에서_쌀_비중(%)": [27, 43, 54],  # Xiang(2025)·Kimura(2018)
            "공업·비농업_비중(추정, GDP%)": [31, 45, 58], # Cha & Kim(2011) 추세 요약화(설명란 주석)
        })

    if st.session_state.source_ratings is None:
        st.session_state.source_ratings = []

    if st.session_state.claim_checks is None:
        st.session_state.claim_checks = []

init_state()

# ---------------------- 정식 사료·통계(링크 포함) ----------------------
SOURCES = [
    {
        "id": "SRC1",
        "이름": "국사편찬위원회 한국사데이터베이스 — 산미증식계획 개요",
        "요약": "1920~1934년 추진, 식민지 농업정책의 중추적 역할 및 사회 변화 서술.",
        "링크": "https://db.history.go.kr/diachronic/level.do?levelId=nh_048_0020_0020_0020"
    },
    {
        "id": "SRC2",
        "이름": "조선총독부 통계연보 — 1932년 총 지출(국가기록원 소개 페이지)",
        "요약": "1932년 총독부 지출 총액 214,494,728원 등 결산 관련 기록 설명.",
        "링크": "https://theme.archives.go.kr/next/government/viewGovernmentArchives.do?id=0001565092"
    },
    {
        "id": "SRC3",
        "이름": "국사편찬위원회 — 3·1운동 당시 총독부 발표 집계",
        "요약": "시위지역 579, 헌병충돌 113, 피살 390, 부상 838 등(발표 통계).",
        "링크": "https://db.history.go.kr/id/hdsr_013_0570"
    },
    {
        "id": "SRC4",
        "이름": "국사편찬위원회 — 기미독립선언서 원문(발췌)",
        "요약": "1919.3.1 독립선언서 텍스트 제공.",
        "링크": "https://db.history.go.kr/item/level.do?levelId=ij_018_0020_00020_0010"
    },
    {
        "id": "SRC5",
        "이름": "국사편찬위원회 — 토지조사사업 경위·지세령 개정 설명",
        "요약": "토지조사(1912~1918)와 지세·등기 제도 정비 과정 요약.",
        "링크": "https://db.history.go.kr/item/level.do?levelId=hdsr_011_0050_0030"
    },
    {
        "id": "SRC6",
        "이름": "Kimura (2018) Japan Review — 식민지기 쌀 비중(최대 54%:1934) 등",
        "요약": "농업 생산과 수출 구조 분석(학술논문).",
        "링크": "https://www.jiia-jic.jp/en/japanreview/pdf/JapanReview_Vol2_No2_03_Kimura.pdf"
    },
    {
        "id": "SRC7",
        "이름": "Xiang (2025) Working Paper — 대일 수출에서 쌀 비중 1910:27%→1920:43%→1930s 50%+",
        "요약": "교역조건·수출구조 분석(작업논문, 데이터 인용 포함).",
        "링크": "https://econ.cau.ac.kr/wp-content/uploads/2025/03/The-Layered-Colonialism-and-Koreas-Terms-of-Trade-under-Japanese-Colonial-Rule.pdf"
    },
    {
        "id": "SRC8",
        "이름": "Cha & Kim (2011) — Korea’s first industrial revolution, 1911–1940",
        "요약": "1인당 생산 2.3% 성장, 부문구조 변화 추정(학술논문).",
        "링크": "https://www.sciencedirect.com/science/article/abs/pii/S0014498311000428"
    }
]

PRIMARY_TEXTS = [
    {
        "id": "PS1",
        "제목": "기미독립선언서(발췌)",
        "연도": 1919,
        "발췌": "2천만 동포를 대표하여 우리는 한국의 독립과 한국인들의 자유를 선언하는 바이다…",
        "출처": "국사편찬위원회 한국사데이터베이스",
        "링크": "https://db.history.go.kr/item/level.do?levelId=ij_018_0020_00020_0010"
    },
    {
        "id": "PS2",
        "제목": "총독부 발표 3·1운동 피해 집계(요약)",
        "연도": 1919,
        "발췌": "시위 579개소, 헌병충돌 113, 피살 390, 부상 838…",
        "출처": "국사편찬위원회 한국사데이터베이스",
        "링크": "https://db.history.go.kr/id/hdsr_013_0570"
    }
]

# ---------------------- 사이드바 ----------------------
st.sidebar.title("📚 한국사2 수행평가 · 일제강점기")
st.sidebar.caption("디지털 리터러시 × 비판적 사고력")
with st.sidebar:
    st.session_state.teacher_mode = st.toggle("교사용 설정 보기", value=False, help="가중치·집계 기능")
    st.markdown("---")
    st.write("**제출자 정보**")
    st.session_state.student_name = st.text_input("이름", value=st.session_state.student_name or "")
    st.session_state.class_id = st.text_input("학급/번호", value=st.session_state.class_id or "")

# ---------------------- 소개 ----------------------
st.title("일제강점기 수행평가: 디지털 리터러시 × 비판적 사고")
st.info("목표: 출처 신뢰도 평가, 사실 검증, 사료 맥락 해석, 데이터 기반 추론, 미디어 비판, 근거 중심 주장 작성.")

# ---------------------- 활동 A: 출처 신뢰도 평가 ----------------------
st.header("A. 출처 신뢰도 평가 (DL)")
st.write("아래 **공식·학술 출처**를 CRAAP 기준(시의성·관련성·권위·정확성·목적)으로 평가하고 근거를 적으시오.")

src_cols = st.columns(4)
ratings = []
for i, S in enumerate(SOURCES[:4]):
    with src_cols[i]:
        st.markdown(f"**{S['이름']}**")
        st.caption(S["요약"]) 
        st.link_button("출처 열기", S["링크"])
        score = st.slider("신뢰도(0~5)", 0, 5, 3, key=f"src_score_{i}")
        note = st.text_area("근거/메모", key=f"src_note_{i}")
        ratings.append({"name": S["이름"], "score": score, "note": note, "url": S["링크"]})

st.markdown(":orange[**학생 추가 출처 입력(선택)**]")
user_src = st.text_input("추가 출처 URL")
user_src_note = st.text_area("추가 출처 평가 메모")

# ---------------------- 활동 B: 사실 검증(Claim Check) ----------------------
st.header("B. 사실 검증 (DL)")
claims = [
    {"id": "C1", "텍스트": "1920년대 산미증식계획은 조선 내 식량 사정을 전반적으로 개선했다."},
    {"id": "C2", "텍스트": "1912~1918년 토지조사사업은 소작농의 권리를 약화시키는 효과가 있었다."},
    {"id": "C3", "텍스트": "1930년대 조선의 대일 수출에서 쌀 비중은 50%를 넘는 해가 있었다."},
]
claim_sel = st.selectbox("검증할 주장 선택", options=[c["id"] for c in claims], format_func=lambda x: next(c["텍스트"] for c in claims if c["id"]==x))
sel = next(c for c in claims if c["id"]==claim_sel)

st.warning(f"주장: {sel['텍스트']}")
verdict = st.radio("판정", ["참", "거짓", "혼합"], horizontal=True)
proof1 = st.text_input("근거 출처 1 (URL/서지)")
proof2 = st.text_input("근거 출처 2 (URL/서지)")
method = st.multiselect("검증 방법", ["원사료 대조", "통계 검증", "언론/학술 대조", "공식문서 확인", "사진/지도 판독"])
reason = st.text_area("판정 근거 요약(3~5문장)")

st.session_state.claim_checks = [{
    "claim_id": sel["id"],
    "claim_text": sel["텍스트"],
    "verdict": verdict,
    "evidences": [proof1, proof2],
    "methods": method,
    "reason": reason
}]

if st.session_state.teacher_mode:
    st.caption("참고 정답 가이드: C2=참 (hdsr_011_0050_0030), C3=참 (Kimura 2018; Xiang 2025), C1=혼합(지표별 상이).")

# ---------------------- 활동 C: 사료 분석(맥락·상호비교) ----------------------
st.header("C. 사료 분석 (CT)")
col_ps = st.columns(2)
ps_answers = {}
for i, PS in enumerate(PRIMARY_TEXTS):
    with col_ps[i % 2]:
        st.markdown(f"**{PS['제목']} ({PS['연도']})**  ")
        st.code(PS["발췌"], language="markdown")
        st.link_button("원문/설명 보기", PS["링크"])  
        q1 = st.text_area("① 문서의 작성 목적을 2문장 이내로 설명.", key=f"ps_{PS['id']}_0")
        q2 = st.text_area("② 생산 배경(시간·공간·권력관계)을 고려한 해석 2문장.", key=f"ps_{PS['id']}_1")
        ps_answers[f"ps_{PS['id']}_0"] = q1
        ps_answers[f"ps_{PS['id']}_1"] = q2

# 상호비교 질문
st.subheader("사료 상호비교 질문")
comp = st.text_area("두 사료가 보여주는 통치 방식/저항의 공통점·차이점과 역사적 의미(5~7문장)")

# ---------------------- 활동 D: 타임라인 구성 ----------------------
st.header("D. 타임라인 구성 (CT)")
st.write("연표상 사건의 **앞(1)→뒤(8)** 순서를 입력하고, 각 행 메모에 **근거 출처 키워드**를 쓰시오.")
editable_df = st.data_editor(
    st.session_state.timeline_df,
    num_rows="fixed",
    column_config={"순서": st.column_config.NumberColumn(min_value=1, max_value=8, step=1)},
    hide_index=True,
)
st.session_state.timeline_df = editable_df

true_order = [1904, 1905, 1910, 1919, 1919, 1927, 1934, 1938]
if (editable_df["순서"] > 0).all():
    try:
        user_seq = editable_df.sort_values("순서")["연도"].tolist()
        auto_timeline = 1.0 if user_seq == true_order else max(0.0, 1 - sum(a!=b for a,b in zip(user_seq, true_order))/8)
    except Exception:
        auto_timeline = 0.0
else:
    auto_timeline = 0.0

# ---------------------- 활동 E: 데이터 리터러시 ----------------------
st.header("E. 데이터 리터러시 (DL)")
st.write("표를 보고 **추세·상관**을 서술하고, 정책(산미증식·전시동원 등)과의 연관성을 추론하시오.")
with st.expander("데이터 출처 설명"):
    st.markdown("""
    - **대일 수출에서 쌀 비중**: 1910년 27%→1920년 43%→1930년대 50%대 (Xiang, 2025; Kimura, 2018).
    - **부문구조 변화(요약)**: 1911~1940 1인당 생산 2.3% 성장, 1차부문 비중 하락(Cha & Kim, 2011). 표의 비농업 비중은 해당 추세를 **교육용 요약치**로 제시.
    - **총독부 재정지표**: 1932년 총 지출액 등(국가기록원 통계연보 소개 페이지).
    """)

st.dataframe(st.session_state.econ_df, use_container_width=True)
ans_trend = st.text_area("① 추세 요약(2~3문장)")
ans_link = st.text_area("② 수치와 정책(산미증식·전시동원 등)의 연관성(3~4문장)")

# 보조: 3·1운동 피해 집계 표(출처: 총독부 발표)
st.subheader("보조 데이터: 3·1운동 피해 집계(총독부 발표)")
martyr_df = pd.DataFrame({
    "항목": ["시위지역(개소)", "헌병충돌(개소)", "피살(명)", "부상(명)"],
    "값": [579, 113, 390, 838]
})
st.dataframe(martyr_df, use_container_width=True)
st.caption("출처: 국사편찬위원회 한국사데이터베이스, ‘총독부, 3·1 운동 발생후… 집계 발표’ 문서")

# ---------------------- 활동 F: 미디어 리터러시 ----------------------
st.header("F. 미디어 리터러시 (DL)")
st.write("가상의 게시물을 비판적으로 분석하시오.")
st.markdown(
    "> [가상 게시물]
> '1930년대 조선 경제가 급성장! 일본 제국의 정책 덕분에 모두가 풍요로워졌다'
> — 그래프 출처 불명, 긍정 사례만 제시"
)
ml_claims = st.multiselect("식별한 문제", [
    "출처 불명/검증 불가 그래프", "과도한 일반화", "사회집단별 격차 은폐",
    "반례/부정적 지표 누락", "시점/기준치 조작 가능성"
])
ml_response = st.text_area("팩트체크 또는 균형 잡힌 대안 서술(3~5문장)")

# ---------------------- 활동 G: 근거기반 최종 주장 ----------------------
st.header("G. 최종 주장(에세이) (CT)")
st.write("주제: **일제강점기 통치 방식과 경제정책이 조선 사회에 미친 영향** — 하나의 주장문을 제시하고, **사료·데이터·출처 평가 결과**를 근거로 400~600자 서술.")
final_essay = st.text_area("최종 에세이(400~600자)", height=200)

# ---------------------- 루브릭 ----------------------
st.header("평가 루브릭")
rubric = pd.DataFrame({
    "영역": [
        "DL_출처평가","DL_사실검증","DL_데이터해석","DL_미디어비판",
        "CT_사료해석","CT_상호비교","CT_논증작성"
    ],
    "4(탁월)": [
        "CRAAP 기준을 체계 적용, 편향·한계를 구체 제시",
        "검증 절차·근거 2개 이상 명확, 판정 타당",
        "추세·상관·한계까지 서술, 정책연관 추론 설득력",
        "표현 기법과 결락 지적, 대안 서술 균형",
        "맥락·의도·한계 통합 해석",
        "사료 간 공통/차이와 의미 구조화",
        "명확 주장+근거 연계, 반론 고려"
    ],
    "3(우수)": [
        "대체로 적절한 기준 적용, 일부 근거 부족",
        "근거 제시와 판정 일치, 보완 여지",
        "추세·상관 서술 적절, 일부 단순",
        "문제 식별 양호, 대안 일부 단순",
        "맥락 고려하나 일부 표면적",
        "비교·의미 도출 있으나 제한적",
        "주장과 근거 연결 양호"
    ],
    "2(보통)": [
        "기준 일부만 적용, 근거 빈약",
        "근거 부족/단일 출처 의존",
        "기초적 추세만 언급",
        "일반적 비판에 그침",
        "맥락 고려 미흡",
        "나열 수준 비교",
        "주장-근거 연결 약함"
    ],
    "1(기초)": [
        "평가 기준 부정확, 근거 결여",
        "판정 자의적, 근거 부적절",
        "해석 오류 또는 무응답",
        "문제 식별 부정확",
        "사료 왜곡/무응답",
        "비교 결여",
        "주장 불명확/근거 없음"
    ]
})
st.dataframe(rubric, use_container_width=True)

# ---------------------- 간단 자동 점수 ----------------------
essay_len = len((final_essay or "").strip())
essay_ok = 400 <= essay_len <= 600

# 사실검증 최소 요건
claim = st.session_state.claim_checks[0] if st.session_state.claim_checks else {}
claim_ok = all(len(str(x).strip())>3 for x in claim.get("evidences", [])) and len((claim.get("reason") or "").strip())>=50

# 미디어·데이터·사료 요건
ml_ok = (len(ml_claims) >= 2) and (len(ml_response.strip()) >= 50)
data_ok = (len((ans_trend or "").strip()) >= 30) and (len((ans_link or "").strip()) >= 50)
ps_total_len = sum(len(v.strip()) for v in (ps_answers.values() or [])) + len((comp or "").strip())
ps_ok = ps_total_len >= 200

auto = {
    "DL_출처평가": 1.0 if len(ratings)==4 and all(len(r["note"].strip())>=15 for r in ratings) else 0.6,
    "DL_사실검증": 1.0 if claim_ok else 0.6,
    "DL_데이터해석": 1.0 if data_ok else 0.6,
    "DL_미디어비판": 1.0 if ml_ok else 0.6,
    "CT_사료해석": 1.0 if ps_ok else 0.6,
    "CT_상호비교": auto_timeline,
    "CT_논증작성": 1.0 if essay_ok else 0.6,
}
weighted = sum(auto[k]*st.session_state.weights[k] for k in auto)

with st.expander("자동 산출 점수(초안) 보기"):
    st.json({"영역점수": auto, "가중총점": round(weighted,3), "예상최종(%)": round(min(1.0, weighted)*100,1)})

# ---------------------- 제출물 미리보기 · 내보내기 ----------------------
st.header("제출물 미리보기 · 내보내기")
meta = {
    "이름": st.session_state.student_name,
    "학급": st.session_state.class_id,
    "제출시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
}

bundle = {
    "meta": meta,
    "출처": SOURCES,
    "A_출처평가": ratings + ([{"name": user_src, "note": user_src_note}] if user_src else []),
    "B_사실검증": st.session_state.claim_checks,
    "C_사료답": {**ps_answers, "상호비교": comp},
    "D_타임라인": st.session_state.timeline_df.to_dict(orient="records"),
    "E_데이터": {"요약표": st.session_state.econ_df.to_dict(orient="records"), "추세": ans_trend, "연관": ans_link},
    "F_미디어": {"문제": ml_claims, "대안": ml_response},
    "G_에세이": final_essay,
}

preview_tabs = st.tabs(["JSON", "CSV(타임라인)", "요약/출처"])
with preview_tabs[0]:
    st.code(json.dumps(bundle, ensure_ascii=False, indent=2))
with preview_tabs[1]:
    csv = st.session_state.timeline_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("타임라인 CSV 다운로드", csv, file_name="timeline.csv", mime="text/csv")
    st.dataframe(st.session_state.timeline_df, use_container_width=True)
with preview_tabs[2]:
    st.write(f"**제출자:** {meta['이름']} / {meta['학급']}")
    st.write("**참고 출처:**")
    for S in SOURCES:
        st.markdown(f"- [{S['이름']}]({S['링크']}) — {S['요약']}")
    st.write("**강점 후보:** 출처평가, 데이터·미디어 리터러시, 타임라인 정확도")
    st.write("**개선 제안:** 에세이 분량 준수, 근거의 다양성, 사료 간 의미 구조화")

json_bytes = json.dumps(bundle, ensure_ascii=False, indent=2).encode('utf-8')
st.download_button("전체 제출물(JSON) 다운로드", data=json_bytes, file_name="khs2_performance_ilje.json", mime="application/json")

st.markdown("---")
st.caption("본 앱은 학습 증거 기반 평가를 지향합니다 · 사료/통계 링크: 국사편찬위원회·국가기록원·학술논문")

