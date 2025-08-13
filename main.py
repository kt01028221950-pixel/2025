# -*- coding: utf-8 -*-
# 한국사2 대단원1(일제강점기) 수행평가 웹앱
# 목표: 디지털 리터러시 역량 + 비판적 사고력 역량 강화
# 사용: streamlit run app.py

import streamlit as st
import pandas as pd
import json
from io import StringIO
from datetime import datetime

st.set_page_config(page_title="한국사2 수행평가: 일제강점기 · 디지털×비판", layout="wide", page_icon="📚")

# ---------------------- 유틸 ----------------------
def init_state():
    keys = [
        "teacher_mode", "weights", "answers_mc", "score_auto", "score_rubric",
        "student_name", "class_id", "final_report", "timeline_df", "econ_df",
        "teacher_note", "claim_checks", "source_ratings"
    ]
    for k in keys:
        if k not in st.session_state:
            st.session_state[k] = None

    if st.session_state.weights is None:
        st.session_state.weights = {
            "DL_출처평가": 0.15,
            "DL_사실검증": 0.15,
            "DL_데이터해석": 0.10,
            "DL_미디어비판": 0.10,
            "CT_사료해석": 0.20,
            "CT_상호비교": 0.15,
            "CT_논증작성": 0.15,
        }

    if st.session_state.answers_mc is None:
        st.session_state.answers_mc = {}

    if st.session_state.score_auto is None:
        st.session_state.score_auto = {}

    if st.session_state.score_rubric is None:
        st.session_state.score_rubric = {}

    if st.session_state.timeline_df is None:
        st.session_state.timeline_df = pd.DataFrame({
            "사건": [
                "한일의정서 체결",  # 1904.2
                "을사늑약 체결",     # 1905.11
                "경술국치(한일병합)", # 1910.8
                "3·1운동",          # 1919.3
                "문화통치 시기 시작", # 1919 하반기
                "신간회 창립",        # 1927.2
                "농촌진흥운동",       # 1932
                "국가총동원법",       # 1938
            ],
            "연도": [1904, 1905, 1910, 1919, 1919, 1927, 1932, 1938],
            "순서": [0]*8,
        })

    if st.session_state.econ_df is None:
        st.session_state.econ_df = pd.DataFrame({
            "연도": [1915, 1920, 1925, 1930, 1935, 1940],
            "쌀_수탈량(가정지표)": [10, 15, 19, 25, 33, 45],
            "조선내_공업생산지수(=1935기준)": [55, 60, 68, 80, 100, 130],
            "일본향_수출비중(%)": [48, 52, 57, 63, 70, 78],
        })

    if st.session_state.source_ratings is None:
        st.session_state.source_ratings = []

    if st.session_state.claim_checks is None:
        st.session_state.claim_checks = []

init_state()

# ---------------------- 데이터(예시 사료/출처) ----------------------
PRIMARY_SOURCES = [
    {
        "id": "PS1",
        "제목": "무단통치기 헌병경찰 통보문(발췌/가상 재구성)",
        "연도": 1912,
        "발췌": "…조선인 거주지의 야간 통행 단속을 강화하고, 집회·결사 활동은 사전 허가제로 한다…",
        "질문": [
            "이 문서의 작성 목적을 2문장 이내로 설명하시오.",
            "사료의 생산 배경(시간·공간·권력관계)을 고려한 해석을 2문장 이내로 제시하시오.",
        ],
        "정답포인트": ["치안통제·저항 억제", "무단통치·헌병경찰·통치 합리화"]
    },
    {
        "id": "PS2",
        "제목": "토지조사사업 공고문(발췌/가상 재구성)",
        "연도": 1912,
        "발췌": "…토지 소유권은 신고하지 않으면 무주지로 간주하여 국유지로 편입한다…",
        "질문": [
            "공고문의 핵심 조항과 농민에게 미칠 경제적 영향을 간단히 쓰시오.",
            "이 사료와 관련하여 나타난 사회·경제 구조 변화를 1가지 제시하시오.",
        ],
        "정답포인트": ["신고주의·소유권 박탈 위험", "지주제 강화/수탈 심화/경작권 약화"]
    },
]

