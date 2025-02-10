# First, install the required package:
# pip install google-cloud-texttospeech

from google.cloud import texttospeech
import os

def text_to_speech(text, output_file="output.mp3", 
                   language_code="en-US", 
                   voice_name="en-US-Standard-A",
                   is_ssml=True):
    """
    Convert text to speech using Google Cloud TTS API
    
    Args:
        text (str): Text to convert to speech
        output_file (str): Output audio file path
        language_code (str): Language code (e.g., "en-US", "es-ES", "fr-FR")
        voice_name (str): Name of the voice to use
        is_ssml (bool): Whether the input text is SSML
    """
    # Initialize the client
    client = texttospeech.TextToSpeechClient()

    # Set the input text
    if is_ssml:
        synthesis_input = texttospeech.SynthesisInput(ssml=text)
    else:
        synthesis_input = texttospeech.SynthesisInput(text=text)

    # Configure voice parameters
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name
    )

    # Select the audio encoding
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.0,
    )

    # Perform the text-to-speech request
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    # Write the response to the output file
    with open(output_file, "wb") as out:
        out.write(response.audio_content)
    
    print(f"Audio content written to '{output_file}'")

def split_ssml_script(ssml_text, max_chars=4800):
    """
    Split SSML script into smaller chunks while preserving SSML tags and conversation structure.
    """
    # Remove outer <speak> tags for processing
    content = ssml_text.replace('<speak>', '').replace('</speak>', '').strip()
    
    # Split into voice segments
    segments = []
    current_chunk = '<speak>'
    current_length = 0
    
    # Split by voice blocks
    voice_blocks = content.split('</voice>')
    
    for block in voice_blocks:
        if not block.strip():
            continue
            
        # Add closing voice tag back
        block = block + '</voice>'
        
        # If adding this block would exceed limit, save current chunk and start new one
        if current_length + len(block) > max_chars and current_length > 0:
            current_chunk += '</speak>'
            segments.append(current_chunk)
            current_chunk = '<speak>'
            current_length = 0
        
        current_chunk += block
        current_length += len(block)
    
    # Add the last chunk if it's not empty
    if current_length > 0:
        current_chunk += '</speak>'
        segments.append(current_chunk)
    
    return segments

def split_text_into_segments(text: str, max_length: int = 4800) -> list[str]:
    """
    Split text into segments using empty lines as natural break points.
    Each segment will be no longer than max_length characters.
    
    Args:
        text (str): The input text to be split
        max_length (int): Maximum length for each segment (default: 4800)
        
    Returns:
        list[str]: List of text segments
    """
    # Split the text into paragraphs using empty lines
    paragraphs = [p.strip() for p in text.split('\n\n')]
    
    segments = []
    current_segment = ''
    
    for paragraph in paragraphs:
        # Check if adding this paragraph would exceed the limit
        potential_segment = f"{current_segment}\n\n{paragraph}" if current_segment else paragraph
        
        if len(potential_segment) > max_length and current_segment:
            # Store current segment and start a new one
            segments.append(current_segment.strip())
            current_segment = paragraph
        else:
            current_segment = potential_segment
    
    # Add the last segment if it's not empty
    if current_segment:
        segments.append(current_segment.strip())
    
    # Validate segments and split long paragraphs if necessary
    validated_segments = []
    
    for segment in segments:
        if len(segment) > max_length:
            # If a segment is too long, split by sentences
            sentences = split_into_sentences(segment)
            current_part = ''
            
            for sentence in sentences:
                potential_part = f"{current_part} {sentence}" if current_part else sentence
                
                if len(potential_part) > max_length and current_part:
                    validated_segments.append(current_part.strip())
                    current_part = sentence
                else:
                    current_part = potential_part
            
            if current_part:
                validated_segments.append(current_part.strip())
        else:
            validated_segments.append(segment)
    
    return validated_segments

