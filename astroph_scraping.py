import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

# URL of the new submissions page for astro-ph
url = "https://arxiv.org/list/astro-ph/new"

# Send a GET request to the arXiv page
response = requests.get(url)
response.raise_for_status()  # Ensure the request was successful

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Find all entries in the new submissions list
entries = soup.find_all('dd')
titles_ids = soup.find_all('dt')
# List to store relevant papers
planet_papers = []


# Loop through entries and titles_ids together to extract details
for entry, title_id in zip(entries, titles_ids):
    # Extract the paper ID link in the correct format
    print(title_id.text)
    if "(replaced)" in title_id.text:
        continue  # Skip this entry as it is a replacement

    paper_id_link = title_id.find('a', title="Abstract")['href']
    paper_id = paper_id_link.split('/')[-1]
    print(paper_id)
    paper_url = f"https://arxiv.org/abs/{paper_id}"
    pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
    
    # Extract title and abstract
    title = entry.find('div', class_='list-title mathjax').get_text(strip=True).replace('Title:', '').strip()
    abstract = entry.find('p', class_='mathjax').get_text(strip=True)
    
    # Check if 'planet' is in the title or abstract (case-insensitive)
    if 'planet' in title.lower() or 'planet' in abstract.lower():
        authors = entry.find('div', class_='list-authors').get_text(strip=True).replace('Authors:', '').strip()
        
        # Collect relevant paper information
        paper_info = {
            'title': title,
            'authors': authors,
            'abstract': abstract,
            'url': paper_url,
            'PDF': pdf_url
        }
        planet_papers.append(paper_info)

# Get the count of new papers
num_papers = len(planet_papers)

# Construct the HTML email content
email_content = "New Planet-Related Papers on arXiv (astro-ph)\n\n"
for paper in planet_papers:
    email_content += f"Title: {paper['title']}\n\n"
    email_content += f"Authors: {paper['authors']}\n\n"
    email_content += f"Abstract: {paper['abstract']}\n\n"
    email_content += f"URL: {paper['url']}\n"
    email_content += f"PDF: {paper['PDF']}"
    email_content += "\n" + "-"*80 + "\n\n"


# Set up the email parameters
email_user = os.getenv("EMAIL_USER")
email_pass = os.getenv("EMAIL_PASS")  # 'ucer hkau wvic paoc'
from_email = email_user
to_email = "uyr2ce@virginia.edu"
subject = f"New Planet-Related Papers on arXiv (astro-ph): {num_papers} New Papers"

# Create the email
msg = MIMEMultipart()
msg['From'] = from_email
msg['To'] = to_email
msg['Subject'] = subject
msg.attach(MIMEText(email_content, 'plain'))

# Send the email securely using environment variables
try:
    # Establish a secure session with Gmail's outgoing SMTP server using your Gmail account
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()  # Enable security
        server.login(from_email, email_pass)  # Log in using environment variable-stored credentials
        server.sendmail(from_email, to_email, msg.as_string())
        print("Email sent successfully.")
except Exception as e:
    print(f"Error sending email: {e}")

    