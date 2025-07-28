from pydantic import BaseModel,HttpUrl,Field,field_validator,computed_field
from typing import Annotated
import re

from fastapi import FastAPI,HTTPException,Path
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from youtube_transcript_api import YouTubeTranscriptApi

from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings,ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate

from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__),'..','.env'))

class UserInput(BaseModel):

    question : Annotated[str,Field(...,description='The question asked by the user',example ='What is the topic of this video')]
    video_url : Annotated[str,Field(...,description='Url of the video',example = 'https://www.youtube.com/watch?v=LPZh9BOjkQs')]

    @field_validator('video_url')
    @classmethod
    def validate_url(cls,url):
        YOUTUBE_REGEX = re.compile(r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$')
        if not YOUTUBE_REGEX.match(url):
            raise HTTPException(status_code=400,detail='Bad Request.Not a valid youtube url')
        
        return url
    
    @computed_field()
    @property
    def video_id(self) -> str:
        match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})(?:&|$)', self.video_url)
        if match:
            video_id = match.group(1)
            return video_id
        else:
            raise ValueError('No valid YouTube video ID found in the URL')


###############building fastapi
app = FastAPI()

# to allow chrome plugin to call out fastapi
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or explicitly set your extension origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/ask')
def rag(user_query : UserInput):

    #fetching video transcript
    video_id = user_query.video_id	#only id not the full url
    print('################## Video id is ################ : ',video_id)

    #fetch the video transcript
    ytt_api = YouTubeTranscriptApi()
    try:
        transcript_list = ytt_api.fetch(video_id=video_id,languages=['en'])
        #merge the list into a single text
        transcript = " ".join(snippet.text for snippet in transcript_list)
    except:
        raise HTTPException(status_code=500,detail='Unable to process video due to lack of english captions')

    ####1.Indexing
    #Building vector database
    splitter = RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap = 100)
    chunks = splitter.create_documents(texts=[transcript])

    #creating vector store
    embedding_model = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(
        documents=chunks,
        embedding=embedding_model
    )

    ####2.Retrieval
    retriever = vector_store.as_retriever(
        search_type = 'mmr',
        search_kwargs = {
            'fetch_k':10,
            'k':4,
            'lambda_multi':0.5}
    )

    question = user_query.question

    retrieved_docs = retriever.invoke(input=question)
    final_context = "\n\n".join(doc.page_content for doc in retrieved_docs)

    print('################## Final context being sent ################')
    print(final_context)    ####
    ####3.Augumentation
    #3.1 Build Prompt
    prompt = PromptTemplate(
        template="""
        You are a helpful assistant.
        Answer ONLY from the provided transcript context.
        If the context is insufficient, just say you don't know.

        {context}
        Question: {question}
        """,
        input_variables = ['context', 'question']
    )

    final_prompt = prompt.invoke(input={
        'context':final_context,
        'question':question})

    print('################## Final prompt being sent ################',final_prompt)
    ####4.Generation
    try:
        llm = ChatOpenAI(model='gpt-4.1-mini-2025-04-14')

        response = llm.invoke(final_prompt)
    except Exception as e:
        raise HTTPException(status_code=404,detail = str(e))
    
    return JSONResponse(status_code=200, content={'answer': response.content})