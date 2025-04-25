import requests
import pandas as pd
from datetime import datetime
from collections import Counter
import os

# --- Configuration ---
API_URL = "https://jobsearch.api.jobtechdev.se/search"
HEADERS = {"accept": "application/json"}
MUNICIPALITY_CODE = "1480"  # Göteborg
OCCUPATION_FIELD = "apaJ_2ja_LuF"  # Data/IT field
SEARCH_QUERY = (
    "developer", "engineer", "utvecklare", "systemutvecklare", "programmerare",
    "software", "mjukvaruutvecklare", "systemdeveloper", "backend", "frontend",
    "cloud", "devops", "python", "java", "c++", "embedded", "programmer", "database",
    "junior", "entry level", "graduate", "trainee", "intern", "praktik", "student",
    "ai", "ml", "data scientist", "data analyst", "fullstack", "webb", "mobile",
    "android", "ios", "typescript", "javascript", "react", "vue", "dotnet", "ci/cd"
)
NON_CONSULTANCY_COMPANIES = [
    "Etraveli Group AB","Volvo Personvagnar AB", "Gotit", "Volvo Car Corporation", "Mullvad VPN", "Trafikverket", "Skatteverket",
    "Jeppesen", "Hogia HR Systems AB", "Hogia Infrastructure Products AB", "Hogia Facility Management AB",
    "Hogia Business Products AB", "deepNumbers systems AB", "Åre Kommun", "Provide IT Sweden AB", "Acoem AB",
    "Icomera AB", "Volvo Group", "Drakryggen", "Saab AB", "Qamcom", "Humly", "Compary AB", "Assemblin",
    "QRTECH", "Novacura", "NOVENTUS SYSTEMS AKTIEBOLAG", "Polismyndigheten", "SOLTAK AB", "Göteborg Energi",
    "Vipas AB", "HaleyTek AB", "Zacco Digital Trust", "Autocom", "Benify", "Logikfabriken AB", "DENTSPLY IH AB",
    "Cambio", "Nexus - Powered by IN Groupe", "Skandia", "SJ AB", "Epiroc", "Hitachi Energy", "Pensionsmyndigheten",
    "Nordea", "Expleo Technology Nordic AB", "Scania CV AB", "Din Psykolog Sverige AB", "Wehype", "Flower",
    "Tutus Data", "Xensam", "BAE Systems Hägglunds AB", "ITAB", "RASALA Group AB"
]

CONSULTANCY_COMPANIES = [
    "Academic Work", "Academic Work Sweden AB", "Quest Consulting Sverige AB", "Jobnet AB", "Quest Consulting Sverige AB","Explipro Group", "Explipro Group AB", "Mission Consultancy Assistance Sweden AB", "EdZa AB", "Knightec AB", "Friday Väst AB", "randstad ab", "Futuria People AB", "Goismo AB","MODERNERA AB", "Nexer Tech Talent AB", "NEXER GROUP", "Sebratec Gothenburg", "Rapid Consulting Sweden AB",
    "Deploja AB", "Integro Consulting AB", "Zcelero AB", "Framtiden AB", "Sogeti", "IBM Client Innovation Center Sweden AB",
    "Knowit Sweden", "Castra", "Annvin AB", "XLNT Recruitment Group", "TNG Group AB", "5 Monkeys Agency AB",
    "Nexer Recruit", "H Sustain AB", "B3 Consulting Group", "Prevas", "JP IT-Konsult i Stockholm AB", "Decerno",
    "AFRY AB", "Arctic Group"
]

OUTPUT_FILE = "filtered_jobs_gothenburg.csv"
HTML_FILE = "public/arbetsformedlingen.html"

