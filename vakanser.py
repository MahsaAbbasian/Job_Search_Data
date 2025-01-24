import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime
import time

# --- Configuration ---
BASE_URL = "https://vakanser.se/alla/datajobb/i/goteborg/{}/"
OUTPUT_FILE = "all_jobs_vakanser.csv"
HTML_FILE = "public/vakanser.html"

# --- Helper Functions ---
def fetch_html(page_number, retries=3, delay=2):
    """
    Fetch HTML content for a specific page number, with retries.
    """
    for _ in range(retries):
        try:
            response = requests.get(BASE_URL.format(page_number), timeout=10)
            if response.status_code == 200:
                return response.content
            elif response.status_code == 404:
                print(f"Page {page_number} does not exist (404).")
                return None
        except requests.RequestException as e:
            print(f"Error fetching page {page_number}: {e}")
        time.sleep(delay)
    print(f"Failed to fetch page {page_number} after {retries} retries.")
    return None

def parse_html(html_content):
    """
    Parse job data from a single page of HTML content.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    sections = soup.find_all("section", class_="section")
    jobs = []

    for section in sections:
        spans = section.find_all("span", style="float: right; color: green;")
        for span in spans:
            raw_text = span.find_next_sibling(string=True)
            if raw_text and " - " in raw_text:
                date, employer = map(str.strip, raw_text.split(" - ", 1))
            else:
                date, employer = "Unknown Date", "Unknown Employer"

            try:
                date = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
            except ValueError:
                date = "Unknown Date"

            title_tag = span.find_next("a")
            title = title_tag.text.strip() if title_tag else "Unknown Title"
            job_link = f"https://vakanser.se{title_tag['href']}" if title_tag else "N/A"

            # Add job to the list
            jobs.append({
                "Date": date,
                "Title": title,
                "Employer": employer,
                "Job Link": job_link
            })

    print(f"Extracted {len(jobs)} jobs from the page.")
    return jobs

def scrape_all_pages(start_page=1, max_empty_pages=3):
    """
    Scrape job data from multiple pages.
    """
    all_jobs = []
    empty_page_count = 0
    page_number = start_page

    while empty_page_count < max_empty_pages:
        page_url = BASE_URL.format(page_number)
        print(f"Scraping {page_url}...")

        html_content = fetch_html(page_number)

        if not html_content:
            print(f"Page {page_number} is inaccessible or empty. Incrementing empty_page_count.")
            empty_page_count += 1
            page_number += 1
            continue

        jobs = parse_html(html_content)
        if not jobs:
            print(f"No jobs found on page {page_number}. Incrementing empty_page_count.")
            empty_page_count += 1
        else:
            empty_page_count = 0
            all_jobs.extend(jobs)

        page_number += 1

    # Remove duplicate jobs based on Title and Employer
    unique_jobs = pd.DataFrame(all_jobs).drop_duplicates(subset=["Title", "Employer"]).to_dict(orient="records")
    return unique_jobs

def save_to_csv(jobs, filename):
    """
    Save jobs to a CSV file.
    """
    pd.DataFrame(jobs).to_csv(filename, index=False)
    print(f"Saved {len(jobs)} jobs to {filename}.")

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
            file.write("<table border='1'><tr><th>Title</th><th>Employer</th><th>Date</th><th>Job Link</th></tr>")
            for job in grouped_jobs[date]:
                file.write("<tr>")
                file.write(f"<td>{job['Title']}</td>")
                file.write(f"<td>{job['Employer']}</td>")
                file.write(f"<td>{job['Date']}</td>")
                file.write(f"<td><a href='{job['Job Link']}' target='_blank'>View Job</a></td>")
                file.write("</tr>")
            file.write("</table>")
        file.write("</body></html>")
    print(f"Saved HTML file to {filename}.")

# --- Main Script ---
if __name__ == "__main__":
    print("Starting Vakanser Job Scraper...")

    all_jobs = scrape_all_pages(start_page=1, max_empty_pages=3)
    save_to_csv(all_jobs, OUTPUT_FILE)
    save_to_html(all_jobs, HTML_FILE)

    print("Vakanser Job Scraper completed successfully.")
