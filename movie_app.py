import streamlit as st
import pandas as pd 
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

#page configration
st.set_page_config(page_title="IMDB Movie Recommender", page_icon="🎬", layout="wide")
st.caption("🎯 A movie recommendation system built with Python, Streamlit, and data analysis techniques.")
# 🎨 CSS
st.markdown("""
<style>

/* Background */
[data-testid="stAppViewContainer"] {
    background-color: var(--background-color);
color: var(--text-color);
}

/* Title */
h1 {
    text-align: center;
    font-size: 50px !important;
}

/* Button */
div.stButton > button:first-child {
    font-size: 24px;
    padding: 18px 0px;
    border-radius: 12px;
    background-color: #3b82f6;
    color: white;
    border: none;
}

/* Movie card */
.movie-card {
    background-color: #1c2233;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 25px;
}
/* Rating */
.rating {
    color: gold;
    font-weight: bold;
    font-size: 18px;
}


</style>
""", unsafe_allow_html=True)

# 🎬 Title
st.markdown("<h1>🎬 IMDB Movie Recommender</h1>", unsafe_allow_html=True)
st.markdown("---")
# 📊 Load data
@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv('imdb orginal.csv')
    df = df.dropna(subset=['Year', 'Genre', 'Rating'])
    df['Year'] = df['Year'].astype(int)
    df['Duration (min)'] = pd.to_numeric(df['Duration (min)'], errors='coerce').astype('Int64')

    df['Genre'] = df['Genre'].astype(str).str.split(',')

    # ✅ CLEAN HERE
    def clean_genres(genres):
        cleaned = []
        for g in genres:
            g = g.strip().lower()

            if g in ["music", "musical"]:
                g = "musical"

            cleaned.append(g.capitalize())

        return cleaned

    df['Genre'] = df['Genre'].apply(clean_genres)

    df_exploded = df.explode('Genre')

    return df, df_exploded
df, df_exploded = load_data()
# 🎛 Filters
if "end_year" not in st.session_state:
    st.session_state.end_year = None
col1, col2, col3 = st.columns([2,1,1])

with col1:
    genre = st.selectbox(
        'Choose Your Favorite Genre',
        sorted(df_exploded['Genre'].unique())
    )

min_year = int(df['Year'].min())
max_year = int(df['Year'].max())

with col2:
    start_year = st.number_input('Start Year', 
                                 min_value=min_year,
                                 max_value=max_year,
                                 value=min_year)

with col3:
    end_year = st.number_input('End Year',
                               min_value=min_year,
                               max_value=max_year,
                               value=st.session_state.end_year if st.session_state.end_year else start_year,
                               step=1,
                               
    )
                        

# 🎬 CENTERED BUTTON recommender
st.markdown("---")

colA, colB, colC = st.columns([1,4,1])

with colB:
    recommend = st.button(
        " Recommend Movies",
        use_container_width=True
    )

# ☁ Wordcloud
def create_wordcloud(text):
    if pd.isna(text) or text == '':
        return None
    
    wordcloud = WordCloud(
        width=250,
        height=120,
        background_color=None,
        stopwords=STOPWORDS,
        colormap='plasma'
    ).generate(str(text))
    
    fig, ax = plt.subplots(figsize=(2.5, 1.2))
    fig.patch.set_alpha(0)
    ax.imshow(wordcloud)
    ax.axis("off")
    plt.tight_layout(pad=0)
    
    return fig

# 🎯 Recommendation function
def recommend_movies(genre, start_year, end_year, top_n=3):
    df_filtered = df_exploded[
        (df_exploded['Genre'] == genre) &
        (df_exploded['Year'] >= start_year) &
        (df_exploded['Year'] <= end_year)
    ]

    df_filtered = df_filtered.drop_duplicates(subset=['Title'])
    df_filtered = df_filtered.sort_values(by='Rating', ascending=False).head(top_n)

    return df_filtered[['Title', 'Year', 'Rating','Director','Duration (min)','Cast' ,'Description', 'Poster', 'Review']]

# 🎥 SHOW RESULTS
if recommend:
        movies = recommend_movies(genre, start_year, end_year)

        if movies.empty:
            st.warning(f"No movies found for {genre} between {start_year} and {end_year}")
        else:
            for i, row in movies.iterrows():

                st.markdown("<div class='movie-card'>", unsafe_allow_html=True)

                col1, col2 = st.columns([1,2])

                # 🎬 Poster
                with col1:
                    if pd.notna(row['Poster']):
                        st.image(row['Poster'], width=260)
                    else:
                        st.info("No poster available")

                # 📄 Info
                with col2:
                    st.markdown(f"## {row['Title']}")
                    st.markdown(
                        f"<span class='rating'>⭐ {row['Rating']}</span> | 📅 {row['Year']}",
                        unsafe_allow_html=True
                    )
                    st.markdown(f"⏱ **Duration:** {row['Duration (min)']} min")
                    st.markdown(f"🎬 **Director:** {row['Director']}")
                    st.markdown(f"🎭 **Cast:** {row['Cast']}")

                    if pd.notna(row['Description']):
                        with st.expander("📝 Description"):
                            st.write(row['Description'])

                    if pd.notna(row['Review']):
                        with st.expander("☁ Critics Word Cloud"):
                            fig = create_wordcloud(row['Review'])
                            if fig:
                                st.pyplot(fig)
                                plt.close(fig)
                                

        st.markdown("</div>", unsafe_allow_html=True)
#movie analysis
st.sidebar.header("📊 Dataset Insights")

# Top Genres
top_genres = df_exploded['Genre'].value_counts().head(10)
st.sidebar.subheader("Top Genres")
st.sidebar.bar_chart(top_genres)

# Ratings over time
avg_rating_by_year = df.groupby('Year')['Rating'].mean()
st.sidebar.subheader("Ratings Over Time")
st.sidebar.line_chart(avg_rating_by_year)

# Metrics
st.sidebar.subheader("Summary")
st.sidebar.metric("Total Movies", len(df))
st.sidebar.metric("Avg Rating", f"{df['Rating'].mean():.2f}")
st.sidebar.metric("Genres", df_exploded['Genre'].nunique())  
