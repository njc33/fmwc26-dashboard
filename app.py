import streamlit as st

st.set_page_config(
    page_title="To honor the legacy of BMFB and his Nomenclator",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    "<h1 style='text-align:center; margin:8px 0 12px;'>BMFB Data Sports Analytics</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; font-size:1.1rem; color:#555;'>"
    "Your hub for real-time sports data, tournament tracking, and league analytics.</p>",
    unsafe_allow_html=True,
)
st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### ⚽ FIFA World Cup 2026")
    st.write("Track groups, fixtures, results, and standings for the 2026 FIFA Men's World Cup.")
    st.page_link("pages/1_FIFA_World_Cup.py", label="Open FIFA World Cup ->")
with col2:
    st.markdown("### ⚾ Men's College World Series")
    st.write("View the bracket for the 2026 tournament.")
    st.page_link("pages/2_Mens_College_World_Series.py", label="Open MCWS ->")
with col3:
    st.markdown("### 🏈 NAFFL")
    st.write("Coming Soon")
    st.page_link("pages/4_NAFFL.py", label="Open NAFFL ->")

st.divider()
col4, col5, col6 = st.columns(3)
with col4:
    st.markdown("### 🧢 Future GMs of America")
    st.write("Coming Soon")
    st.page_link("pages/3_Future_GMs_of_America.py", label="Open Future GMs ->")
with col5:
    st.markdown("### 🤝 About Us")
    st.write("PLACEHOLDER")
    st.page_link("pages/5_About_Us.py", label="About Us ->")
with col6:
    st.markdown("### 💛 Giving")
    st.write("loading...")
    st.page_link("pages/6_Giving.py", label="Giving ->")
