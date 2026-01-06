import streamlit as st
import pickle
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt

# --- Load Pickle Files ---
with open("commerce_scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

with open("commerce_course_classifier.pkl", "rb") as f:
    clf = pickle.load(f)

with open("commerce_label_encoder.pkl", "rb") as f:
    le_course = pickle.load(f)

with open("commerce_feature_columns.pkl", "rb") as f:
    feature_columns = pickle.load(f)

with open("commerce_dataset.pkl", "rb") as f:
    df = pickle.load(f)

# --- Recommendation Function ---
def recommend_courses(user_profile, top_n=5):
    user_scaled = scaler.transform([user_profile])
    
    sims = cosine_similarity(user_scaled, scaler.transform(df[feature_columns]))[0]
    df_temp = df.copy()
    df_temp["similarity"] = sims
    
    # Aggregate similarity per course
    course_scores = df_temp.groupby("Course")["similarity"].mean().reset_index()
    top_courses = course_scores.sort_values("similarity", ascending=False).head(top_n)
    
    recommendations = []
    for _, row in top_courses.iterrows():
        course = row["Course"]
        sim = row["similarity"]
        careers = df_temp[df_temp["Course"] == course]["Career Options"].unique()
        
        # 🔎 Find top contributing skills by comparing with course average
        course_avg = df_temp[df_temp["Course"] == course][feature_columns].mean().values
        diff = np.abs(user_profile - course_avg)
        top_features_idx = diff.argsort()[:3]  # 3 most aligned skills
        top_features = [feature_columns[i] for i in top_features_idx]
        
        recommendations.append({
            "Course": course,
            "Similarity": round(sim, 3),
            "Career Options": ", ".join(careers),
            "Top Skills": ", ".join(top_features)
        })
    
    return pd.DataFrame(recommendations)

# --- Streamlit UI ---
st.set_page_config(page_title="Course & Career Recommendation System", layout="wide")
st.title("🎓 Course & Career Recommendation System")
st.write("Enter your subject & skill scores to get personalized course and career recommendations.")

# Sidebar input
st.sidebar.header("📝 Student Profile Input")
user_input = []
for col in feature_columns:
    val = st.sidebar.slider(f"{col}", 0, 100, 50)
    user_input.append(val)

if st.sidebar.button("🔍 Recommend Courses & Careers"):
    recs = recommend_courses(user_input, top_n=5)
    
    st.subheader("📌 Top 5 Recommended Courses & Careers (with reasons)")
    st.dataframe(recs, use_container_width=True)

    # --- Visualization ---
    st.subheader("📊 Similarity Scores")
    fig, ax = plt.subplots()
    ax.bar(recs["Course"], recs["Similarity"], color="skyblue")
    ax.set_ylabel("Similarity Score")
    ax.set_xlabel("Course")
    ax.set_title("Top-5 Course Recommendations")
    st.pyplot(fig)
