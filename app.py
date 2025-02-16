import streamlit as st
import requests

st.title("🔍 Multi-Platform Job Search")

job_title = st.text_input("Enter Job Title", "Python Developer")
location = st.text_input("Enter Location", "Remote")

if st.button("Search Jobs"):
    api_url = f"http://127.0.0.1:5000/search?title={job_title}&location={location}"
    response = requests.get(api_url)

    if response.status_code == 200:
        jobs = response.json()  # Directly store the list
        
        if jobs:  # Check if the list is not empty
            for job in jobs:
                st.markdown(f"""
                🔹 **[{job['title']}]({job['link']})**  
                **Company:** {job['company']}  
                **Source:** {job['source']}  
                """)
        else:
            st.warning("No jobs found. Try different keywords.")
    else:
        st.error("Error fetching job listings.")
