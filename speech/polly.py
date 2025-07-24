import boto3
from utils import get_env_var


def use_polly(text, voice_id="Matthew"):
    print("Using Polly for text-to-speech")
    client=boto3.client('polly',aws_access_key_id=get_env_var("AMAZON_ACCESS_KEY"),aws_secret_access_key=get_env_var("AMAZON_SECRET_KEY"),region_name='ap-south-1')
    response = client.synthesize_speech(
        Engine='standard',
        LanguageCode='en-US',
        OutputFormat='mp3',
        Text=text,
        VoiceId=voice_id
        )
    return response['AudioStream'].read()

