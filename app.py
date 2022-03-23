import streamlit as st
import pandas as pd
import numpy as np
#from PIL import Image
#from io import BytesIO
import scipy.sparse
import requests
from sklearn.metrics.pairwise import cosine_similarity
st.set_page_config(layout="wide")

@st.cache(allow_output_mutation=True)
def load_data():
    movies = pd.read_csv('movies_streamlit.csv')
    cv_matrix = scipy.sparse.load_npz('cv_matrix.npz')
    cs_matrix = cosine_similarity(cv_matrix, dense_output=False)
    #cs_matrix = scipy.sparse.load_npz('cs_matrix.npz')
    return movies, cs_matrix

movies, cs_matrix = load_data()

def recommendations(title, cosine_sim=cs_matrix):
    idx = movies.loc[movies.title == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx].toarray()[0]))
    #sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    movie_indices = [i[0] for i in sim_scores]
    st.session_state['indices'] = movie_indices
    #return movie_indices

def fetch_data(index, column):
    return movies.loc[index, column]

def update_session_state(name, value):
    for n, v in zip(name, value):
        st.session_state[n] = v

def get_cast(movie_id):
    api = 'ec619fb3830712e3767e7582898a8592'
    link = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api}&language=en-US"
    cast = requests.get(link).json()['cast']
    names = []
    characters = []
    profile_paths = []
    base_url = 'https://image.tmdb.org/t/p/w500'

    for val in cast:
        if hasattr(val, 'get'):
            names.append(val.get('name'))
            characters.append(val.get('character'))
            profile_paths.append(base_url + val.get('profile_path') if type(val.get('profile_path')) == str else 'http://tinleychamber.org/wp-content/uploads/2019/01/no-image-available.png')
    return names, characters, profile_paths

def movie_details(index):
    movie_title = fetch_data(index, 'title')
    overview = fetch_data(index, 'overview')
    poster = fetch_data(index, 'poster_path')
    year = fetch_data(index, 'year')
    vote_average = fetch_data(index, 'vote_average')
    director = fetch_data(index, 'director')
    genres = fetch_data(index, 'genres')
    if '|' in genres:
        genres = genres.replace('|', ', ')



    names, characters, profile_paths = get_cast(fetch_data(index, 'id'))
    
    st.image(poster, use_column_width='never', width=200)
    st.title(f"{movie_title} ({int(year)})")
    st.markdown(f'<b style="font-size:25px">Genres: {genres}</b>', unsafe_allow_html=True)
    st.markdown(f'<b style="font-size:22px">Directed by {director}</b>', unsafe_allow_html=True)
    st.header('Overview')
    st.markdown(f'<b style="font-size:20px">{overview}</b>', unsafe_allow_html=True)
    
    st.info(f'Voting Average: {vote_average}')
    num_col_rows = np.ceil(len(names) / 5).astype(int)
    with st.expander("Cast"):
        for i in range(num_col_rows):
            start = i * 5
            cols = st.columns((1,1,1,1,1))
            for j, col in zip(np.arange(start, start+5), cols):
                if j < len(names):
                    with col:
                        st.image(profile_paths[j], use_column_width='never', width=200)
                        #st.write(f'{names[j]} as {characters[j]}')
                        st.markdown(f'<b style="font-size:20px">{names[j]} as {characters[j]}</b>', unsafe_allow_html=True)
    st.button('Back to Recommendations', key='detail_', on_click=update_session_state, kwargs=dict(name=['movie_details'], value=[None]))
    st.button('Reset', on_click=update_session_state, kwargs=dict(name=['indices', 'movie_details'], value=[None, None]))

    
    


def display_columns(indices):
    titles = [fetch_data(i, 'title') for i in indices]
    posters = [fetch_data(i, 'poster_path') for i in indices]

    
    st.title('Here are your Top 10 recommendations:')
    st.button('Reset', on_click=update_session_state, kwargs=dict(name=['indices', 'movie_details'], value=[None, None]))
    columns_1 = st.columns((1,1,1,1,1))
    columns_2 = st.columns((1,1,1,1,1))
    for i, col in zip(np.arange(0,5), columns_1):
        with col:
            st.header(titles[i])
            st.image(posters[i], use_column_width=True)            
            st.button('Details', key='detail_' + str(i), on_click=update_session_state, kwargs=dict(name=['movie_details'], value=[indices[i]]))

    for i, col in zip(np.arange(5,10), columns_2):
        with col:
            st.header(titles[i])
            st.image(posters[i],use_column_width=True)
            st.button('Details', key='detail_' + str(i), on_click=update_session_state, kwargs=dict(name=['movie_details'], value=[indices[i]]))

import base64

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)





if 'indices' not in st.session_state:
    st.session_state['indices'] = None

if 'movie_details' not in st.session_state:
    st.session_state['movie_details'] = None




if st.session_state['indices'] == None:
    #st.image('image1.png', width=800)
    st.title('Movie Recommendation System')
    #title = '<p style="font-family: sans-serif; color:White; font-size: 90px; font-weight: bold;-webkit-text-stroke: 5px Red;">Movie Recommendation System</p>'
    #st.markdown(title, unsafe_allow_html=True)
    selected_movie = st.selectbox('Select a movie to get recommendations:', sorted(movies['title'].values))
    st.button('Recommend', on_click=recommendations, kwargs=dict(title=selected_movie))
    st.button('Reset', on_click=update_session_state, kwargs=dict(name=['indices', 'movie_details'], value=[None, None]))
    set_background('image2.png')
    

if st.session_state['indices'] != None and st.session_state['movie_details'] == None:
    display = display_columns(st.session_state['indices'])


elif st.session_state['indices'] != None and st.session_state['movie_details'] != None:
    movie_details(st.session_state['movie_details'])




