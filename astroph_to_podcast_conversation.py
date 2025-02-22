import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from datetime import datetime
now = datetime.now()
date = now.strftime("%Y-%m-%d")
    
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
    if ('planet' in title.lower())\
          or ('planet' in abstract.lower())\
              and (not 'planetary nebula' in title.lower())\
                  and (not 'planetary nebula' in abstract.lower()):
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

abstractList = []

for paper in planet_papers:
    abstractDict_i = {'title': paper['title'], 'authors': paper['authors'], 'abstract': paper['abstract']}
    abstractList.append(abstractDict_i)


# Doing some DeepSeek Shit

import requests
import time

# Replace with your DeepSeek API key
API_KEY = os.getenv("DeepSeek_API")  #

# DeepSeek API endpoint for summarization (replace with the actual endpoint)
API_URL = 'https://api.deepseek.com/chat/completions'

# Headers for the API request
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

def abstract_to_podcast_script(papers, maxTry=60):
    """
    Sends the abstract to the DeepSeek API for summarization.
    """
    # combine papers into a string
    inputContent = ''
    for i, paper in enumerate(papers):
        title_i = paper['title']
        abstract_i = paper['abstract']
        author_i = paper['authors']
        paperString = f"title {i+1:d}: {title_i}" + '\n' + f"authors: {author_i}" + '\n' + f"abstract: {abstract_i}"
        inputContent += paperString + '\n_\n'
    prompt = f"""You will output ONLY valid SSML for a podcast script - no explanations, no additional text.

Your task is to convert the technical abstract below into a casual, engaging conversation between ExoDaily hosts Mike and Sarah, who make complex scientific topics fun and accessible.

Required Show Introduction:
Begin with: "Welcome to ExoDaily, where we make space science simple! I'm Mike," followed by Sarah's introduction. This must be included in the first speaking segment.

Host Personalities:
- Mike (voice="en-US-Neural2-I"): Enthusiastic and curious, loves pop culture references
- Sarah (voice="en-US-Neural2-F"): Expert at breaking down complex concepts with analogies, warm teaching style

Required SSML Structure:
<speak>
    <voice name="en-US-Neural2-I">[Mike's dialogue]</voice>
    <break time="500ms"/>
    <voice name="en-US-Neural2-F">[Sarah's dialogue]</voice>
    [... continue alternating ...]
</speak>

SSML Guidelines:
- Add <break time="300ms"/> for natural pauses
- Use <emphasis level="strong"> for key revelations
- Use <say-as interpret-as="characters"> for acronyms (TOI-[number], HST, JWST)
- DO NOT use any unsupported SSML tags
- Ensure all tags are properly nested and closed

Required Pronunciation Patterns:
1. ANY "TOI-[number]" reference must be formatted as:
   <say-as interpret-as="characters">TOI</say-as> <say-as interpret-as="cardinal">[number]</say-as>
   Examples:
   - "TOI-150" → <say-as interpret-as="characters">TOI</say-as> <say-as interpret-as="cardinal">150</say-as>
   - "TOI-1234" → <say-as interpret-as="characters">TOI</say-as> <say-as interpret-as="cardinal">1234</say-as>
2. Other acronyms:
   - "HST" → <say-as interpret-as="characters">HST</say-as>
   - "JWST" → <say-as interpret-as="characters">JWST</say-as>

Content Requirements (8-10 minutes, 1500-1800 words):
1. Show introduction with ExoDaily branding (15s)
2. Hook and show intro (45s)
3. Topic introduction (1m)
4. Main discussion with analogies (6-7m)
5. Brief conclusion (30s)

Conversation Style:
- Replace technical jargon with plain language
- Include natural reactions and questions
- Keep uninterrupted speech under 45 seconds
- Balance speaking time between hosts
- Use analogies for complex concepts

REMEMBER: Output ONLY the SSML script. Do not include any explanations, notes, or additional text.

Technical Abstract:
                {inputContent}"""
    payload = {
        'model': 'deepseek-chat',  # Specify the model
        'messages': [
        {'role': 'system', 'content': 'You are a podcast script writer specializing in SSML formatting.'},
        {'role': 'user', 'content': prompt}],
        'temperature': 1.0}
    nTry = 0
    while nTry < maxTry:
        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()  # Raise an error for bad status codes
            result = response.json()
            # Extract the assistant's reply from the response
            return result['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            print(f"Error summarizing abstract: {e}")
            print("Status Code:", response.status_code)
            print("Response:", response.text)
            nTry += 1            
            time.sleep(10)
    return None    

print("start summarizing")
summary = abstract_to_podcast_script(abstractList)

print("podcast script ready")
# save summary into a text file, file name include current date
with open(f'./script_output/podcast_conversation_{date}.txt', 'w') as f:
    f.write(summary)

""" summary_file = './script_output/podcast_script_2025-02-08.txt'
with open(summary_file, 'r') as f:
    summary = f.read() """

# convert the summary into speech
from text_to_speech import text_to_speech_long, combine_audio_files
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./continual-grin-440504-c8-136d2e328d2d.json"
segments = text_to_speech_long(summary, base_output_file=f'./voice_output/podcast_conversation_{date}', is_ssml=True)
combine_audio_files(segments, output_file=f'./voice_output/podcast_conversation_{date}_combined.mp3')


