from datetime import datetime

from pydub import AudioSegment
from speechkit import configure_credentials, creds, model_repository

configure_credentials(
   yandex_credentials=creds.YandexCredentials(
      api_key='SECRET'
   )
)

def date_by_words() -> str:
    """Current date by words, like '26 августа'"""
    
    date = datetime.now()

    ru_months_dic = {
        'Jan': 'января',
        'Feb': 'февраля',
        'Mar': 'марта',
        'Apr': 'апреля',
        'May': 'мая',
        'Jun': 'июня',
        'Jul': 'июля',
        'Aug': 'августа',
        'Sep': 'сентября',
        'Oct': 'октября',
        'Nov': 'ноября',
        'Dec': 'декабря',
    }

    return f'{date.day} {ru_months_dic[date.strftime("%b")]}'

def ms_to_timing(microseconds: int) -> str:
    """Convert microseconds to timing like '9:21'

    Args:
        microsec: number of microseconds

    Returns:
        String like '9:21'
    """
    
    min = microseconds // 60000
    sec = (microseconds - min * 60000) // 1000

    return f'{min}:{sec}' if sec >= 10 else f'{min}:0{sec}'

def audio_wrapper(sound: AudioSegment) -> AudioSegment:
    """Add start and end sounds, +2.5 and +5 seconds

    Args:
        sound: input audio

    Returns:
        sound in AudioSegment format
    """

    # Get start and end sound effects
    start = AudioSegment.from_file("start.wav", format="wav")
    end = AudioSegment.from_file("end.wav", format="wav")

    # Add silence to original audion
    new_sound = AudioSegment.silent(duration=2500) + sound + AudioSegment.silent(duration=5000)

    # Add effects
    return new_sound.overlay(end, position=len(new_sound) - 7000).overlay(start, position=0)

def main():

    # Get text from file
    with open('input.txt', 'r') as file:
        text = file.read()

    # Extract categories
    main = text[:text.find('-\nСофт-новости\n-')]
    soft = text[text.find('-\nСофт-новости\n-'):text.find('-\nХард-новости\n-')]
    hardpron = text[text.find('-\nХард-новости\n-'):text.find('-\nБизнес-новости\n-')]
    businnes = text[text.find('-\nБизнес-новости\n-'):]

    # Send Filipp to Yandex Speech Kit
    filipp = model_repository.synthesis_model()
    filipp.voice = 'filipp'
    audio_main = filipp.synthesize(main, raw_format=False)
    audio_soft = filipp.synthesize(soft, raw_format=False)
    audio_businnes = filipp.synthesize(businnes, raw_format=False)

    # Send Alena to Yandex Speech Kit
    alena = model_repository.synthesis_model()
    alena.voice = 'alena'
    audio_hardpron = alena.synthesize(hardpron, raw_format=False)

    # Combine and add sound effects
    silence = AudioSegment.silent(duration=500)
    result = audio_wrapper(audio_main + silence
                           + audio_soft + silence
                           + audio_hardpron + silence
                           + audio_businnes)

    # Generate filename
    filename = date_by_words()

    # Export
    result.export(f'{filename}.mp3',
                    format="mp3",
                    bitrate="192k",
                    tags={'artist': 'ntab', 'title': filename},
                    cover='artwork.jpg',
                    id3v2_version='3')

    # Calc timings
    soft_pos = ms_to_timing(2500 + len(audio_main))
    hard_pos = ms_to_timing(2500 + len(audio_main) + len(audio_soft))
    biz_pos = ms_to_timing(2500 + len(audio_main) + len(audio_soft) + len(audio_hardpron))
    
    print(f'{soft_pos} • Software\n\n{hard_pos} • Hardpron\n\n{biz_pos} • Business')


if __name__ == '__main__':
   main()