from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# LinkedIn Scraper
def scrape_linkedin(job_title, location):
    job_title = job_title.replace(" ", "%20")
    location = location.replace(" ", "%20")
    url = f"https://www.linkedin.com/jobs/search?keywords={job_title}&location={location}"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []
    job_cards = soup.find_all("div", class_="base-card")

    for job_card in job_cards:
        title_elem = job_card.find("h3", class_="base-search-card__title")
        company_elem = job_card.find("h4", class_="base-search-card__subtitle")
        location_elem = job_card.find("span", class_="job-search-card__location")
        link_elem = job_card.find("a", href=True)

        if title_elem and company_elem and link_elem:
            title = title_elem.text.strip()
            company = company_elem.text.strip()
            job_location = location_elem.text.strip() if location_elem else "Not specified"
            link = link_elem["href"]
            jobs.append({
                "title": title,
                "company": company,
                "location": job_location,
                "link": link,
                "source": "LinkedIn"
            })

    return jobs

# Adzuna API Scraper
def scrape_adzuna(job_title, location):
    APP_ID = "19c2df2a"
    API_KEY = "9856459a9eb7e5b34fb4b0770683d028"
    country = "in"

    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
    params = {
        "app_id": APP_ID,
        "app_key": API_KEY,
        "what": job_title,
        "where": location,
        "results_per_page": 10,
        "content-type": "application/json"
    }

    response = requests.get(url, params=params)
    jobs = []

    if response.status_code == 200:
        data = response.json()
        for result in data.get("results", []):
            title = result.get("title")
            company = result.get("company", {}).get("display_name", "N/A")
            job_location = result.get("location", {}).get("display_name", "Remote/Not Specified")
            link = result.get("redirect_url")

            jobs.append({
                "title": title,
                "company": company,
                "location": job_location,
                "link": link,
                "source": "Adzuna"
            })

    return jobs

# JSearch API Scraper (replacing RemoteOK)
def scrape_jsearch(job_title, location):
    url = "https://jsearch.p.rapidapi.com/search"
    querystring = {
        "query": f"{job_title} in {location}",
        "page": "1",
        "num_pages": "1"
    }

    headers = {
        "X-RapidAPI-Key": "3ea05b6d4dmshe1086e619de148ep1b58b9jsn87d5a35bb710",
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    jobs = []

    if response.status_code == 200:
        data = response.json()
        for job in data.get("data", []):
            jobs.append({
                "title": job.get("job_title"),
                "company": job.get("employer_name"),
                "location": job.get("job_city", "Remote/Not Specified"),
                "link": job.get("job_apply_link"),
                "source": "JSearch"
            })
    else:
        print("Error from JSearch:", response.status_code, response.text)

    return jobs

# API route
@app.route('/search', methods=['GET'])
def search_jobs():
    job_title = request.args.get('title', '')
    location = request.args.get('location', '')

    linkedin_jobs = scrape_linkedin(job_title, location)
    adzuna_jobs = scrape_adzuna(job_title, location)
    jsearch_jobs = scrape_jsearch(job_title, location)

    all_jobs = linkedin_jobs + adzuna_jobs + jsearch_jobs
    return jsonify(all_jobs)

if __name__ == "__main__":
    app.run(debug=True)

