import streamlit as st
from streamlit_folium import folium_static
import folium
import pandas as pd
import time
from predict import make_prediction


st.set_page_config(
            page_title="Titanic prediction model", # => Quick reference - Streamlit
            page_icon="🛳️",
            layout="centered", # wide
            initial_sidebar_state="auto") # collapsed

st.markdown('# 🛳️ Titanic prediction model')
st.markdown("## Would you have survived the titanic disaster? Let's find out!")


st.markdown('We\'ll start with the basic information')
columns = st.columns(4)

title_list = ['Mr', 'Mrs', 'Miss', 'Master', 'Don', 'Rev', 'Dr', 'Mme',
       'Ms', 'Major', 'Lady', 'Sir', 'Mlle', 'Col', 'Capt',
       'the Countess', 'Jonkheer']
title = columns[0].selectbox("What's your title?", title_list)

first_name = columns[1].text_input("First name", value="Jane")

sex = columns[2].radio("Male/female", ("male", "female"))

age = columns[3].number_input("Age", min_value=0, max_value=100, value=30)

st.markdown('Next, you will need to get your ticket')

def get_ports():
    ports_df = pd.read_csv("ports.csv")
    return ports_df

ports_df = get_ports()

m = folium.Map(location=[50, 1], zoom_start=5)

port = st.selectbox("Select your port of departure", list(ports_df['name']))
selected_port = ports_df[ports_df["name"] == port]
embarked = selected_port["embarked"].values[0]

folium.Marker(
        location=[selected_port["latitude"], selected_port["longitude"]],
        popup=selected_port["name"].values[0],
        icon=folium.Icon(color=selected_port["color"].values[0], icon="ship", prefix='fa'),
    ).add_to(m)

folium_static(m)

pclass_name = st.radio("How fancy are you?", ("1st class", "2nd class", "3rd class"))

if pclass_name == "1st class":
    fare = st.slider('How much are you willing to pay for the ticket?', 0, 550, 85)
    pclass = 1
if pclass_name == '2nd class':
    fare = st.slider('How much are you willing to pay for the ticket?', 0, 75, 20)
    pclass = 2
if pclass_name == '3rd class':
    fare = st.slider('How much are you willing to pay for the ticket?', 0, 70, 13)  
    pclass = 3

st.markdown('Great, now who are you traveling with?')

travel_option = st.radio("I'm traveling...", ("...on my own", "...with family"))
family_options = st.columns(4)
if travel_option == '...with family':
    sib = family_options[0].number_input("Siblings", min_value=0, max_value=7, value=0)  
    spouse = family_options[1].number_input("Spouse", min_value=0, max_value=1, value=0)
    parents = family_options[2].number_input("Parents", min_value=0, max_value=2, value=0)
    children = family_options[3].number_input("Children", min_value=0, max_value=7, value=0)
    sibsp = sib + spouse
    parch = parents + children
    family = sibsp + parch
    
else:
    sibsp = 0
    parch = 0
    family = sibsp + parch
    
st.markdown("## And that's all we need to know!")

family = sibsp + parch
X_pred = pd.DataFrame({
        "Pclass": pd.Series(pclass, dtype='float64'),
        "Sex": pd.Series(sex, dtype='object'),
        "Age": pd.Series(age, dtype='float64'),
        "SibSp": pd.Series(sibsp, dtype='float64'),
        "Parch": pd.Series(parch, dtype="float64"),
        "Fare": pd.Series(fare, dtype="float64"),
        "Embarked": pd.Series(embarked, dtype='object'),
        "Title": pd.Series(title, dtype='object'),
        "Family": pd.Series(family, dtype="float64")
        })

result, survival_probability = make_prediction(X_pred)
if result == 1:
    prediction = 'Survived'
else:
    prediction = 'Not survived'
    

if st.button("Give me the result!"):
    # print is visible in the server output, not in the page
    latest_iteration = st.empty()
    bar = st.progress(0)
    for i in range(100):
        # Update the progress bar with each iteration.
        # latest_iteration.text(f'Progress: {i+1}%')
        if i == 0:
            latest_iteration.text("Starting engines..")
        if i == 25:
            latest_iteration.text("Reviewing input..")
        if i == 50:
            latest_iteration.text("Predicting survival..")
        if i == 75:
            latest_iteration.text("Preparing result..")
        bar.progress(i + 1)
        time.sleep(0.05)
        
    if result == 1:
        st.success('You would most likely have survived!')
        st.metric("Survival probability", f'{round(survival_probability*100,2)}%')
    else:
        st.error('Unfortunately, you would probably not have survived')
        st.metric("Survival probability", f'{round(survival_probability*100,2)}%')

