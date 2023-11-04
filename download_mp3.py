import asyncio
from pytube import YouTube, Search

YOUTUBE_VIDEO_BASE_URL = 'https://www.youtube.com/watch?v='

async def download_song(song):
    s = Search(f'{song} audio')
    search_result = s.results[0]
    video_id = search_result.video_id

    yt = YouTube(YOUTUBE_VIDEO_BASE_URL + video_id)
    # itag = yt.streams.filter(adaptive=True)[0].itag
    # stream = yt.streams.get_by_itag(itag=itag)
    # stream.download()
    
    audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()
    output_path = 'C:\\Spotify-OAuth-App'
    file_name = f'{song}.mp3'
    audio_stream.download(output_path=output_path, filename=file_name)