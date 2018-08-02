import subprocess
import settings
from datetime import datetime
from datetime import timedelta

# /!\ Before launching this script, you must have resized the speaker video to this ratio : 202*360
# and rename it "video_speaker_resized", otherwise the speaker video will be distorded in the mounted video

def init():
    global PREPARE_VIDEOS, MOUNT_VIDEOS
    global start_video_speaker, stop_videos, synchro_speaker, synchro_slides, folder_path
    global speaker_path, slides_path, speaker_final_path, slides_final_path, video_to_mute, formation_path

    PREPARE_VIDEOS = True
    MOUNT_VIDEOS = True

    # To adapt to your videos

    start_video_speaker = "00:00:10.000000"
    stop_videos = "00:25:23.000000" #00:25:33 - 00:00:10 = 00:25:23

    synchro_speaker = "00:00:09.000000" 
    synchro_slides = "00:00:21.000000" 

    folder_path = "../" + "Name of the folder of the formation" + "/"

    speaker_format = ".mp4"
    slides_format = ".mov"
    video_to_mute = "speaker" # speaker or slides

    # Do not change
    speaker_path = folder_path + "video_speaker_resized" + speaker_format
    slides_path = folder_path + "video_slides" + slides_format
    speaker_final_path = folder_path + "video_speaker_cut" + speaker_format
    slides_final_path = folder_path + "video_slides_cut" + slides_format
    formation_path = folder_path + "formation.mp4"

def calculate_start_video_slides(synchro_speaker, synchro_slides):
  FMT = '%H:%M:%S.%f'
  
  # Calcul temps à enlever au début des slides
  tdelta = datetime.strptime(synchro_slides, FMT) - datetime.strptime(synchro_speaker, FMT)
  thour, tminute, tsec = str(tdelta).split(":")
  tsec, tmsec = str(tsec).split(".")

  # if synchro_slides < synchro_speaker
  if thour[0] == '-':
    tdelta = datetime.strptime(synchro_speaker, FMT) - datetime.strptime(synchro_slides, FMT)
    thour, tminute, tsec = str(tdelta).split(":")
    tsec, tmsec = str(tsec).split(".")

    start_time_slides = datetime.strptime(start_video_speaker, FMT) - timedelta(minutes=float(tminute), seconds=float(tsec), microseconds=float(tmsec))
  else:
    start_time_slides = datetime.strptime(start_video_speaker, FMT) + timedelta(minutes=float(tminute), seconds=float(tsec), microseconds=float(tmsec))
    
  # Remove date
  start_time_slides_split = str(start_time_slides).split(" ")
  if len(start_time_slides_split) > 1:
    start_time_slides = start_time_slides_split[len(start_time_slides_split)-1]

  # Reformat time
  thour, tminute, tsec = str(start_time_slides).split(":")
  # TODO : Add try to find if there is "." in tsec
  tsec, tmsec = str(tsec).split(".")
  if len(thour) == 1:
    thour = "0" + thour
  elif len(thour) == 0:
    thour = "00" 

  # Return start time video slides  
  print(thour + ":" + tminute + ":" + tsec + "." + tmsec)
  return thour + ":" + tminute + ":" + tsec + "." + tmsec

def call_commands(command):
  subprocess.call(command)

def main():
  init()
  
  start_video_slides = calculate_start_video_slides(synchro_speaker, synchro_slides)
  
  if PREPARE_VIDEOS:
    # Cut videos
    command_speaker = ['ffmpeg', '-ss', start_video_speaker, '-i', speaker_path, '-t', stop_videos, '-vcodec', 'copy']
    command_slides = ['ffmpeg', '-ss', start_video_slides, '-i', slides_path, '-t', stop_videos, '-vcodec', 'copy']

    if video_to_mute == "speaker":
      command_speaker.extend(('-an', speaker_final_path))
      command_slides.extend(('-acodec', 'copy', slides_final_path))
    elif video_to_mute == "slides":
      command_speaker.extend(('-acodec', 'copy', speaker_final_path))
      command_slides.extend(('-an', slides_final_path))

    confirmation_to_continue = input('Press enter to cut speaker video')
    call_commands(command_speaker)
    confirmation_to_continue = input('Press enter to cut slides video')
    call_commands(command_slides)


  # Mount videos
  if MOUNT_VIDEOS:
    confirmation_to_continue = input('Press enter to mount video')
    command_formation = ['ffmpeg', '-i', slides_final_path, '-i', speaker_final_path, '-filter_complex', 'color=s=1920x1080:c=black [base]; [0:v] scale=1410x880 [slides]; [1:v] scale=495x880 [speaker]; [base][slides] overlay=shortest=1:x=0:y=100 [tmp1]; [tmp1][speaker] overlay= shortest=1:x=1425:y=100', '-profile:v', 'main', '-level', '3.1', '-b:v', '2000k', '-ar', '44100', '-ab', '128k', '-s', '1920x1080', '-vcodec', 'h264', formation_path]
    call_commands(command_formation)

if __name__ == "__main__":
  print("Process started.")
  main()
  print("Process finished !")
