import streamlit as st
from youtubesearchpython import VideosSearch
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import google.generativeai as genai
st.image("srisri.jpeg",use_column_width=True)

GOOGLE_API_KEY="AIzaSyAimoYBCAPRKN773YUqBwokefkbt0x7Mps"
genai.configure(api_key=GOOGLE_API_KEY)
model=genai.GenerativeModel("gemini-pro")
prompt="""You are an experienced spiritual seeker and a devoted follower of Gurudev Sri Sri Ravi Shankar. Summarize the following content and provide suggestions based on the context without deviating from the given information. Write a reply, ensuring that the reply begins with "Jai Gurudev." Incorporate Gurudev's teachings and wisdom into your response, starting with the phrase "As Gurudev always says..." If the content is not that good, say no"
"""
prompt="""You are an experineced spritual seeker and a devotee of Gurudev Sri Sri ravi shankar , summarize the follwing content and give suggestions as per conetxt and write a reply to the person only if you get something out of the context and it resonates with the question provided your reply should start with "Jai gurudev , as gurudev mentions"  , and if the context is not provided or does not resonates with the question reply by saying "I guess I dont have answer to this sorry" 
context: {title}
question: {question}
"""
prompt2= """You are a youtube video filter. If you find that a particular video matches the context of the  prompt given and there is mention of Gurudev Sri Sri Ravi Shankar and is not a meditation,  respond with "GO" or else respond with "stop". As output, we only need either "GO" or "stop". 
title: {title}
prompt: {prompt}
"""
def get_gemini_response(input,pdf_content,prompt):
    prompt_filled = input.format(title=prompt,question=pdf_content)
    response=model.generate_content([prompt_filled])
    return response.text
def get_link(prompt_template, title, context):
    prompt_filled = prompt_template.format(title=title, prompt=context)
    response = model.generate_content([prompt_filled])
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
  

import re

def get_transcripts_for_terms(terms,context,prompt, max_transcripts=5):
    """
    Searches YouTube for videos containing any of the provided terms and extracts their transcripts.

    Args:
        terms: A list of strings representing the search terms.
        max_transcripts: Maximum number of transcripts to retrieve.

    Returns:
        A list of transcripts for the search results.
    """
    search_results = search_multiple_terms(terms)  # Make sure this function is defined elsewhere

    transcripts = []
    title=[]
     
    for result in search_results:
        title = result["title"]
        url = result["link"]
        
       
        response=get_link(prompt,context,title)
    
        # Use regex to check if "Gurudev" is in the title, case insensitive
        if response == "GO" :
            transcript = extract_transcript_details(url)  # Make sure this function is defined elsewhere
            if transcript:
                transcripts.append(transcript)
            
            # Stop if we have collected enough transcripts
            if len(transcripts) >= max_transcripts:
                break
        else:
            st.write("Skipping video as it does not match criteria")

    return transcripts


# Streamlit interface
st.title("Shishya Bot")

# Optionally, you can add a subtitle in a similar manner
st.subheader("Carry the knowledge wherever you go")
import time
prompt1 = st.chat_input("Ask me a question")
st.write(prompt1)
st.write("__________________________________________")
transcripts = []

if prompt1:
    search_terms = ["gurudev", "sri sri ravi shankar", prompt1]
    transcripts = get_transcripts_for_terms(search_terms)

    # Print video titles and links
    

    start=time.process_time()



    response=get_gemini_response(prompt,prompt1,str(transcripts))
    message = st.chat_message("assistant")
    message.write((response))

