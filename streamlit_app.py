#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

#######################
# Page configuration
st.set_page_config(
    page_title="US Population Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("default")

#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)


#######################
# Load data
#######################
# Load data (robust)
def load_people_data():
    # 1) ensure openpyxl
    try:
        import openpyxl  # noqa: F401
    except ImportError:
        import sys, subprocess
        try:
            st.warning("필수 패키지 'openpyxl'이 없어 설치합니다…")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl", "--quiet"])
            st.success("'openpyxl' 설치 완료.")
        except Exception as e:
            st.error(f"'openpyxl' 설치 실패: {e}")
            st.stop()

    # 2) find file
    from pathlib import Path
    candidates = ["people_data.xlsx", "/mnt/data/people_data.xlsx"]
    excel_path = next((p for p in candidates if Path(p).exists()), None)
    if not excel_path:
        st.error("people_data.xlsx 파일을 찾을 수 없습니다. 앱 루트 또는 /mnt/data 에 배치해 주세요.")
        st.stop()

    # 3) read
    try:
        return pd.read_excel(excel_path, engine="openpyxl")
    except Exception as e:
        st.error(f"엑셀 로딩 중 오류: {e}")
        st.stop()

df_reshaped = load_people_data()

#df_reshaped = pd.read_excel('people_data.xlsx')


#######################
# Sidebar

with st.sidebar:
    st.title("👥 인구 특성 분석 대시보드")

    # 연령대 선택
    age_group = st.selectbox(
        "연령대 선택",
        options=["전체", "10대", "20대", "30대", "40대", "50대", "60대 이상"]
    )

    # 성별 선택
    gender = st.radio(
        "성별 선택",
        options=["전체", "Male", "Female"]
    )

    # 직업 유무 선택
    job_status = st.radio(
        "직업 상태",
        options=["전체", "Employed", "Unemployed"]
    )

    # 소득 범위 선택
    income_range = st.slider(
        "소득 범위 (달러)",
        min_value=0, max_value=500, value=(0, 500), step=10
    )

    # 색상 테마 선택
    color_theme = st.selectbox(
        "색상 테마",
        options=["Blues", "Viridis", "Plasma", "Cividis"]
    )




#######################
# Plots



#######################
# Dashboard Main Panel
col = st.columns((1.5, 4.5, 2), gap='medium')

# with col[0]:
with col[0]:
    st.markdown("### 📊 요약 지표")

    # 요약 지표 계산
    avg_income = df_reshaped["Income($)"].mean()
    max_income = df_reshaped["Income($)"].max()
    min_income = df_reshaped["Income($)"].min()
    avg_age = df_reshaped["Age"].mean()
    avg_height = df_reshaped["Height(cm)"].mean()
    employed_ratio = (df_reshaped["Job Status"].eq("Employed").mean()) * 100
    unemployed_ratio = 100 - employed_ratio

    # 카드 스타일 템플릿
    def metric_card(title, value, subtitle=""):
        st.markdown(
            f"""
            <div style="
                background-color: #FFFFFF;
                padding: 15px;
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                text-align: center;
                margin-bottom: 15px;
            ">
                <h4 style="margin-bottom:5px;">{title}</h4>
                <h2 style="margin:5px 0;">{value}</h2>
                <p style="color:gray; margin:0;">{subtitle}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 카드 표시
    metric_card("평균 소득 ($)", f"{avg_income:.1f}", f"최고 {max_income}, 최저 {min_income}")
    metric_card("평균 나이", f"{avg_age:.1f} 세")
    metric_card("평균 키", f"{avg_height:.1f} cm")
    metric_card("고용률", f"{employed_ratio:.1f} %")
    metric_card("실업률", f"{unemployed_ratio:.1f} %")


# with col[1]:
with col[1]:
    st.markdown("### 📈 인구 특성 시각화")

    # 1. 연령대 컬럼 생성
    bins = [0, 19, 29, 39, 49, 59, 69, 120]
    labels = ["10대 이하", "20대", "30대", "40대", "50대", "60대", "70대 이상"]
    df_reshaped["연령대"] = pd.cut(df_reshaped["Age"], bins=bins, labels=labels, right=True)

    # 2. 히트맵 (연령대 vs 고용상태, 값=평균 소득)
    heatmap_data = (
        df_reshaped.groupby(["연령대", "Job Status"])["Income($)"]
        .mean()
        .reset_index()
    )

    heatmap_chart = alt.Chart(heatmap_data).mark_rect().encode(
        x=alt.X("Job Status:N", title="직업 상태"),
        y=alt.Y("연령대:N", title="연령대"),
        color=alt.Color("Income($):Q", scale=alt.Scale(scheme=color_theme.lower()), title="평균 소득($)"),
        tooltip=["연령대", "Job Status", "Income($)"]
    ).properties(
        width=400,
        height=300,
        title="연령대 × 직업 상태별 평균 소득 히트맵"
    )

    st.altair_chart(heatmap_chart, use_container_width=True)

    # 3. 소득 분포 히스토그램 (성별 구분)
    hist_chart = px.histogram(
        df_reshaped,
        x="Income($)",
        color="Gender",
        nbins=30,
        title="소득 분포 (성별 구분)",
        color_discrete_sequence=px.colors.sequential.__dict__.get(color_theme, px.colors.sequential.Blues)
    )
    hist_chart.update_layout(bargap=0.1)

    st.plotly_chart(hist_chart, use_container_width=True)




# with col[2]:
with col[2]:
    st.markdown("### 🏆 소득 Top 10 인물")

    # 소득 상위 10명
    top_income = df_reshaped.nlargest(10, "Income($)")

    # Progress bar 스타일 테이블
    for i, row in top_income.iterrows():
        st.markdown(
            f"""
            <div style="
                background-color:#FFFFFF;
                padding:8px;
                margin-bottom:8px;
                border-radius:8px;
                box-shadow:0 2px 5px rgba(0,0,0,0.1);
            ">
                <strong>{row['Name']}</strong>  
                <div style="font-size:12px; color:gray;">
                    {row['Gender']} | 나이 {row['Age']}세 | {row['Job Status']}
                </div>
                <div style="margin-top:5px;">
                    <progress value="{row['Income($)']}" max="500" style="width:100%; height:12px;"></progress>
                </div>
                <div style="font-size:13px; text-align:right; color:#333;">
                    ${row['Income($)']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("### 📌 데이터 설명")
    st.markdown(
        """
        - **소득 Top 10**: 상위 10명의 인물을 소득 기준으로 표시했습니다.  
        - Progress bar는 최대 소득 범위(500$) 기준으로 상대적 위치를 보여줍니다.  
        - 하단 설명 영역에는 데이터 출처 및 추가 안내를 넣을 수 있습니다.  
        """
    )
