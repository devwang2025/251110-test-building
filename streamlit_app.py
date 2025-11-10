import streamlit as st
import numpy as np
import pandas as pd
import altair as alt


st.set_page_config(page_title="주사위 굴리기 앱", layout="wide")

st.title("� 주사위 굴리기 앱")

st.write("주사위 개수와 면 수를 선택한 뒤 '굴리기' 버튼을 눌러 결과를 확인하세요.")


with st.sidebar:
    st.header("설정")
    n = st.slider("주사위 개수 (개)", min_value=1, max_value=5000, value=100, step=1)
    faces = st.selectbox("주사위 면 수", options=[4, 6, 8, 10, 12, 20], index=1)
    seed = st.number_input("랜덤 시드 (선택, 비워두면 무작위)", value=0, format="%d")
    if seed == 0:
        use_seed = False
    else:
        use_seed = True
    roll_btn = st.button("굴리기")

# 세션 상태에 마지막 결과 저장
if "last_roll" not in st.session_state:
    st.session_state.last_roll = np.array([], dtype=int)

if roll_btn:
    if use_seed:
        rng = np.random.default_rng(seed)
        rolls = rng.integers(1, faces + 1, size=n)
    else:
        rolls = np.random.randint(1, faces + 1, size=n)
    st.session_state.last_roll = rolls

if st.session_state.last_roll.size == 0:
    st.info("굴리기 버튼을 눌러 주사위를 굴려보세요.")
else:
    rolls = st.session_state.last_roll

    # 통계량
    mean = float(rolls.mean())
    std = float(rolls.std(ddof=0))
    median = float(np.median(rolls))
    minimum = int(rolls.min())
    maximum = int(rolls.max())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("평균 (mean)", f"{mean:.3f}")
    c2.metric("표준편차 (std)", f"{std:.3f}")
    c3.metric("중앙값 (median)", f"{median:.0f}")
    c4.metric("최솟값 / 최댓값", f"{minimum} / {maximum}")

    # 면별 빈도
    counts = pd.Series(rolls).value_counts().sort_index().reindex(range(1, faces + 1), fill_value=0)
    df = pd.DataFrame({
        "face": counts.index.astype(int),
        "count": counts.values,
    })
    df["proportion"] = df["count"] / df["count"].sum()

    st.subheader("면별 분포 (빈도)")
    bar = alt.Chart(df).mark_bar().encode(
        x=alt.X("face:O", title="면"),
        y=alt.Y("count:Q", title="빈도"),
        tooltip=[alt.Tooltip("face:O", title="면"), alt.Tooltip("count:Q", title="빈도"), alt.Tooltip("proportion:Q", title="비율", format=".3f")]
    ).properties(height=320)
    st.altair_chart(bar, use_container_width=True)

    st.subheader("샘플 히스토그램 (주사위 값)")
    hist_df = pd.DataFrame({"value": rolls})
    hist = alt.Chart(hist_df).mark_bar().encode(
        x=alt.X("value:Q", bin=alt.Bin(step=1, extent=[0.5, faces + 0.5]), title="값"),
        y=alt.Y("count():Q", title="빈도"),
        tooltip=[alt.Tooltip("count():Q", title="빈도")]
    ).properties(height=240)
    st.altair_chart(hist, use_container_width=True)

    st.subheader("세부 정보")
    left, right = st.columns([2, 1])

    with left:
        if n <= 200:
            st.write("굴린 값 (전체)")
            st.write(rolls.tolist())
        else:
            st.write(f"굴린 값이 {n}개이므로 처음 200개만 표시합니다:")
            st.write(rolls[:200].tolist())

    with right:
        st.write("면별 빈도표")
        st.dataframe(df.assign(proportion=lambda d: d.proportion.round(3)).set_index("face"))

    st.markdown("---")
    st.caption("참고: 최대 5000개의 주사위를 동시에 굴릴 수 있습니다. 큰 수일수록 이론적 분포(균등)에 근접합니다.")