# 사실 검증용 주장(혼합/참/거짓 예시)
CLAIMS = [
    {
        "id": "C1",
        "텍스트": "1930년대 이후에도 일본은 조선의 언론·출판·집회를 광범위하게 허용했다.",
        "정답": "거짓",
        "힌트": "전시체제 강화·사상통제 확대" 
    },
    {
        "id": "C2",
        "텍스트": "토지조사사업은 지주의 권리를 강화하는 결과를 낳았고, 소작농의 지위는 약화되었다.",
        "정답": "참",
        "힌트": "신고주의·지주제 심화"
    },
    {
        "id": "C3",
        "텍스트": "3·1운동 직후 총독부는 문화통치를 표방하며 일부 제도를 완화하였다.",
        "정답": "혼합",
        "힌트": "표면적 완화 vs. 근본 통치기반 유지"
    },
]

# 객관식(자동채점) — 개념·맥락 파악
MC_ITEMS = [
    {
        "id": "MC1",
        "문항": "무단통치기의 특징으로 옳은 것은?",
        "선지": [
            "보통·평등·비밀선거의 실시",
            "헌병경찰제와 즉결처분권의 광범위한 적용",
            "산미증식계획의 본격 추진",
            "조선공산당 합법화"
        ],
        "정답": 1
    },
    {
        "id": "MC2",
        "문항": "토지조사사업의 직접적 결과와 거리가 가장 먼 것은?",
        "선지": [
            "경작권의 법적 약화",
            "지주의 권한 강화",
            "소작농의 지위 향상",
            "지세 수입의 증대"
        ],
        "정답": 2
    },
    {
        "id": "MC3",
        "문항": "다음 정책 가운데 전시동원체제와 가장 밀접한 것은?",
        "선지": [
            "내선일체 선전 강화",
            "광무개혁 추진",
            "갑오개혁 실시",
            "독립협회 결성"
        ],
        "정답": 0
    },
]

# ---------------------- 사이드바 ----------------------
st.sidebar.title("📚 한국사2 수행평가 · 일제강점기")
st.sidebar.caption("디지털 리터러시 × 비판적 사고력")
with st.sidebar:
    st.session_state.teacher_mode = st.toggle("교사용 설정 보기", value=False, help="가중치·정답·집계 기능")
    st.markdown("---")
    st.write("**제출자 정보**")
    st.session_state.student_name = st.text_input("이름", value=st.session_state.student_name or "")
    st.session_state.class_id = st.text_input("학급/번호", value=st.session_state.class_id or "")

# ---------------------- 소개 ----------------------
st.title("일제강점기 수행평가: 디지털 리터러시 × 비판적 사고")
st.info("목표: 출처의 신뢰도 평가, 사실 검증, 사료의 맥락적 해석, 데이터 기반 추론, 미디어 비판, 근거 중심 주장의 작성.")

# ---------------------- 교사용 설정 ----------------------
if st.session_state.teacher_mode:
    st.subheader("교사용 설정")
    st.write("평가 영역 가중치(총합 1.0)")
    cols = st.columns(4)
    wkeys = list(st.session_state.weights.keys())
    for i, k in enumerate(wkeys):
        with cols[i % 4]:
            st.session_state.weights[k] = st.number_input(k, min_value=0.0, max_value=1.0, step=0.05, value=float(st.session_state.weights[k]))
    total_w = sum(st.session_state.weights.values())
    st.caption(f"가중치 합계: **{total_w:.2f}** (1.00 권장)")
    st.session_state.teacher_note = st.text_area("교사 메모(선택)", value=st.session_state.teacher_note or "")
    st.markdown("---")

# ---------------------- 활동 A: 출처 신뢰도 평가 ----------------------
st.header("A. 출처 신뢰도 평가 (DL)")
st.write("아래 제공 출처 3종을 **CRAAP 기준(시의성·관련성·권위·정확성·목적)**으로 평가하고 근거를 적으시오.")

sample_sources = [
    {
        "이름": "신문 사설(1932, 가상)",
        "요약": "산미증식계획의 성과를 강조하며 농민의 희생은 불가피하다고 주장.",
        "링크": "https://example.com/editorial1932"
    },
    {
        "이름": "총독부 통계연보(1935, 가상)",
        "요약": "쌀 수출 증가와 공업생산지수 수치 제시.",
        "링크": "https://example.com/stat1935"
    },
    {
        "이름": "구술자료(1975, 가상)",
        "요약": "1930년대 농촌의 소작 관계와 수탈 체험 진술.",
        "링크": "https://example.com/oral1975"
    },
]