# --- Functions ---
def fetch_jobs(query, municipality, occupation_field):
    """
    Fetch all relevant jobs from the API.
    """
    print(f"[{datetime.now()}] Fetching job data...")
    all_jobs = []
    offset = 0
    limit = 50

    while True:
        params = {
            "q": query,  # Expanded query for better coverage
            "municipality": municipality,
            "occupation-field": occupation_field,
            "limit": limit,
            "offset": offset
        }
        response = requests.get(API_URL, headers=HEADERS, params=params)
        if response.status_code == 400:
            print(f"[ERROR] Bad request. Response: {response.text}")
            break
        if response.status_code != 200:
            print(f"[ERROR] Unable to fetch data. Status Code: {response.status_code}")
            break

        jobs = response.json().get("hits", [])
        if not jobs:
            break

        all_jobs.extend(jobs)
        offset += limit

    print(f"[{datetime.now()}] Fetched a total of {len(all_jobs)} jobs.")
    return all_jobs

def classify_job(employer, description):
    """
    Classify job based on employer and description.
    """
    employer = employer.lower()
    description = description.lower()

    # Use predefined lists for classification
    if any(company.lower() in employer for company in NON_CONSULTANCY_COMPANIES):
        return "Non-Consultancy"
    if any(company.lower() in employer for company in CONSULTANCY_COMPANIES):
        return "Consultancy"

    # Fallback classification
    if "consult" in employer or "consultancy" in description:
        return "Consultancy"
    return "Uncategorized"

def process_jobs(jobs):
    """
    Process and categorize jobs.
    """
    processed_jobs = []
    for job in jobs:
        employer = job.get("employer", {}).get("name", "").strip()
        description = job.get("description", {}).get("text", "").strip().lower()
        title = job.get("headline", "").strip()
        date = job.get("publication_date", "")[:10]  # Extract date part
        job_link = job.get("webpage_url", "")

        category = classify_job(employer, description)

        processed_jobs.append({
            "Title": title,
            "Employer": employer,
            "Category": category,
            "Date": date,
            "Job Link": job_link
        })

    return processed_jobs

def save_to_csv(jobs, filename):
    """
    Save processed jobs to a CSV file.
    """
    pd.DataFrame(jobs).to_csv(filename, index=False)
    print(f"[{datetime.now()}] Saved {len(jobs)} jobs to {filename}.")

def save_to_html(jobs, filename):
    """
    Save jobs to an HTML file grouped by date.
    """
    grouped_jobs = {}
    for job in jobs:
        pub_date = job["Date"]
        if pub_date not in grouped_jobs:
            grouped_jobs[pub_date] = []
        grouped_jobs[pub_date].append(job)

    sorted_dates = sorted(grouped_jobs.keys(), reverse=True)
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, "w", encoding="utf-8") as file:
        file.write("<html><head><title>Job Listings</title>")
        file.write("<link rel='stylesheet' href='styles.css'></head><body>")
        file.write("<h1>Job Listings by Date</h1>")

        for date in sorted_dates:
            file.write(f"<h2>Jobs from {date}</h2>")
            file.write("<table><tr><th>Title</th><th>Employer</th><th>Category</th><th>Date</th><th>Job Link</th></tr>")
            for job in grouped_jobs[date]:
                file.write("<tr>")
                file.write(f"<td>{job['Title']}</td>")
                file.write(f"<td>{job['Employer']}</td>")
                file.write(f"<td>{job['Category']}</td>")
                file.write(f"<td>{job['Date']}</td>")
                file.write(f"<td><a href='{job['Job Link']}' target='_blank'>View Job</a></td>")
                file.write("</tr>")
            file.write("</table>")
        file.write("</body></html>")
    print(f"[{datetime.now()}] Saved jobs to HTML file: {filename}")

# --- Main ---
if __name__ == "__main__":
    print(f"[{datetime.now()}] Starting job fetch process...")

    jobs = fetch_jobs(SEARCH_QUERY, MUNICIPALITY_CODE, OCCUPATION_FIELD)
    if not jobs:
        print("[ERROR] No jobs fetched. Exiting.")
        exit()

    processed_jobs = process_jobs(jobs)

    # Save to CSV and HTML
    save_to_csv(processed_jobs, OUTPUT_FILE)
    save_to_html(processed_jobs, HTML_FILE)

    job_counts = Counter(job["Category"] for job in processed_jobs)
    print(f"[{datetime.now()}] Job counts by category: {job_counts}")
    print(f"[{datetime.now()}] Job fetch process completed.")
