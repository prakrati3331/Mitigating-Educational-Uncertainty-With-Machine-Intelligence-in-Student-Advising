import streamlit as st
import pickle
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt

# --- Load Saved Elements ---
with open("pcb_scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

with open("pcb_course_classifier.pkl", "rb") as f:
    clf = pickle.load(f)

with open("pcb_label_encoder.pkl", "rb") as f:
    le_course = pickle.load(f)

with open("pcb_feature_columns.pkl", "rb") as f:
    feature_columns = pickle.load(f)

with open("pcb_dataset.pkl", "rb") as f:
    df = pickle.load(f)

# --- Recommendation Function ---
def recommend_courses(user_profile, top_n=5):
    # Scale input
    user_scaled = scaler.transform([user_profile])

    # Similarity with dataset
    sims = cosine_similarity(user_scaled, scaler.transform(df[feature_columns]))[0]
    df["similarity"] = sims

    # Aggregate similarity per course
    course_scores = df.groupby("Course")["similarity"].mean().reset_index()
    top_courses = course_scores.sort_values("similarity", ascending=False).head(top_n)

    recommendations = []
    for _, row in top_courses.iterrows():
        course = row["Course"]
        sim = row["similarity"]
        careers = df[df["Course"] == course]["Career Option"].unique()

        # --- Explainability: top supporting skills ---
        course_avg = df[df["Course"] == course][feature_columns].mean().values
        diffs = user_profile - course_avg
        top_features_idx = diffs.argsort()[::-1][:3]
        top_features = [feature_columns[i] for i in top_features_idx]

        recommendations.append({
            "Course": course,
            "Similarity": round(sim, 3),
            "Career Option": ", ".join(careers),
            "Top Supporting Skills": ", ".join(top_features)
        })

    return pd.DataFrame(recommendations)

# --- Streamlit UI ---
st.set_page_config(page_title="PCB Course & Career Recommendation System", layout="wide")
st.title("🧪 PCB Course & Career Recommendation System")
st.write("Enter your subject & skill scores to get personalized course and career recommendations, along with the strengths that make you suitable.")

# User input via sliders
st.sidebar.header("📝 Student Profile Input")
user_input = []
for col in feature_columns:
    val = st.sidebar.slider(f"{col}", 0, 100, 50)
    user_input.append(val)

if st.sidebar.button("🔍 Recommend PCB Courses & Careers"):
    recs = recommend_courses(user_input, top_n=5)
    
    st.subheader("📌 Top 5 Recommended PCB Courses, Careers & Strengths")
    st.dataframe(recs, use_container_width=True)

    # --- Visualization (Bar Chart of Similarity Scores) ---
    st.subheader("📊 Similarity Scores")
    fig, ax = plt.subplots()
    ax.bar(recs["Course"], recs["Similarity"], color="lightgreen")
    ax.set_ylabel("Similarity Score")
    ax.set_xlabel("Course")
    ax.set_title("Top-5 PCB Course Recommendations")
    st.pyplot(fig)