src_cols = st.columns(3)
ratings = []
for i, S in enumerate(sample_sources):
    with src_cols[i]:
        st.markdown(f"**{S['이름']}**")
        st.caption(S["요약"]) 
        st.link_button("출처 보기", S["링크"], help="외부 링크(가상)")
        score = st.slider("신뢰도(0~5)", 0, 5, 3, key=f"src_score_{i}")
        note = st.text_area("근거/메모", key=f"src_note_{i}")
        ratings.append({"name": S["이름"], "score": score, "note": note})

st.session_state.source_ratings = ratings

st.markdown(":orange[**학생 추가 출처 입력(선택)**]")
user_src = st.text_input("추가 출처 URL")
user_src_note = st.text_area("추가 출처 평가 메모")

# ---------------------- 활동 B: 사실 검증(Claim Check) ----------------------
st.header("B. 사실 검증 (DL)")
st.write("무작위 주장 1개를 선택해 사실 여부를 판단하고, 최소 2개의 근거 출처를 제시하시오.")

claim_ids = [c["id"] for c in CLAIMS]
claim_sel = st.selectbox("검증할 주장 선택", options=claim_ids, format_func=lambda x: next(c["텍스트"] for c in CLAIMS if c["id"]==x))
sel_claim = next(c for c in CLAIMS if c["id"]==claim_sel)

st.warning(f"주장: {sel_claim['텍스트']}")
verdict = st.radio("판정", ["참", "거짓", "혼합"], horizontal=True)
proof1 = st.text_input("근거 출처 1 (URL/서지)")
proof2 = st.text_input("근거 출처 2 (URL/서지)")
method = st.multiselect("검증 방법", ["원사료 대조", "통계 검증", "언론/학술 대조", "공식문서 확인", "사진/지도 판독"])
reason = st.text_area("판정 근거 요약(3~5문장)")

st.session_state.claim_checks = [{
    "claim_id": claim_sel["id"] if isinstance(claim_sel, dict) else claim_sel,
    "claim_text": sel_claim["텍스트"],
    "verdict": verdict,
    "evidences": [proof1, proof2],
    "methods": method,
    "reason": reason
}]

# 자동 피드백(정답 공개는 교사용)
if st.session_state.teacher_mode:
    st.caption(f"정답 가이드: {sel_claim['정답']} (힌트: {sel_claim['힌트']})")

# ---------------------- 활동 C: 사료 분석(맥락·상호비교) ----------------------
st.header("C. 사료 분석 (CT)")
col_ps = st.columns(2)
ps_answers = {}
for i, PS in enumerate(PRIMARY_SOURCES):
    with col_ps[i % 2]:
        st.markdown(f"**{PS['제목']} ({PS['연도']})**")
        st.code(PS["발췌"], language="markdown")
        for qi, q in enumerate(PS["질문"]):
            key = f"ps_{PS['id']}_{qi}"
            ans = st.text_area(q, key=key)
            ps_answers[key] = ans

# 상호비교 질문
st.subheader("사료 상호비교 질문")
comp = st.text_area("두 사료가 보여주는 통치 방식의 공통점/차이점과 그 역사적 의미를 기술(5~7문장)")

# ---------------------- 활동 D: 타임라인 구성 ----------------------
st.header("D. 타임라인 구성 (CT)")
st.write("연표상 사건의 **앞(1)→뒤(8)** 순서를 입력하고, 근거 1문장을 각 행 메모에 적으시오.")
editable_df = st.data_editor(
    st.session_state.timeline_df,
    num_rows="fixed",
    column_config={"순서": st.column_config.NumberColumn(min_value=1, max_value=8, step=1)},
    hide_index=True,
)
st.session_state.timeline_df = editable_df

# 자동 채점(부분)
true_order = [1904, 1905, 1910, 1919, 1919, 1927, 1932, 1938]
if (editable_df["순서"] > 0).all():
    try:
        # 사용자가 입력한 순서에 따라 연도를 재정렬
        user_seq = editable_df.sort_values("순서")["연도"].tolist()
        auto_timeline = 1.0 if user_seq == true_order else max(0.0, 1 - sum(a!=b for a,b in zip(user_seq, true_order))/8)
    except Exception:
        auto_timeline = 0.0
