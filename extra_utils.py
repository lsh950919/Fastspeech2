import os
import io
import re
import argparse
import hparams as hp

from glob import glob
from tqdm import tqdm
from utils import resample
from pydub import AudioSegment
from google.cloud import speech
from moviepy.editor import VideoFileClip
from pydub.silence import split_on_silence


# Extract audio from a video
def vid_to_audio(vid_path):
    out_path = os.path.join(os.path.dirname(vid_path), 'audio.wav')
    clip = VideoFileClip(vid_path)
    clip.audio.write_audiofile(out_path, 22050)

# Split long audio file into parts
def split_audio(audio_path, out_dir):
    os.makedirs(out_dir, exist_ok = True)
    
    ext = audio_path.split('.')[-1]
    audio = AudioSegment.from_file(audio_path, ext)

    # split on silences in audio
    chunks = split_on_silence(audio, min_silence_len = 700, silence_thresh=-36) # adjust parameters according to the result of the split
    
    # filter audio files that are too short
    chunks2 = [chunk for chunk in chunks if len(chunk) > 2000]
    print(len(chunks2))

    # save each audio file
    print('Saving audio chunks...\n')
    for i, chunk in tqdm(enumerate(chunks2)):
        chunk.export("{}/chunk{}.wav".format(out_dir, i), format="wav")

# Google STT API for creating transcript to audio files without script
# Requires google service account key (json file, download from Google Cloud Platform)
def transcribe(audio_path, key):
    client = speech.SpeechClient.from_service_account_json(key)
    config = speech.RecognitionConfig(encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16, 
                                      sample_rate_hertz = 22050, language_code = 'ko-KR')

    with io.open(audio_path, 'rb') as audio_file:
        content = audio_file.read()
        audio = speech.RecognitionAudio(content = content)
    response = client.recognize(config = config, audio = audio)
    
    if response.results == []:
        return response.results
    return response.results[0].alternatives[0].transcript

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v',
                        '--video',
                        type = str,
                        default = None,
                        help = 'path to video file to extract audio from')
    parser.add_argument('-s',
                        '--long_audio',
                        type = str,
                        default = None,
                        help = 'path to audio file to split into pieces')    
    parser.add_argument('-k',
                        '--key',
                        type = str,
                        default = None,
                        help = 'path to service account key (json file)')
    args = parser.parse_args()

    if args.video:
        vid_to_audio(args.video)

    if args.long_audio:
        out_dir = hp.audio_path
        print('Splitting Audio...\n')
        split_audio(args.long_audio, out_dir)

    if args.key:
        audio_dir = hp.audio_path
        resample()

        file_list = glob(os.path.join(audio_dir, '*.wav'))
        assert len(file_list) != 0, 'Could not find any audio file, check directory or wav extension'

        meta = open(os.path.join(audio_dir, '../', 'metadata.txt'), 'w')
        print('Creating metadata...\n')
        for path in tqdm(file_list):
            transcribed = transcribe(path, args.key)
            # if result contains characters other than korean, space, or .,?! then skip the audio file
            if transcribed == [] or transcribed == '오디오 인터페이스' or re.search('[^가-힣0-9.?!, ]', transcribed) is not None:
                print(transcribed)
                continue
            meta.write(f'{os.path.basename(path)}|{transcribed}\n')
        meta.close()


