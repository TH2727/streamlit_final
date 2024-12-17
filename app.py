import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rc
from io import BytesIO


# 한국어 폰트 설정
rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False 


# Streamlit 페이지 설정
st.set_page_config(page_title="데이터 분석 도구", layout="wide")

# 공통 스타일 설정
st.markdown(
    """
    <style>
    .css-18e3th9 {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .sidebar-button {
        display: block;
        width: 100%;
        padding: 10px;
        margin-bottom: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 14px;
        color: white;
        border-radius: 8px;
        box-shadow: inset 1px 1px 2px rgba(0, 0, 0, 0.2);
        text-decoration: none;
        transition: background-color 0.3s, transform 0.2s;
    }
    .upload-button {
        background-color: #f9c2c2;
    }
    .upload-button:hover {
        background-color: #f4a1a1;
        transform: scale(1.05);
    }
    .preprocessing-button {
        background-color: #d4f9c2;
    }
    .preprocessing-button:hover {
        background-color: #bdf4a1;
        transform: scale(1.05);
    }
    .visualization-button {
        background-color: #c2d4f9;
    }
    .visualization-button:hover {
        background-color: #a1bdf4;
        transform: scale(1.05);
    }
    .stats-button {
        background-color: #f9e6c2;
    }
    .stats-button:hover {
        background-color: #f4d6a1;
        transform: scale(1.05);
    }
    a.sidebar-button:visited, a.sidebar-button:hover, a.sidebar-button:link {
        color: black;
        text-decoration: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 세션 상태 초기화
if "uploaded_data" not in st.session_state:
    st.session_state["uploaded_data"] = None
if "preprocessed_data" not in st.session_state:
    st.session_state["preprocessed_data"] = None
if "page" not in st.session_state:
    st.session_state["page"] = "upload"

# 사이드바 메뉴
def change_page(page):
    st.session_state["page"] = page

st.sidebar.title("📂 메뉴")
st.sidebar.button("데이터 업로드", on_click=change_page, args=("upload",))
st.sidebar.button("전처리", on_click=change_page, args=("preprocessing",))
st.sidebar.button("시각화", on_click=change_page, args=("visualization",))
st.sidebar.button("분석 결과", on_click=change_page, args=("stats",))

# 데이터 업로드 페이지
def upload_page():
    st.header("📂 데이터 업로드")
    uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

    if uploaded_file:
        data = pd.read_csv(uploaded_file)
        st.session_state["uploaded_data"] = data
        st.dataframe(data.head())
        st.success("데이터 업로드가 완료되었습니다.")

    if st.button("다음: 전처리"):
        st.session_state["page"] = "preprocessing"


# 전처리 페이지
def preprocessing_page():
    st.header("🛠 데이터 전처리")
    if st.session_state["uploaded_data"] is None:
        st.error("데이터가 업로드되지 않았습니다. 메인 페이지로 이동하세요.")
        if st.button("메인 페이지로 이동"):
            st.session_state["page"] = "upload"
        return

    data = st.session_state["uploaded_data"]

    # 속성 선택
    st.subheader("속성을 선택하세요")
    selection_option = st.radio("전체 선택 / 해제", ["전체 선택", "전체 해제", "사용자 선택"], horizontal=True)
    if selection_option == "전체 선택":
        selected_columns = list(data.columns)
    elif selection_option == "전체 해제":
        selected_columns = []
    else:
        selected_columns = st.multiselect("분석에 사용할 속성을 선택하세요", options=data.columns, default=data.columns)
    data = data[selected_columns]

    # 결측치 제거
    if st.checkbox("결측치 행 제거"):
        data = data.dropna()

    # 원핫 인코딩
    if st.checkbox("선택된 속성의 범주형 데이터 원핫 인코딩"):
        categorical_columns = data.select_dtypes(include=["object", "category"]).columns
        selected_categorical_columns = [col for col in selected_columns if col in categorical_columns]
        data = pd.get_dummies(data, columns=selected_categorical_columns)

    st.session_state["preprocessed_data"] = data
    st.dataframe(data.head())

    # CSV 파일 다운로드 버튼
    csv_buffer = BytesIO()
    data.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    st.download_button(
        label="전처리 결과 다운로드",
        data=csv_buffer,
        file_name="preprocessed_data.csv",
        mime="text/csv",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("이전: 데이터 업로드"):
            st.session_state["page"] = "upload"
    with col2:
        if st.button("다음: 시각화"):
            st.session_state["page"] = "visualization"
    with col3:
        if st.button("다음: 분석 결과"):
            st.session_state["page"] = "stats"


# 시각화 페이지
def visualization_page():
    st.header("📊 데이터 시각화")
    if st.session_state["preprocessed_data"] is None:
        st.error("전처리된 데이터가 없습니다. 먼저 데이터를 전처리해주세요!")
        return

    data = st.session_state["preprocessed_data"]

    st.subheader("그래프 종류 선택")
    graph_type = st.selectbox(
        "시각화할 그래프의 종류를 선택하세요",
        ["막대그래프", "히스토그램", "산점도", "상관관계 히트맵", "꺾은선 그래프"],
    )

    img_buffer = BytesIO()  # 그래프 이미지를 저장할 버퍼

    if graph_type in ["막대그래프", "히스토그램", "꺾은선 그래프"]:
        x_column = st.selectbox("X축으로 사용할 속성을 선택하세요", options=data.columns)
        if st.button("그래프 생성"):
            plt.figure(figsize=(10, 6))
            if graph_type == "막대그래프":
                data[x_column].value_counts().plot(kind="bar")
            elif graph_type == "히스토그램":
                data[x_column].plot(kind="hist", bins=30)
            elif graph_type == "꺾은선 그래프":
                data[x_column].plot(kind="line")
            plt.title(f"{graph_type} ({x_column})")
            plt.savefig(img_buffer, format="png")
            st.pyplot(plt)

    elif graph_type == "산점도":
        col1, col2 = st.columns(2)
        with col1:
            x_column = st.selectbox("X축 속성", options=data.columns)
        with col2:
            y_column = st.selectbox("Y축 속성", options=data.columns)
        if st.button("그래프 생성"):
            plt.figure(figsize=(10, 6))
            plt.scatter(data[x_column], data[y_column])
            plt.title(f"{x_column} vs {y_column} 산점도")
            plt.xlabel(x_column)
            plt.ylabel(y_column)
            plt.savefig(img_buffer, format="png")
            st.pyplot(plt)

    elif graph_type == "상관관계 히트맵":
        if st.button("그래프 생성"):
            plt.figure(figsize=(10, 8))
            sns.heatmap(data.corr(), annot=True, cmap="coolwarm")
            plt.title("상관관계 히트맵")
            plt.savefig(img_buffer, format="png")
            st.pyplot(plt)

    # 다운로드 버튼
    if img_buffer.getvalue():
        st.download_button(
            label="이미지 다운로드",
            data=img_buffer.getvalue(),
            file_name="visualization.png",
            mime="image/png",
        )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전: 전처리"):
            st.session_state["page"] = "preprocessing"


# 분석 결과 페이지
def stats_page():
    st.header("📈 분석 결과 제공")
    if st.session_state["preprocessed_data"] is None:
        st.error("전처리된 데이터가 없습니다. 먼저 데이터를 전처리해주세요!")
        return

    data = st.session_state["preprocessed_data"]

    st.subheader("속성을 선택하세요")
    selection_option = st.radio("전체 선택 / 해제", ["전체 선택", "전체 해제", "사용자 선택"], horizontal=True)
    if selection_option == "전체 선택":
        selected_columns = list(data.columns)
    elif selection_option == "전체 해제":
        selected_columns = []
    else:
        selected_columns = st.multiselect("분석할 속성을 선택하세요", options=data.columns, default=data.columns)
    selected_data = data[selected_columns]

    if not selected_columns:
        st.warning("분석할 속성을 선택해주세요!")
        return

    st.subheader("통계량 계산 결과")
    stats = selected_data.describe().transpose()
    stats["분산"] = selected_data.var()
    stats["중앙값"] = selected_data.median()
    st.dataframe(stats)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("이전: 시각화"):
            st.session_state["page"] = "visualization"


# 페이지 로딩
if st.session_state["page"] == "upload":
    upload_page()
elif st.session_state["page"] == "preprocessing":
    preprocessing_page()
elif st.session_state["page"] == "visualization":
    visualization_page()
elif st.session_state["page"] == "stats":
    stats_page()