else:
    auto_timeline = 0.0

# ---------------------- 활동 E: 데이터 리터러시 ----------------------
st.header("E. 데이터 리터러시 (DL)")
st.write("표를 보고 **추세·상관**을 서술하고, 정책과의 연관성을 추론하시오.")
st.dataframe(st.session_state.econ_df, use_container_width=True)
ans_trend = st.text_area("① 추세 요약(2~3문장)")
ans_link = st.text_area("② 수치와 정책(산미증식·전시동원 등)의 연관성(3~4문장)")

# ---------------------- 활동 F: 미디어 리터러시(사회관계망 게시물 분석) ----------------------
st.header("F. 미디어 리터러시 (DL)")
st.write("가상의 게시물을 비판적으로 분석하시오.")
st.markdown(
    "> [가상 게시물]\n> '1930년대 조선 경제가 급성장! 일본 제국의 정책 덕분에 모두가 풍요로워졌다'\n> — 그래프 출처 불명, 긍정 사례만 제시"
)
ml_claims = st.multiselect("식별한 문제", [
    "출처 불명/검증 불가 그래프", "선정적 표현/과도한 일반화", "사회집단별 격차 은폐",
    "반례/부정적 지표 누락", "시점/기준치 조작 가능성"
])
ml_response = st.text_area("팩트체크 또는 균형 잡힌 대안 서술(3~5문장)")

# ---------------------- 활동 G: 근거기반 최종 주장(미니 에세이) ----------------------
st.header("G. 최종 주장(에세이) (CT)")
st.write("주제: **일제강점기 통치 방식과 경제정책이 조선 사회에 미친 영향** — 하나의 주장문을 제시하고, **사료·데이터·출처 평가 결과**를 근거로 400~600자 서술.")
final_essay = st.text_area("최종 에세이(400~600자)", height=200)

# ---------------------- 객관식 자동 채점 ----------------------
st.header("객관식 문항(자동 채점)")
for item in MC_ITEMS:
    st.write(f"**{item['문항']}**")
    choice = st.radio("선택", list(range(len(item['선지']))), format_func=lambda i: item['선지'][i], key=item['id'])
    st.session_state.answers_mc[item['id']] = choice

# 자동 채점 결과
correct = 0
for item in MC_ITEMS:
    if st.session_state.answers_mc.get(item['id']) == item['정답']:
        correct += 1
mc_score = correct / len(MC_ITEMS)

