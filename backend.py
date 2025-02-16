from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Function to scrape LinkedIn (Basic)
def scrape_linkedin(job_title, location):
    job_title = job_title.replace(" ", "%20")
    location = location.replace(" ", "%20")
    url = f"https://www.linkedin.com/jobs/search?keywords={job_title}&location={location}"
    headers = {"User-Agent": "Mozilla/5.0"}

    print(f"Scraping LinkedIn: {url}")  # Debugging print

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []
    job_cards = soup.find_all("div", class_="base-card")  # Updated LinkedIn class
    print(f"Found {len(job_cards)} job cards on LinkedIn.")  # Debugging print

    for job_card in job_cards:
        title_elem = job_card.find("h3", class_="base-search-card__title")
        company_elem = job_card.find("h4", class_="base-search-card__subtitle")
        location_elem = job_card.find("span", class_="job-search-card__location")
        link_elem = job_card.find("a", href=True)

        if title_elem and company_elem and link_elem:
            title = title_elem.text.strip()
            company = company_elem.text.strip()
            location = location_elem.text.strip() if location_elem else "Not specified"
            link = link_elem["href"]
            jobs.append({"title": title, "company": company, "location": location, "link": link, "source": "LinkedIn"})

    return jobs

# Function to scrape TimesJobs
def scrape_timesjobs(job_title, location):
    job_title = job_title.replace(" ", "%20")
    location = location.replace(" ", "%20")
    url = f"https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords={job_title}&txtLocation={location}"
    headers = {"User-Agent": "Mozilla/5.0"}

    print(f"Scraping TimesJobs: {url}")  # Debugging print

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []
    job_cards = soup.find_all("li", class_="clearfix job-bx")
    print(f"Found {len(job_cards)} job cards on TimesJobs.")  # Debugging print

    for job_card in job_cards:
        title_elem = job_card.find("h2", class_="job-title")
        company_elem = job_card.find("h3", class_="company-name")
        location_elem = job_card.find("span", class_="location")
        link_elem = job_card.find("a", href=True)

        if title_elem and company_elem and link_elem:
            title = title_elem.text.strip()
            company = company_elem.text.strip()
            location = location_elem.text.strip() if location_elem else "Not specified"
            link = link_elem["href"]
            jobs.append({"title": title, "company": company, "location": location, "link": link, "source": "TimesJobs"})

    return jobs

# Function to scrape Glassdoor
def scrape_glassdoor(job_title, location):
    job_title = job_title.replace(" ", "%20")
    location = location.replace(" ", "%20")
    url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={job_title}&locT=C&locId={location}"
    headers = {"User-Agent": "Mozilla/5.0"}

    print(f"Scraping Glassdoor: {url}")  # Debugging print

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []
    job_cards = soup.find_all("li", class_="react-job-listing")
    print(f"Found {len(job_cards)} job cards on Glassdoor.")  # Debugging print

    for job_card in job_cards:
        title_elem = job_card.find("a", class_="jobLink")
        company_elem = job_card.find("div", class_="jobEmpolyerName")
        location_elem = job_card.find("span", class_="pr-xxsm")
        link_elem = job_card.find("a", href=True)

        if title_elem and company_elem and link_elem:
            title = title_elem.text.strip()
            company = company_elem.text.strip()
            location = location_elem.text.strip() if location_elem else "Not specified"
            link = "https://www.glassdoor.com" + link_elem["href"]
            jobs.append({"title": title, "company": company, "location": location, "link": link, "source": "Glassdoor"})

    return jobs

@app.route('/search', methods=['GET'])
def search_jobs():
    job_title = request.args.get('title', '')
    location = request.args.get('location', '')

    linkedin_jobs = scrape_linkedin(job_title, location)
    timesjobs_jobs = scrape_timesjobs(job_title, location)
    glassdoor_jobs = scrape_glassdoor(job_title, location)

    all_jobs = linkedin_jobs + timesjobs_jobs + glassdoor_jobs  # Combine all sources

    print(f"Total Jobs Found: {len(all_jobs)}")  # Debugging print

    return jsonify(all_jobs)

if __name__ == "__main__":
    app.run(debug=True)




# # python -m streamlit run app.py
