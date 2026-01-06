import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.express as px

# Load saved model, scaler, and label encoder
with open("stream_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("stream_scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

with open("stream_label_encoder.pkl", "rb") as f:
    le = pickle.load(f)

# Title
st.title("🎓 Stream Recommendation System")
st.write("Enter your subject & aptitude scores to get personalized stream suggestions.")

# Input form
with st.form("student_form"):
    st.subheader("📘 Enter Your Scores (0 - 100)")
    math = st.slider("Mathematics", 0, 100, 70)
    science = st.slider("Science (Physics + Chemistry)", 0, 100, 70)
    biology = st.slider("Biology", 0, 100, 70)
    english = st.slider("English", 0, 100, 70)
    social = st.slider("Social Studies", 0, 100, 70)
    language = st.slider("Language (Hindi/Other)", 0, 100, 70)

    st.subheader("🧠 Aptitude & Skills")
    logical = st.slider("Logical Reasoning", 0, 100, 70)
    analytical = st.slider("Analytical Skills", 0, 100, 70)
    numerical = st.slider("Numerical Ability", 0, 100, 70)
    creativity = st.slider("Creativity", 0, 100, 70)
    communication = st.slider("Communication Skills", 0, 100, 70)
    artistic = st.slider("Artistic Skills", 0, 100, 70)
    practical = st.slider("Practical Skills", 0, 100, 70)

    submitted = st.form_submit_button("🔍 Recommend Stream")

if submitted:
    # Prepare input
    student_data = {
        "Math": math, "Science": science, "Biology": biology, "English": english,
        "SocialStudies": social, "Language": language,
        "LogicalReasoning": logical, "AnalyticalSkills": analytical, "NumericalAbility": numerical,
        "Creativity": creativity, "CommunicationSkills": communication,
        "ArtisticSkills": artistic, "PracticalSkills": practical
    }

    student_df = pd.DataFrame([student_data])
    student_scaled = scaler.transform(student_df)

    # Prediction probabilities
    probs = model.predict_proba(student_scaled)[0]
    stream_names = le.classes_
    
    # Convert to DataFrame for visualization
    prob_df = pd.DataFrame({
        "Stream": stream_names,
        "Probability": probs * 100
    }).sort_values(by="Probability", ascending=False)

    # Show best stream
    st.success(f"✅ Best Recommended Stream: **{prob_df.iloc[0]['Stream']}**")

    # Show Bar Graph
    st.subheader("📊 Recommendation Probabilities")
    fig = px.bar(prob_df, x="Stream", y="Probability", 
                 color="Stream", text=prob_df["Probability"].map(lambda x: f"{x:.2f}%"),
                 title="Stream Recommendation Probabilities")
    fig.update_layout(yaxis_title="Probability (%)", xaxis_title="Streams")
    st.plotly_chart(fig)
