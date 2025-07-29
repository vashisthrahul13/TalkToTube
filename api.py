import sys
import os

# Add the current working directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__))) 
#adds the current file folder allowing us to import files from the same folder (ex .env)

from schema.user_input import UserInput #import the pydantic base class for user input validation

from model.rag import rag,MODEL_VERSION

from fastapi import FastAPI,HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv


load_dotenv(os.path.join(os.path.dirname(__file__),'..','.env'))


app = FastAPI()

# to allow chrome plugin to call out fastapi
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or explicitly set your extension origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#home page
@app.get('/')
def home():
    return JSONResponse(content={'message':'TalktoTube API'})


#add health check for AWS and Kuberneties check
@app.get('/health')
def health_check():
    return {
        'status':'OK',
        'version':MODEL_VERSION,
    }


#add query endpoint
@app.post('/ask')
def ask(user_query : UserInput):

#fetch the video transcript
    ytt_api = YouTubeTranscriptApi()
    try:
        transcript_list = ytt_api.fetch(video_id=user_query.video_id,languages=['en'])
        #merge the list into a single text
    except:
        raise HTTPException(status_code=500,detail='Unable to process video due to lack of english captions')
    
    #call rag to generate prompt
    question = user_query.question
    rag(transcript_list,question)


    try:
        timestamp_context,llm_response = rag(transcript_list,question)
    except Exception as e:
        raise HTTPException(status_code=404,detail = str(e))

    return JSONResponse(status_code=200, content={'answer': llm_response,
                                                  'timestamp':timestamp_context})
    