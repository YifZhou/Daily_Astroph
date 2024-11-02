import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
    
from openai import OpenAI
import pyttsx3

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
    if "(replaced)" in title_id.text:
        continue  # Skip this entry as it is a replacement

    paper_id_link = title_id.find('a', title="Abstract")['href']
    paper_id = paper_id_link.split('/')[-1]
    paper_url = f"https://arxiv.org/abs/{paper_id}"
    pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
    
    # Extract title and abstract
    title = entry.find('div', class_='list-title mathjax').get_text(strip=True).replace('Title:', '').strip()
    abstract = entry.find('p', class_='mathjax').get_text(strip=True)
    
    # Check if 'planet' is in the title or abstract (case-insensitive)
    if 'planet' in title.lower() or 'planet' in abstract.lower():
        authors = entry.find('div', class_='list-authors').get_text(strip=True).replace('Authors:', '').strip()
        authorList = authors.split(',')
        if len(authorList) > 3:
            authors = ', '.join(authorList[:3]) + ', et al.'
        else:
            authors = ', '.join(authorList)
        # Collect relevant paper information
        paper_info = {
            'title': title,
            'authors': authors,
            'abstract': abstract,
            'url': paper_url,
            'pdf_url': pdf_url
        }
        planet_papers.append(paper_info)

# Get the count of new papers
num_papers = len(planet_papers)

email_content = """
<html>
<body>
"""
podcast_content = []

for paper in planet_papers:
    podcast_content.append((paper['title'], paper['abstract']))


client = OpenAI(
    # This is the default and can be omitted
    api_key="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",
)


# Configure OpenAI API key


def generate_podcast_script(abstracts):
    # Step 1: Combine abstracts into a coherent, conversational podcast-style script
    prompt = (
        "You're a podcast host. Take the following scientific paper abstracts and "
        "turn them into a coherent, engaging script for a podcast episode. "
        "Make it conversational and accessible, tying the abstracts together smoothly.\n\n"
    )
    for i, abstract in enumerate(abstracts, 1):
        prompt += f"title:{abstract[0]}\n{abstract[1]}\n\n"

    
    return prompt

def convert_script_to_speech(script):
    # Initialize the pyttsx3 engine
    engine = pyttsx3.init()
    engine.setProperty("rate", 150)  # Set speaking rate
    engine.setProperty("volume", 1)  # Set volume level

    # Generate speech from script
    engine.say(script)
    engine.save_to_file(script, "podcast_episode.mp3")  # Save as mp3 file
    engine.runAndWait()
    print("Podcast episode audio generated as 'podcast_episode.mp3'.")

# Sample abstracts - Replace these with actual abstracts extracted from arXiv

# Generate the podcast script
podcast_script = generate_podcast_script(podcast_content)
print("Generated Podcast Script:\n", podcast_script)

# Convert the script to speech
# convert_script_to_speech(podcast_script)