def split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences, handling common abbreviations and edge cases.
    
    Args:
        text (str): Text to split into sentences
        
    Returns:
        list[str]: List of sentences
    """
    import re
    
    # Common abbreviations to avoid splitting on
    abbreviations = r'Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.|Sr\.|Jr\.|etc\.|vs\.|e\.g\.|i\.e\.'
    
    # Split on period-space-capital letter pattern, but not after abbreviations
    sentence_endings = r'(?<!{})\. +(?=[A-Z])'.format(abbreviations[:-1])
    
    # Also split on ! and ? followed by space and capital letter
    sentences = re.split(f'{sentence_endings}|[!?] +(?=[A-Z])', text)
    
    # Clean up sentences
    return [s.strip() for s in sentences if s.strip()]

def text_to_speech_long(ssml_text, 
                        base_output_file="podcast", 
                        language_code="en-US", 
                        voice_name="en-US-Standard-A",
                        is_ssml=True):
    """
    Handle long SSML text by splitting it into chunks and processing each separately.
    """
    # Split the SSML into manageable chunks
    if is_ssml:
        chunks = split_ssml_script(ssml_text)
    else:
        chunks = split_text_into_segments(ssml_text)
    audio_segments = []
    
    # Process each chunk
    for i, chunk in enumerate(chunks):
        output_file = f"{base_output_file}_part{i+1:02d}.mp3"
        try:
            # Convert chunk to speech
            print(f"Processing chunk {i+1}/{len(chunks)}...")
            text_to_speech(chunk, output_file, language_code, voice_name=voice_name, is_ssml=is_ssml)
            audio_segments.append(output_file)
            print(f"Processed chunk {i+1}/{len(chunks)}")
        except Exception as e:
            print(f"Error processing chunk {i+1}: {e}")
            continue
    
    return audio_segments

def combine_audio_files(audio_files, output_file="final_podcast.mp3"):
    """
    Combine multiple MP3 files into one.
    Requires pydub: pip install pydub
    """
    try:
        from pydub import AudioSegment
        
        combined = AudioSegment.empty()
        for audio_file in audio_files:
            segment = AudioSegment.from_mp3(audio_file)
            combined += segment
            
        combined.export(output_file, format="mp3")
        print(f"Combined audio saved to {output_file}")
        
        # Optionally cleanup individual files
        for file in audio_files:
            os.remove(file)
            
    except ImportError:
        print("Please install pydub to combine audio files: pip install pydub")
        return None

# Example usage
if __name__ == "__main__":
    # Set your Google Cloud credentials
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./continual-grin-440504-c8-136d2e328d2d.json"
    
    # Convert text to speech
    sample_text = """<speak>
<voice name="en-US-Neural2-D">Welcome to Cosmic Conversations! I'm Alex, uh... here with my co-host Sarah to break down this week's space discoveries.</voice>

<voice name="en-US-Neural2-F">And what a week it's been! <break time="400ms"/> Let's start with... Europa - there's some fascinating chemistry happening on that icy moon.</voice>

<voice name="en-US-Neural2-D">Mm-hmm! Scientists found that when electrons hit organic molecules on Europa's surface - especially those with, um, carboxylic acid groups - they produce huge amounts of CO2. <break time="300ms"/> Pretty much explains those mysterious signatures we've been seeing.</voice>

<voice name="en-US-Neural2-F">It's incredible how these processes on a distant moon might... you know... be connected to potential biosignatures! <break time="500ms"/> Oh! And have you been following that Kuiper Belt research?</voice>

<voice name="en-US-Neural2-D"><emphasis>Yes!</emphasis> <break time="200ms"/> The pebble accretion study is just... wow. We're basically watching how dwarf planets form through these tiny rocks coming together.</voice>

<voice name="en-US-Neural2-F">And then there's TOI-150b - I mean... talk about extreme weather! <break time="300ms"/> Those eccentric hot Jupiters with their wild orbits create some... pretty intense atmospheric conditions.</voice>

<voice name="en-US-Neural2-D">The jet streams they're seeing are just... incredible. <break time="200ms"/> It's like Earth's weather patterns gone completely crazy!</voice>

<voice name="en-US-Neural2-F">Space never stops surprising us, does it? <break time="400ms"/> What's your bet on the next big discovery?</voice>

<voice name="en-US-Neural2-D">Well... with these new observations coming in daily, who knows? But that's what makes this field so exciting!</voice>
</speak>"""
    output_file = "voice_output/output.mp3"
    text_to_speech(sample_text, output_file=output_file)