# ---------------------- 루브릭 ----------------------
st.header("평가 루브릭")
rubric = pd.DataFrame({
    "영역": [
        "DL_출처평가","DL_사실검증","DL_데이터해석","DL_미디어비판",
        "CT_사료해석","CT_상호비교","CT_논증작성"
    ],
    "4(탁월)": [
        "CRAAP 기준을 체계적으로 적용, 편향·한계를 구체 제시",
        "검증 절차·근거 2개 이상 명확, 판정의 타당성 높음",
        "추세·상관·한계까지 서술, 정책연관 추론 설득력",
        "표현 기법과 결락 지적, 대안 서술 균형 잡힘",
        "사료 맥락·의도·한계 통합 해석",
        "사료 간 공통/차이와 의미를 구조화",
        "명확한 주장+근거 연계, 반론 고려"
    ],
    "3(우수)": [
        "대체로 적절한 기준 적용, 일부 근거 부족",
        "근거 제시와 판정 일치하나 보완 여지",
        "추세·상관 서술 적절, 일부 해석 단순",
        "문제 식별 양호, 대안 서술 일부 단순",
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

# ---------------------- 자동 점수 산출(초안) ----------------------
# 가벼운 자동평가: 객관식, 타임라인, 분량·충실도 체크 기반

# 에세이 분량 체크
essay_len = len(final_essay.strip())
essay_ok = 400 <= essay_len <= 600

# 사실검증 정답 일치도(교사용에서만 비교)
claim_auto = None
if st.session_state.teacher_mode:
    claim_auto = 1.0 if verdict == sel_claim["정답"] else (0.5 if (sel_claim["정답"]=="혼합" and verdict in ["참","거짓"]) else 0.0)
else:
    # 학생 모드에서는 항상 중립 점수(검증 절차 중심)
    claim_auto = 0.7 if len(reason.strip())>=50 and all(len(x.strip())>3 for x in [proof1, proof2]) else 0.4

# 미디어 리터러시 최소 요건
ml_ok = (len(ml_claims) >= 2) and (len(ml_response.strip()) >= 50)

# 데이터 해석 최소 요건
data_ok = (len(ans_trend.strip()) >= 30) and (len(ans_link.strip()) >= 50)

# 출처평가 최소 요건(3개 모두 점수+근거)
src_ok = all((r["score"] is not None) and (len(str(r["note"]).strip())>=15) for r in st.session_state.source_ratings)

# 사료 해석 충실도: 각 답변 길이 합
ps_total_len = sum(len(v.strip()) for v in ps_answers.values()) + len(comp.strip())
ps_ok = ps_total_len >= 200

# 영역별 자동초점수(0~1)
auto = {
    "DL_출처평가": 1.0 if src_ok else 0.5,
    "DL_사실검증": claim_auto,
    "DL_데이터해석": 1.0 if data_ok else 0.5,
    "DL_미디어비판": 1.0 if ml_ok else 0.5,
    "CT_사료해석": 1.0 if ps_ok else 0.5,
    "CT_상호비교": auto_timeline,
    "CT_논증작성": 1.0 if essay_ok else 0.5,
}

# 객관식 가산점(최대 +0.1)
auto_bonus = 0.1 * mc_score

weighted = sum(auto[k]*st.session_state.weights[k] for k in auto)
final_auto_score = min(1.0, weighted + auto_bonus)

with st.expander("자동 산출 점수(초안) 보기"):
    st.json({"영역점수": auto, "객관식가산": round(auto_bonus,3), "가중총점": round(weighted,3), "예상최종": round(final_auto_score*100,1)})

# ---------------------- 제출물 미리보기 & 내보내기 ----------------------
st.header("제출물 미리보기 · 내보내기")
meta = {
    "이름": st.session_state.student_name,
    "학급": st.session_state.class_id,
    "제출시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
}

bundle = {
    "meta": meta,
    "A_출처평가": st.session_state.source_ratings + ([{"name": user_src, "note": user_src_note}] if user_src else []),
    "B_사실검증": st.session_state.claim_checks,
    "C_사료답": ps_answers | {"상호비교": comp},
    "D_타임라인": st.session_state.timeline_df.to_dict(orient="records"),
    "E_데이터": {"추세": ans_trend, "연관": ans_link},
    "F_미디어": {"문제": ml_claims, "대안": ml_response},
    "G_에세이": final_essay,
    "객관식": {k: st.session_state.answers_mc.get(k) for k in [i['id'] for i in MC_ITEMS]},
    "자동점수": {"영역": auto, "가중총점": weighted, "객관식가산": auto_bonus, "예상최종(%)": round(final_auto_score*100,1)}
}

preview_tabs = st.tabs(["JSON", "CSV(타임라인)", "요약"])
with preview_tabs[0]:
    st.code(json.dumps(bundle, ensure_ascii=False, indent=2))
with preview_tabs[1]:
    csv = st.session_state.timeline_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("타임라인 CSV 다운로드", csv, file_name="timeline.csv", mime="text/csv")
    st.dataframe(st.session_state.timeline_df, use_container_width=True)
with preview_tabs[2]:
    st.write(f"**제출자:** {meta['이름']} / {meta['학급']}")
    st.write(f"**예상 점수:** {round(final_auto_score*100,1)}점")
    st.write("**강점 후보:** 출처평가, 데이터·미디어 리터러시, 타임라인 정확도")
    st.write("**개선 제안:** 에세이 분량 준수, 근거의 다양성, 사료 간 의미 관계의 구조화")

# 다운로드(전체 JSON)
json_bytes = json.dumps(bundle, ensure_ascii=False, indent=2).encode('utf-8')
st.download_button("전체 제출물(JSON) 다운로드", data=json_bytes, file_name="khs2_performance_ilje.json", mime="application/json")

st.success("작성 완료 후 위의 다운로드 버튼으로 결과를 제출하세요. 교사는 JSON을 수합·기록 관리에 활용할 수 있습니다.")

# ---------------------- 푸터 ----------------------
st.markdown("---")
st.caption("본 앱은 학습 증거 기반 평가를 지향합니다 · ⓒ 한국사2 수행평가 템플릿")
