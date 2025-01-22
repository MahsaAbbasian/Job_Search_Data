import requests
import pandas as pd
from datetime import datetime
import os
from collections import Counter

# --- Configuration ---
API_URL = "https://jobsearch.api.jobtechdev.se/search"
HEADERS = {"accept": "application/json"}
MUNICIPALITY_CODE = "1480"  # Göteborg
OCCUPATION_FIELD = "apaJ_2ja_LuF"  # Data/IT field
SEARCH_QUERY = (
    "developer OR engineer OR utvecklare OR Systemutvecklare OR Programmerare OR "
    "Embedded OR Backend OR Frontend OR Cloud OR Simulink OR mjukvaruingenjör OR "
    "Systemarkitekt OR Systemspecialist OR Kubernetes OR Database OR C++ OR Java OR Python"
)
OUTPUT_FILE = "filtered_jobs_gothenburg.csv"
HTML_FILE = "public/arbetsformedlingen.html"

NON_CONSULTANCY_COMPANIES = [
    "Volvo Personvagnar AB", "Gotit", "Volvo Car Corporation", "Mullvad VPN", "Trafikverket", "Skatteverket",
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
    "Mission Consultancy Assistance Sweden AB", "EdZa AB", "Knightec AB", "Friday Väst AB", "randstad ab", "Futuria People AB", "Goismo AB","MODERNERA AB", "Nexer Tech Talent AB", "NEXER GROUP", "Sebratec Gothenburg", "Rapid Consulting Sweden AB",
    "Deploja AB", "Integro Consulting AB", "Zcelero AB", "Framtiden AB", "Sogeti", "IBM Client Innovation Center Sweden AB",
    "Knowit Sweden", "Castra", "Annvin AB", "XLNT Recruitment Group", "TNG Group AB", "5 Monkeys Agency AB",
    "Nexer Recruit", "H Sustain AB", "B3 Consulting Group", "Prevas", "JP IT-Konsult i Stockholm AB", "Decerno",
    "AFRY AB", "Arctic Group"
]

# --- Helper Functions ---
def fetch_all_jobs(query, municipality, occupation_field):
    print(f"[{datetime.now()}] Fetching job data...")
    all_jobs = []
    offset = 0
    limit = 50

    while True:
        params = {
            "q": query,
            "municipality": municipality,
            "occupation-field": occupation_field,
            "limit": limit,
            "offset": offset
        }
        response = requests.get(API_URL, headers=HEADERS, params=params)
        if response.status_code == 400:
            print("Error: Bad request. Please check your query parameters.")
            print(f"Response: {response.text}")
            break
        if response.status_code != 200:
            print(f"Error: Unable to fetch data. Status Code {response.status_code}")
            break

        jobs = response.json().get("hits", [])
        if not jobs:
            break

        all_jobs.extend(jobs)
        offset += limit

    print(f"Fetched a total of {len(all_jobs)} jobs.")
    return all_jobs

def classify_job(employer, description):
    """
    Classify a job based on its employer and description using predefined company lists.
    """
    employer = employer.lower()
    description = description.lower()

    for company in NON_CONSULTANCY_COMPANIES:
        if company.lower() in employer:
            return "Non-Consultancy"

    for company in CONSULTANCY_COMPANIES:
        if company.lower() in employer:
            return "Consultancy"

    # Use fallback logic
    if "consult" in employer or "consultancy" in description:
        return "Consultancy"

    return "Uncategorized"

def filter_and_categorize_jobs(jobs):
    print(f"[{datetime.now()}] Filtering and categorizing jobs...")
    categorized_jobs = []

    for job in jobs:
        employer = job.get("employer", {}).get("name", "").strip()
        description = job.get("description", {}).get("text", "").lower()
        headline = job.get("headline", "").strip()
        publication_date = job.get("publication_date", "")
        job_link = job.get("webpage_url", "")

        category = classify_job(employer, description)

        categorized_jobs.append({
            "Title": headline,
            "Employer": employer,
            "Category": category,
            "Date": publication_date[:10],  # Only keep the date
            "Job Link": job_link
        })

    return categorized_jobs

def group_jobs_by_date(jobs):
    print(f"[{datetime.now()}] Grouping jobs by date...")
    grouped_jobs = {}
    for job in jobs:
        pub_date = job["Date"]
        if pub_date not in grouped_jobs:
            grouped_jobs[pub_date] = []
        grouped_jobs[pub_date].append(job)

    sorted_dates = sorted(grouped_jobs.keys(), reverse=True)
    return grouped_jobs, sorted_dates

def save_to_csv(jobs, filename):
    print(f"[{datetime.now()}] Saving jobs to {filename}...")
    pd.DataFrame(jobs).to_csv(filename, index=False)
    print(f"Saved {len(jobs)} jobs to {filename}.")

def save_to_html(grouped_jobs, sorted_dates, filename):
    print(f"[{datetime.now()}] Saving jobs to {filename}...")
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, "w", encoding="utf-8") as file:
        file.write("<html><head>")
        file.write("<title>Job Listings by Date</title>")
        file.write("<link rel='stylesheet' href='styles.css'></head><body>")
        file.write("<h1>Job Listings by Date</h1>")

        for date in sorted_dates:
            file.write(f"<h2>Jobs from {date}</h2>")
            file.write("<table border='1'><tr><th>Title</th><th>Employer</th><th>Category</th><th>Date</th><th>Job Link</th></tr>")
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
    print(f"Saved HTML file: {filename}")

# --- Main Script ---
if __name__ == "__main__":
    print(f"[{datetime.now()}] Job Scheduler started...")
    jobs = fetch_all_jobs(SEARCH_QUERY, MUNICIPALITY_CODE, OCCUPATION_FIELD)
    if not jobs:
        print("[ERROR] No jobs fetched. Exiting.")
        exit()

    categorized_jobs = filter_and_categorize_jobs(jobs)
    grouped_jobs, sorted_dates = group_jobs_by_date(categorized_jobs)
    
    save_to_csv(categorized_jobs, OUTPUT_FILE)
    save_to_html(grouped_jobs, sorted_dates, HTML_FILE)

    job_counts = Counter(job["Category"] for job in categorized_jobs)
    print(f"Job counts by category: {job_counts}")
    print(f"[{datetime.now()}] Job Scheduler completed.")
