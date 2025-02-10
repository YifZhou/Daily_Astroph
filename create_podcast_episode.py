from pydub import AudioSegment
from pydub.effects import normalize
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB
from datetime import datetime
import random
now = datetime.now()
date = now.strftime("%Y-%m-%d")

def add_cover_art(mp3_path, image_path):
    """
    Add cover art to MP3 file
    
    Parameters:
    - mp3_path: Path to the MP3 file
    - image_path: Path to the image file (jpg/png)
    """
    try:
        # Load the MP3 file
        audio = MP3(mp3_path, ID3=ID3)
        
        # Create ID3 tag if it doesn't exist
        if audio.tags is None:
            audio.add_tags()
            
        # Read the image file
        with open(image_path, 'rb') as img_file:
            img_data = img_file.read()
        
        # Add the cover art
        audio.tags.add(
            APIC(
                encoding=3,  # UTF-8
                mime='image/jpeg' if image_path.endswith('jpg') else 'image/png',
                type=3,  # Cover image
                desc='Cover',
                data=img_data
            )
        )
        
        # Add basic metadata
        audio.tags.add(TIT2(encoding=3, text="ExoDaily"))
        audio.tags.add(TPE1(encoding=3, text="ExoDaily Podcast"))
        audio.tags.add(TALB(encoding=3, text="Daily Exoplanet Digest"))
        
        # Save the changes
        audio.save()
        print("Successfully added cover art")
        
    except Exception as e:
        print(f"Error adding cover art: {e}")


def create_episode_with_dynamic_music(
    main_audio_path,
    music_path,
    output_path="final_episode.mp3",
    intro_music_volume=-15,  # Slightly louder for intro
    background_music_volume=-35,  # Quieter during speech
    crossfade_duration=5000  # 3 seconds crossfade
):
    """
    Add background music with dynamic volume levels
    """
    try:
        # Load audio files
        main_audio = AudioSegment.from_mp3(main_audio_path)
        music = AudioSegment.from_mp3(music_path)
        
        # Create intro music segment (first 5 seconds louder)
        intro_duration = 10000  # 10 seconds
        intro_music = music[:intro_duration] + intro_music_volume
        
        # Create background music for the rest
        background_music = music[intro_duration:] + background_music_volume
        
        # Loop if needed
        while len(background_music) < len(main_audio) - intro_duration:
            background_music = background_music + (music + background_music_volume)

        # Create crossfade between intro and background
        intro_music = intro_music.fade_out(crossfade_duration)
        background_music = background_music.fade_in(crossfade_duration)
        
        # Overlap intro and background by crossfade duration
        overlap_position = len(intro_music) - crossfade_duration
        full_music = intro_music + background_music
        
        # Add overall fade in/out
        full_music = full_music.fade_in(2000).fade_out(3000)
            
        
        # Overlay with main audio
        final_audio = main_audio.overlay(full_music)
        
        # Export
        final_audio.export(
            output_path,
            format="mp3",
            bitrate="192k",
            tags={
                "album": "ExoDaily",
                "title": "Daily Exoplanet Digest"
            }
        )
        
        # Add cover art
        cover_art_path = "./coverart.jpg"
        add_cover_art(output_path, cover_art_path)
        print(f"Successfully exported to {output_path}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        main_audio_path = sys.argv[1]
    else:
        import os
        # get the latest podcast script
        files = os.listdir('./voice_output')
        files.sort()
        latest_file = files[-1]
        main_audio_path = f'./voice_output/{latest_file}'
    music_path = './music/Top Of The Morning - TrackTribe.mp3'
    print(music_path)
    create_episode_with_dynamic_music(
        main_audio_path=main_audio_path,
        music_path=music_path,
        output_path=f"./podcast_output/episode_{date}.mp3"
    )