import requests
import pandas as pd
import os
from datetime import datetime
from bs4 import BeautifulSoup

# --- Constants ---
ARBETSFORMEDLINGEN_OUTPUT_HTML = "public/arbetsformedlingen.html"
VAKANSER_OUTPUT_HTML = "public/vakanser.html"
ARBETSFORMEDLINGEN_OUTPUT_CSV = "filtered_jobs_arbetsformedlingen.csv"
VAKANSER_OUTPUT_CSV = "filtered_jobs_vakanser.csv"
SEARCH_QUERY = "Software Developer"
MUNICIPALITY_CODE = "1480"  # Göteborg
OCCUPATION_FIELD = "apaJ_2ja_LuF"

HEADERS = {"accept": "application/json"}
ARBETSFORMEDLINGEN_API_URL = "https://jobsearch.api.jobtechdev.se/search"
VAKANSER_URL = "https://vakanser.se/alla/datajobb/i/goteborg/2/"

# --- Helper Functions ---
def sanitize_text(text):
    """Handle encoding issues in text."""
    return text.encode('utf-8').decode('utf-8', 'replace')

# --- Arbetsförmedlingen Fetch ---
def fetch_arbetsformedlingen_jobs(query, municipality, occupation_field):
    print(f"[{datetime.now()}] Fetching jobs from Arbetsförmedlingen...")
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
        response = requests.get(ARBETSFORMEDLINGEN_API_URL, headers=HEADERS, params=params)

        if response.status_code != 200:
            print(f"Error: Unable to fetch data. Status Code {response.status_code}")
            break

        jobs = response.json().get("hits", [])
        if not jobs:
            break

        all_jobs.extend(jobs)
        offset += limit

    print(f"Fetched {len(all_jobs)} jobs from Arbetsförmedlingen.")
    return all_jobs

# --- Vakanser Fetch ---
def fetch_vakanser_jobs():
    print(f"[{datetime.now()}] Fetching jobs from Vakanser...")
    response = requests.get(VAKANSER_URL)

    if response.status_code != 200:
        print(f"Error: Unable to fetch data. Status Code {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    job_list = []

    for job in soup.find_all("div", class_="job-listing"):
        title = job.find("a").text.strip()
        link = job.find("a")["href"]
        date = job.find("span", class_="date").text.strip()
        job_list.append({
            "Title": title,
            "Job Link": link,
            "Publication Date": date,
            "Source": "Vakanser"
        })

    print(f"Fetched {len(job_list)} jobs from Vakanser.")
    return job_list

# --- Save Functions ---
def save_to_csv(jobs, filename):
    print(f"[{datetime.now()}] Saving jobs to {filename}...")
    pd.DataFrame(jobs).to_csv(filename, index=False)
    print(f"Saved {len(jobs)} jobs to {filename}.")

def save_to_html(jobs, filename):
    print(f"[{datetime.now()}] Saving jobs to HTML file: {filename}")
    with open(filename, "w", encoding="utf-8") as file:
        file.write("<html><head><title>Job Listings</title></head><body>")
        file.write("<h1>Job Listings</h1><table border='1'><tr>")
        file.write("<th>Title</th><th>Publication Date</th><th>Job Link</th></tr>")

        for job in jobs:
            file.write("<tr>")
            file.write(f"<td>{sanitize_text(job['Title'])}</td>")
            file.write(f"<td>{job['Publication Date']}</td>")
            file.write(f"<td><a href='{job['Job Link']}' target='_blank'>View Job</a></td>")
            file.write("</tr>")

        file.write("</table></body></html>")
    print(f"Saved HTML file: {filename}")

# --- Main Function ---
def main():
    # Arbetsförmedlingen Jobs
    arbetsformedlingen_jobs = fetch_arbetsformedlingen_jobs(SEARCH_QUERY, MUNICIPALITY_CODE, OCCUPATION_FIELD)
    categorized_arbetsformedlingen_jobs = [
        {"Title": job.get("headline", "N/A"), "Job Link": job.get("webpage_url", "#"), "Publication Date": job.get("publication_date", "N/A")}
        for job in arbetsformedlingen_jobs
    ]
    save_to_csv(categorized_arbetsformedlingen_jobs, ARBETSFORMEDLINGEN_OUTPUT_CSV)
    save_to_html(categorized_arbetsformedlingen_jobs, ARBETSFORMEDLINGEN_OUTPUT_HTML)

    # Vakanser Jobs
    vakanser_jobs = fetch_vakanser_jobs()
    save_to_csv(vakanser_jobs, VAKANSER_OUTPUT_CSV)
    save_to_html(vakanser_jobs, VAKANSER_OUTPUT_HTML)

# Run the script
if __name__ == "__main__":
    main()
