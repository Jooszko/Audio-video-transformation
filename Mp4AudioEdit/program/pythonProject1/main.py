import os
import subprocess
from pydub import AudioSegment, effects
import numpy as np
from scipy.io import wavfile


def extract_audio_from_video(video_path, audio_output_path):
    command = ['ffmpeg', '-y', '-i', video_path, '-q:a', '0', '-map', 'a', audio_output_path]
    subprocess.run(command, check=True)


def noise_reduction(audio_path, noise_sample_path, reduced_noise_path):
    audio = AudioSegment.from_file(audio_path)
    noise_sample = AudioSegment.from_file(noise_sample_path)

    audio_np = np.array(audio.get_array_of_samples())
    noise_np = np.array(noise_sample.get_array_of_samples())

    noise_mean = np.mean(noise_np)
    audio_np_reduced = audio_np - noise_mean

    reduced_audio = audio._spawn(audio_np_reduced.astype(np.int16).tobytes())
    reduced_audio.export(reduced_noise_path, format="wav")


def apply_gain(audio_path, output_path, gain_value=45):
    audio = AudioSegment.from_file(audio_path)
    audio = effects.normalize(audio) + gain_value
    audio.export(output_path, format="wav")


def trim_silence(audio_path, output_path):
    audio = AudioSegment.from_file(audio_path)
    trimmed_audio = effects.strip_silence(audio, silence_thresh=-50) # silence_thresh to change
    if len(trimmed_audio) > 0:
        trimmed_audio.export(output_path, format="wav")
        return True
    return False


def replace_audio_in_video(video_path, new_audio_path, output_video_path):
    command = ['ffmpeg', '-y', '-i', video_path, '-i', new_audio_path, '-c:v', 'copy', '-map', '0:v:0', '-map', '1:a:0',
               output_video_path]
    subprocess.run(command, check=True)


def create_output_path(video_path, output_base_folder):
    parts = video_path.split(os.sep)
    date_folder = parts[-2]
    date = f"{date_folder[:4]}_{date_folder[4:6]}_{date_folder[6:8]}"
    output_folder = os.path.join(output_base_folder, date)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    video_filename = parts[-1]
    hour = date_folder[8:10]
    minute = video_filename.split('M')[0][-2:]
    new_filename = f"{hour}h_{minute}m.mp4"

    return os.path.join(output_folder, new_filename)


def process_video(video_path, noise_sample_path, output_base_folder, gain_value=45):

    final_output_video_path = create_output_path(video_path, output_base_folder)

    if os.path.exists(final_output_video_path):
        print(f"Plik {final_output_video_path} już istnieje. Pomijanie przetwarzania.")
        return

    audio_output_path = 'extracted_audio.wav'
    reduced_noise_path = 'reduced_noise.wav'
    gain_applied_path = 'gain_applied.wav'
    trimmed_audio_path = 'trimmed_audio.wav'
    final_output_video_path = create_output_path(video_path, output_base_folder)

    extract_audio_from_video(video_path, audio_output_path)
    noise_reduction(audio_output_path, noise_sample_path, reduced_noise_path)
    apply_gain(reduced_noise_path, gain_applied_path, gain_value)

    if trim_silence(gain_applied_path, trimmed_audio_path):
        replace_audio_in_video(video_path, trimmed_audio_path, final_output_video_path)
    else:
        print(f"Pusty plik {video_path}. Skip.")


def process_videos_in_folder(input_folder, noise_sample_path, output_base_folder, gain_value=45):
    if not os.path.exists(output_base_folder):
        os.makedirs(output_base_folder)

    for root, dirs, files in os.walk(input_folder):

        for dir_name in dirs:
            date_folder = dir_name
            date = f"{date_folder[:4]}_{date_folder[4:6]}_{date_folder[6:8]}"
            output_folder = os.path.join(output_base_folder, date)

            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

        for filename in files:
            if filename.endswith('.mp4'):
                video_path = os.path.join(root, filename)
                process_video(video_path, noise_sample_path, output_base_folder, gain_value)

# edit your path:
input_folder = r"C:\path\to\your\folder"
output_base_folder = r'C:\finish\files\path'
noise_sample_path = r"..\..\probkaSzumu\probka.wav"
#gain to change
gain_value = 45

process_videos_in_folder(input_folder, noise_sample_path, output_base_folder, gain_value)

print("Przetworzono wszystkie pliki")