import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime

# --- Configuration ---
BASE_URL = "https://arbetsformedlingen.se/platsbanken/annonser?q=software%20developer&l=2:zdoY_6u5_Krt&page={}"
OUTPUT_FILE = "filtered_jobs_arbetsformedlingen.csv"
HTML_FILE = "public/arbetsformedlingen.html"

SEARCH_QUERY = (
    "developer OR engineer OR utvecklare OR Systemutvecklare OR Programmerare OR "
    "Embedded OR Backend OR Frontend OR Cloud OR Simulink OR mjukvaruingenjör OR "
    "Systemarkitekt OR Systemspecialist OR Kubernetes OR Database OR C++ OR Java OR Python"
)
SEARCH_KEYWORDS = [keyword.strip().lower() for keyword in SEARCH_QUERY.split("OR")]

NON_CONSULTANCY_COMPANIES = [
    "Volvo Personvagnar AB", "Gotit", "Volvo Car Corporation", "Mullvad VPN", "Trafikverket", "Skatteverket",
    # Add more companies as needed...
]

CONSULTANCY_COMPANIES = [
    "MODERNERA AB", "Nexer Tech Talent AB", "NEXER GROUP", "Sebratec Gothenburg", "Rapid Consulting Sweden AB",
    # Add more companies as needed...
]

# --- Helper Functions ---
def classify_job(employer):
    """
    Classify a job based on employer name using predefined lists.
    """
    employer_cleaned = employer.strip().lower()

    for company in NON_CONSULTANCY_COMPANIES:
        if company.lower() in employer_cleaned:
            return "Non-Consultancy"

    for company in CONSULTANCY_COMPANIES:
        if company.lower() in employer_cleaned:
            return "Consultancy"

    return "Uncategorized"

def fetch_html(page_number):
    """
    Fetch HTML content for a specific page number.
    """
    url = BASE_URL.format(page_number)
    print(f"[{datetime.now()}] Fetching page {page_number} from {url}...")
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    print(f"Error: Unable to fetch page {page_number}. Status: {response.status_code}")
    return None

def parse_html(html_content):
    """
    Parse job data from a single page of HTML content.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    job_listings = soup.find_all("div", class_="job-card")  # Update to match Platsbanken's structure
    jobs = []

    for listing in job_listings:
        # Extract job title
        title_tag = listing.find("h3", class_="job-card-title")
        title = title_tag.text.strip() if title_tag else "Unknown Title"

        # Extract employer
        employer_tag = listing.find("span", class_="job-card-company")
        employer = employer_tag.text.strip() if employer_tag else "Unknown Employer"

        # Extract date
        date_tag = listing.find("time", class_="job-card-date")
        date = date_tag["datetime"] if date_tag else "Unknown Date"

        # Convert date format
        try:
            date = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            date = "Unknown Date"

        # Extract job link
        link_tag = listing.find("a", href=True)
        job_link = f"https://arbetsformedlingen.se{link_tag['href']}" if link_tag else "N/A"

        # Filter by SEARCH_KEYWORDS
        if not any(keyword in title.lower() for keyword in SEARCH_KEYWORDS):
            continue  # Skip jobs that don't match the search query

        # Classify the job
        category = classify_job(employer)

        # Add job to the list
        jobs.append({
            "Date": date,
            "Title": title,
            "Employer": employer,
            "Category": category,
            "Job Link": job_link
        })

    print(f"[{datetime.now()}] Extracted {len(jobs)} jobs from the page.")
    return jobs

def scrape_all_pages(start_page=1, max_empty_pages=3):
    """
    Scrape job data from multiple pages.
    """
    all_jobs = []
    empty_page_count = 0
    page_number = start_page

    while empty_page_count < max_empty_pages:
        html_content = fetch_html(page_number)
        if not html_content:
            empty_page_count += 1
            page_number += 1
            continue

        jobs = parse_html(html_content)
        if not jobs:
            empty_page_count += 1
        else:
            empty_page_count = 0  # Reset if jobs are found
            all_jobs.extend(jobs)

        page_number += 1

    return pd.DataFrame(all_jobs).drop_duplicates(subset=["Title", "Employer"]).to_dict(orient="records")

def save_to_csv(jobs, filename):
    """
    Save jobs to a CSV file.
    """
    pd.DataFrame(jobs).to_csv(filename, index=False)
    print(f"[{datetime.now()}] Saved {len(jobs)} jobs to {filename}.")

def save_to_html(jobs, filename):
    """
    Save jobs to an HTML file.
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
    print(f"[{datetime.now()}] Saved HTML file to {filename}.")

# --- Main Script ---
if __name__ == "__main__":
    print(f"[{datetime.now()}] Starting Arbetsförmedlingen Job Scraper...")

    # Scrape job data
    all_jobs = scrape_all_pages(start_page=1, max_empty_pages=3)

    # Save jobs to CSV and HTML
    save_to_csv(all_jobs, OUTPUT_FILE)
    save_to_html(all_jobs, HTML_FILE)

    print(f"[{datetime.now()}] Arbetsförmedlingen Job Scraper completed successfully.")
