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
    color: white; /* 글씨를 흰색으로 */
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
  color: white; /* 라벨도 흰색 */
}

[data-testid="stMetricValue"] {
  color: white; /* 값도 흰색 */
}

[data-testid="stMetricDelta"] {
  color: white !important; /* 증감 수치 흰색 */
}

[data-testid="stMetricDeltaIcon-Up"],
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
df_reshaped = pd.read_csv('titanic.csv') ## 분석 데이터 넣기


#######################
# Sidebar
with st.sidebar:
    st.title("🚢 Titanic Survival Dashboard")

    # Pclass filter
    pclass = st.multiselect(
        "Select Passenger Class",
        options=sorted(df_reshaped["Pclass"].unique()),
        default=sorted(df_reshaped["Pclass"].unique())
    )

    # Sex filter
    sex = st.multiselect(
        "Select Gender",
        options=df_reshaped["Sex"].unique(),
        default=df_reshaped["Sex"].unique()
    )

    # Embarked filter
    embarked = st.multiselect(
        "Select Embarked Port",
        options=df_reshaped["Embarked"].dropna().unique(),
        default=df_reshaped["Embarked"].dropna().unique()
    )

    # Age range slider
    age_min = int(df_reshaped["Age"].min())
    age_max = int(df_reshaped["Age"].max())
    age_range = st.slider(
        "Select Age Range",
        min_value=age_min,
        max_value=age_max,
        value=(age_min, age_max)
    )

    # Fare range slider
    fare_min = int(df_reshaped["Fare"].min())
    fare_max = int(df_reshaped["Fare"].max())
    fare_range = st.slider(
        "Select Fare Range",
        min_value=fare_min,
        max_value=fare_max,
        value=(fare_min, fare_max)
    )

    # 필터링된 데이터프레임 (이후 본문에서 활용)
    df_filtered = df_reshaped[
        (df_reshaped["Pclass"].isin(pclass)) &
        (df_reshaped["Sex"].isin(sex)) &
        (df_reshaped["Embarked"].isin(embarked)) &
        (df_reshaped["Age"].between(age_range[0], age_range[1], inclusive="both")) &
        (df_reshaped["Fare"].between(fare_range[0], fare_range[1], inclusive="both"))
    ]


#######################
# Dashboard Main Panel
col = st.columns((1.5, 4.5, 2), gap='medium')

# with col[0]:
with col[0]:
    st.markdown("### 📊 Survival Summary")

    # KPI 지표
    total_passengers = len(df_filtered)
    survived = df_filtered["Survived"].sum()
    died = total_passengers - survived
    survival_rate = (survived / total_passengers * 100) if total_passengers > 0 else 0

    st.metric("Total Passengers", total_passengers)
    st.metric("Survived", survived, delta=f"{survival_rate:.1f}%")
    st.metric("Died", died)

    st.markdown("---")

    # 성별별 생존율
    st.markdown("#### Survival Rate by Gender")
    gender_survival = (
        df_filtered.groupby("Sex")["Survived"].mean().reset_index()
    )
    gender_survival["Survived"] = gender_survival["Survived"] * 100

    fig_gender = px.pie(
        gender_survival,
        names="Sex",
        values="Survived",
        color="Sex",
        hole=0.4,
        color_discrete_map={"male": "blue", "female": "pink"}
    )
    st.plotly_chart(fig_gender, use_container_width=True)

    st.markdown("#### Survival Rate by Class")
    class_survival = (
        df_filtered.groupby("Pclass")["Survived"].mean().reset_index()
    )
    class_survival["Survived"] = class_survival["Survived"] * 100

    fig_class = px.pie(
        class_survival,
        names="Pclass",
        values="Survived",
        hole=0.4,
        color="Pclass"
    )
    st.plotly_chart(fig_class, use_container_width=True)

# with col[1]:
with col[1]:
    st.markdown("### 📈 Survival Analysis")

    # 1. 연령 분포 (생존자 vs 사망자)
    st.markdown("#### Age Distribution by Survival")
    fig_age = px.histogram(
        df_filtered,
        x="Age",
        color="Survived",
        nbins=30,
        barmode="overlay",
        color_discrete_map={0: "red", 1: "green"},
        labels={"Survived": "Survival"}
    )
    fig_age.update_traces(opacity=0.6)
    st.plotly_chart(fig_age, use_container_width=True)

    st.markdown("---")

    # 2. 운임대별 생존율 (Fare vs Survival)
    st.markdown("#### Fare vs Survival")
    fig_fare = px.box(
        df_filtered,
        x="Survived",
        y="Fare",
        color="Survived",
        color_discrete_map={0: "red", 1: "green"},
        labels={"Survived": "Survival", "Fare": "Fare"}
    )
    st.plotly_chart(fig_fare, use_container_width=True)

    st.markdown("---")

    # 3. 승선 항구별 생존율
    st.markdown("#### Survival Rate by Embarked Port")
    embarked_survival = (
        df_filtered.groupby("Embarked")["Survived"].mean().reset_index()
    )
    embarked_survival["Survived"] = embarked_survival["Survived"] * 100

    fig_embarked = px.bar(
        embarked_survival,
        x="Embarked",
        y="Survived",
        color="Embarked",
        text=embarked_survival["Survived"].round(1).astype(str) + "%",
        labels={"Survived": "Survival Rate (%)"}
    )
    st.plotly_chart(fig_embarked, use_container_width=True)


# with col[2]:
with col[2]:
    st.markdown("### 🏅 Top Groups & Details")

    # 1. Top 생존율 집단 (성별/등급/연령대)
    st.markdown("#### Top Survival Groups")
    group_stats = (
        df_filtered.groupby(["Sex", "Pclass"])["Survived"].mean().reset_index()
    )
    group_stats["Survived"] = group_stats["Survived"] * 100
    group_stats = group_stats.sort_values("Survived", ascending=False)

    fig_top_groups = px.bar(
        group_stats,
        x="Survived",
        y="Sex",
        color="Pclass",
        orientation="h",
        text=group_stats["Survived"].round(1).astype(str) + "%",
        labels={"Survived": "Survival Rate (%)", "Sex": "Gender", "Pclass": "Class"},
    )
    st.plotly_chart(fig_top_groups, use_container_width=True)

    st.markdown("---")

    # 2. 데이터 테이블 (필터링 반영)
    st.markdown("#### Filtered Passenger Data")
    st.dataframe(
        df_filtered[["PassengerId", "Name", "Sex", "Age", "Pclass", "Fare", "Embarked", "Survived"]],
        use_container_width=True,
        height=300
    )

    st.markdown("---")

    # 3. 데이터 출처 및 설명
    st.markdown("#### ℹ️ About Dataset")
    st.info(
        """
        Titanic dataset (Kaggle / seaborn 내장 데이터 변형판).
        - 총 승객 수: 891명
        - 주요 변수: 성별, 연령, 객실 등급, 운임, 탑승 항구
        - 목표 분석: 생존 패턴과 요인 파악
        """
    )
