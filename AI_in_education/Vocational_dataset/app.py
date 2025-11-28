# --- Streamlit App for Vocational Course & Career Guidance ---
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt

# --- Load Saved Models and Data ---
with open("vocational_scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

with open("vocational_course_classifier.pkl", "rb") as f:
    clf = pickle.load(f)

with open("vocational_label_encoder.pkl", "rb") as f:
    le_course = pickle.load(f)

with open("vocational_feature_columns.pkl", "rb") as f:
    feature_columns = pickle.load(f)

with open("vocational_dataset.pkl", "rb") as f:
    df = pickle.load(f)

# --- Streamlit UI ---
st.set_page_config(page_title="Vocational Career Guidance System", layout="wide")

st.title("🎓 Vocational Career Guidance System")
st.write("Get personalized **course recommendations** and explore **career options** based on your skills and subjects.")

# --- Input Section ---
st.sidebar.header("📌 Enter Your Profile")

user_profile = []
for col in feature_columns:
    val = st.sidebar.slider(f"{col}", min_value=0, max_value=100, value=50)
    user_profile.append(val)

user_profile = np.array(user_profile)

# --- Recommendation System ---
def recommend_courses(user_profile, top_n=5):
    # Scale user input
    user_scaled = scaler.transform([user_profile])
    
    # Cosine similarity with dataset
    sims = cosine_similarity(user_scaled, scaler.transform(df[feature_columns]))[0]
    df_temp = df.copy()
    df_temp["similarity"] = sims
    
    # Aggregate similarity per course
    course_scores = df_temp.groupby("Course")["similarity"].mean().reset_index()
    top_courses = course_scores.sort_values("similarity", ascending=False).head(top_n)
    
    # Collect career options
    recommendations = []
    for _, row in top_courses.iterrows():
        course = row["Course"]
        sim = row["similarity"]
        careers = df_temp[df_temp["Course"] == course]["Career Options"].unique()
        recommendations.append({
            "Course": course,
            "Similarity": round(sim, 3),
            "Career Options": ", ".join(careers)
        })
    
    return pd.DataFrame(recommendations)

# --- Predict Course (Classifier) ---
def predict_course(user_profile):
    user_scaled = scaler.transform([user_profile])
    pred = clf.predict(user_scaled)
    course = le_course.inverse_transform(pred)[0]
    return course

# --- Main Display ---
if st.sidebar.button("🔍 Get Recommendations"):
    st.subheader("✅ Predicted Best Fit Course")
    best_course = predict_course(user_profile)
    st.success(f"🎯 {best_course}")
    
    st.subheader("📊 Top Recommended Courses & Careers")
    recs = recommend_courses(user_profile, top_n=5)
    st.dataframe(recs, use_container_width=True)

    # --- Bar Graph: Similarity Scores ---
    st.subheader("📈 Similarity Scores for Recommended Courses")
    fig, ax = plt.subplots()
    ax.bar(recs["Course"], recs["Similarity"], color="skyblue")
    ax.set_ylabel("Similarity Score")
    ax.set_xlabel("Course")
    ax.set_title("Top Recommended Courses (Cosine Similarity)")
    st.pyplot(fig)

    # --- Pie Chart: Career Options of Predicted Course ---
    st.subheader("🥧 Career Options Distribution for Predicted Course")
    careers = df[df["Course"] == best_course]["Career Options"].unique()
    career_counts = pd.Series(careers)
    
    fig2, ax2 = plt.subplots()
    ax2.pie([1]*len(career_counts), labels=career_counts, autopct='%1.1f%%', startangle=140)
    ax2.set_title(f"Career Options for {best_course}")
    st.pyplot(fig2)

else:
    st.info("👉 Adjust your subject & skill levels in the sidebar, then click **Get Recommendations**.")
