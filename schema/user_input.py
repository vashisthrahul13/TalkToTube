from pydantic import BaseModel,Field,computed_field,field_validator
from typing import Annotated
import re


class UserInput(BaseModel):

    question : Annotated[str,Field(...,description='The question asked by the user',example ='What is the topic of this video')]
    video_url : Annotated[str,Field(...,description='Url of the video',example = 'https://www.youtube.com/watch?v=LPZh9BOjkQs')]

    @field_validator('video_url')
    @classmethod
    def validate_url(cls,url):
        YOUTUBE_REGEX = re.compile(r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$')
        if not YOUTUBE_REGEX.match(url):
            raise ValueError('Not a valid youtube url')
        
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