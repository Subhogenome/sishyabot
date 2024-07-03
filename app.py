import streamlit as st
from youtubesearchpython import VideosSearch
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import google.generativeai as genai

st.image("srisri.jpeg",use_column_width=True,)
GOOGLE_API_KEY=st.secret["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
model=genai.GenerativeModel("gemini-pro")
prompt=st.secret["prompt"]
def get_gemini_response(input,pdf_content,prompt):
    response=model.generate_content([input+pdf_content+prompt])
    return response.text
def search_multiple_terms(terms):
    """
    Searches YouTube for videos containing any of the provided terms.

    Args:
        terms: A list of strings representing the search terms.

    Returns:
        A list of dictionaries containing information about the search results.
    """
    combined_query = " | ".join(terms)
    results = VideosSearch(query=combined_query, limit=10)
    return results.result()["result"]

def extract_transcript_details(url):
    """
    Extracts the transcript from a YouTube video URL.

    Args:
        url: The URL of the YouTube video.

    Returns:
        The transcript text of the video, or None if transcript retrieval failed.
    """
    try:
        video_id = url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]
        return transcript
    except TranscriptsDisabled:
        # Handle case where transcripts are disabled
        return None
    except :
        # Handle case where no transcript is found
        return None


def get_transcripts_for_terms(terms, max_transcripts=5):
    """
    Searches YouTube for videos containing any of the provided terms and extracts their transcripts.

    Args:
        terms: A list of strings representing the search terms.
        max_transcripts: Maximum number of transcripts to retrieve.

    Returns:
        A list of transcripts for the search results.
    """
    search_results = search_multiple_terms(terms)
    transcripts = []

    for result in search_results:
        title = result["title"].lower()
        url = result["link"]
        
        # Skip videos related to meditation
        if "meditation" in title:
            continue

        transcript = extract_transcript_details(url)
        if transcript:
            transcripts.append(transcript)
        
        # Stop if we have collected enough transcripts
        if len(transcripts) >= max_transcripts:
            break

    return transcripts

# Streamlit interface
st.title("Shishya Bot")

# Optionally, you can add a subtitle in a similar manner
st.subheader("Carry the knowledge wherever you go")
import time
prompt1 = st.chat_input("Ask me a question")
transcripts = []

if prompt1:
    search_terms = ["gurudev", "sri sri ravi shankar", prompt1]
    transcripts = get_transcripts_for_terms(search_terms)

    # Print video titles and links
    

    start=time.process_time()



    response=get_gemini_response(prompt,str(transcripts),prompt1)
    message = st.chat_message("assistant")
    message.write((response))

