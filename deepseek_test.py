import requests
import time

# Replace with your DeepSeek API key
API_KEY = 'sk-f1248158294f486ca8c94d6a77e3421b'

# DeepSeek API endpoint for chat completions
API_URL = 'https://api.deepseek.com/chat/completions'

# Headers for the API request
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

# Example arXiv paper data (replace with your actual data)
papers = [
    {
        'title': 'A Novel Approach to Quantum Computing',
        'author': 'John Doe',
        'abstract': 'Quantum computing is a rapidly advancing field that promises to revolutionize computation by leveraging quantum mechanics.'
    },
    {
        'title': 'Advances in Deep Learning for Natural Language Processing',
        'author': 'Jane Smith',
        'abstract': 'Deep learning has revolutionized natural language processing, enabling machines to understand and generate human language with unprecedented accuracy.'
    },
    # Add more papers here
]

def summarize_abstract(abstract):
    """
    Sends the abstract to the DeepSeek API for summarization with a jokingly uplifting tone.
    """
    # Define the payload with the correct structure
    payload = {
        'model': 'deepseek-chat',  # Specify the model
        'messages': [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': f'Summarize this abstract in a lighthearted, uplifting tone: {abstract}'}
        ]
    }

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
        return None

def combine_summaries(papers):
    """
    Combines summaries of multiple abstracts into a single structured output.
    """
    combined_output = "Good morning! ☕ Here's your daily dose of science with a smile:\n\n"

    for paper in papers:
        title = paper['title']
        author = paper['author']
        abstract = paper['abstract']

        # Summarize the abstract with a jokingly uplifting tone
        summary = summarize_abstract(abstract)
        if summary:
            combined_output += f"**Title**: {title}\n"
            combined_output += f"**Author**: {author}\n"
            combined_output += f"**Summary**: {summary}\n\n"
        else:
            combined_output += f"**Title**: {title}\n"
            combined_output += f"**Author**: {author}\n"
            combined_output += "**Summary**: Oops, something went wrong. Maybe it's the coffee? ☕\n\n"

        # Add a delay to avoid hitting rate limits (if applicable)
        time.sleep(1)

    return combined_output

# Generate the combined output
combined_output = combine_summaries(papers)

# Print or save the combined output
print(combined_output)

# Optionally, save the output to a file
with open('morning_coffee_summaries.txt', 'w') as f:
    f.write(combined_output)