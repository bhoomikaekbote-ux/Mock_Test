import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from bs4 import BeautifulSoup

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="Stack Overflow Analytics",
    page_icon="📊",
    layout="wide"
)

# -------------------------------
# LOAD DATA
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(
        "QueryResults_web testing stackoverflow questions.csv"
    )

    df["CreationDate"] = pd.to_datetime(
        df["CreationDate"],
        errors="coerce"
    )

    df["Year"] = df["CreationDate"].dt.year

    return df

df = load_data()

# -------------------------------
# SIDEBAR
# -------------------------------
st.sidebar.title("Dashboard Filters")

years = sorted(df["Year"].dropna().unique())

selected_years = st.sidebar.multiselect(
    "Select Year",
    years,
    default=years
)

filtered_df = df[df["Year"].isin(selected_years)]

# -------------------------------
# HEADER
# -------------------------------
st.title("📊 Stack Overflow Web Testing Analytics Dashboard")

st.markdown("""
Analyze Web Testing related Stack Overflow questions,
views, scores, answers and tag popularity.
""")

# -------------------------------
# KPI SECTION
# -------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Questions",
        f"{len(filtered_df):,}"
    )

with col2:
    st.metric(
        "Avg Score",
        round(filtered_df["Score"].mean(), 2)
    )

with col3:
    st.metric(
        "Avg Views",
        round(filtered_df["ViewCount"].mean())
    )

with col4:
    st.metric(
        "Avg Answers",
        round(filtered_df["AnswerCount"].mean(), 2)
    )

st.divider()

# -------------------------------
# DATASET PREVIEW
# -------------------------------
st.subheader("Dataset Preview")

st.dataframe(
    filtered_df.head(20),
    use_container_width=True
)

# -------------------------------
# QUESTIONS OVER TIME
# -------------------------------
st.subheader("Questions Posted Over Time")

year_counts = (
    filtered_df.groupby("Year")
    .size()
    .reset_index(name="Questions")
)

fig = px.bar(
    year_counts,
    x="Year",
    y="Questions",
    title="Questions per Year"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# SCORE DISTRIBUTION
# -------------------------------
st.subheader("Score Distribution")

fig = px.histogram(
    filtered_df,
    x="Score",
    nbins=30,
    title="Question Score Distribution"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# VIEW COUNT DISTRIBUTION
# -------------------------------
st.subheader("View Count Distribution")

fig = px.histogram(
    filtered_df,
    x="ViewCount",
    nbins=40,
    title="Views Distribution"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# TOP VIEWED QUESTIONS
# -------------------------------
st.subheader("Top Viewed Questions")

top_viewed = (
    filtered_df[
        ["Title", "ViewCount"]
    ]
    .sort_values(
        by="ViewCount",
        ascending=False
    )
    .head(10)
)

fig = px.bar(
    top_viewed,
    x="ViewCount",
    y="Title",
    orientation="h",
    title="Top Viewed Questions"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# TOP ANSWERED QUESTIONS
# -------------------------------
st.subheader("Most Answered Questions")

top_answered = (
    filtered_df[
        ["Title", "AnswerCount"]
    ]
    .sort_values(
        by="AnswerCount",
        ascending=False
    )
    .head(10)
)

fig = px.bar(
    top_answered,
    x="AnswerCount",
    y="Title",
    orientation="h",
    title="Top Answered Questions"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# CORRELATION
# -------------------------------
st.subheader("Correlation Analysis")

corr_df = filtered_df[
    ["Score", "ViewCount", "AnswerCount", "CommentCount"]
]

fig = px.imshow(
    corr_df.corr(numeric_only=True),
    text_auto=True,
    title="Correlation Matrix"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# TAG ANALYSIS
# -------------------------------
st.subheader("Popular Tags")

all_tags = []

for tag in filtered_df["Tags"].dropna():

    tag = tag.replace("<", "")
    tag = tag.split(">")

    all_tags.extend(
        [t for t in tag if t]
    )

tag_df = pd.Series(all_tags).value_counts().head(15)

fig = px.bar(
    x=tag_df.index,
    y=tag_df.values,
    labels={
        "x": "Tag",
        "y": "Frequency"
    },
    title="Top Tags"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# WORD CLOUD
# -------------------------------
st.subheader("Question Title Word Cloud")

text = " ".join(
    filtered_df["Title"].dropna()
)

wordcloud = WordCloud(
    width=1200,
    height=500,
    background_color="white"
).generate(text)

fig, ax = plt.subplots(figsize=(12, 5))

ax.imshow(wordcloud)

ax.axis("off")

st.pyplot(fig)

# -------------------------------
# INSIGHTS SECTION
# -------------------------------
st.subheader("AI-style Insights")

highest_views = filtered_df["ViewCount"].max()

highest_score = filtered_df["Score"].max()

most_answers = filtered_df["AnswerCount"].max()

st.success(f"""
• Highest View Count: {highest_views:,}

• Highest Question Score: {highest_score}

• Maximum Answers Received: {most_answers}

• Selenium and WebDriver dominate discussions.

• Questions with higher views generally receive more answers.

• Most activity comes from automation testing topics.

• Popular tags indicate strong industry focus on Selenium,
Python, Java and Web Automation.
""")

# -------------------------------
# DOWNLOAD DATA
# -------------------------------
st.subheader("Download Data")

csv = filtered_df.to_csv(index=False)

st.download_button(
    "Download Filtered Dataset",
    csv,
    file_name="filtered_stackoverflow_data.csv",
    mime="text/csv"
)

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.markdown(
    "Created with Streamlit ❤️"
)
