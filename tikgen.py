import os, random
from moviepy.editor import *

newfiles = [] #define newfiles
files = os.listdir() #create a list of every file in directory
for x in files:
    x = str(x.replace(".mp4", "")) # get rid of file extension
    newfiles.append(x) #create a new list without extensions
newfiles = [s for s in newfiles if s.isdigit()] #remove non-numbers from the list
newfiles.sort(key=int) #sort by number
amtfiles = len(newfiles)

bgselection = input("Would you like to select a folder or file for the background clip?: ")
if bgselection == "folder" or bgselection.lower() == "folder":
    folder = 1
    bgfolder = input("Folder name(must be in directory): ")
    bgvid = bgfolder + "/" + str(random.choice(os.listdir(bgfolder)))
elif bgselection == "file" or bgselection.lower() == "file":
    folder = 0
    bgvid = input("\nFilename of background clip? Include extension, use 9:16 aspect ratio: ")
else:
    print("Invalid input! Quitting...")
    quit()

bgv = VideoFileClip(bgvid)
if bgv.duration < VideoFileClip(newfiles[0] + ".mp4").duration: # if the background vid is shorter than the clip duration
    duration = float(VideoFileClip(newfiles[0] + ".mp4").duration) / 60 # turn video duration into minutes 
    bgduration = float(bgv.duration) / 60 # turn background duration into minutes
    askduration = input(f"\nIt looks like your videos are {duration} minutes long, but your background video is only {bgduration} minutes long. Continue? Y/N: ")
    if askduration == "n" or askduration == "N":
        quit()
    #basically if the background video is too short it'll ask if you want to continue

if folder == 0:
    bgnosnd = bgv.without_audio()
    bgnomp4 = bgvid.replace(".mp4", "")

if folder == 0:
    if os.path.exists(f"{bgnomp4}nosound.mp4"): #if the no sound version already exists
        print(f"\n\"{bgnomp4}nosound.mp4\" already exists, skipping audio removal")
        pass
    else:
        removeaudio = input(f"Remove audio from {bgnomp4}.mp4? y/n: ")
        if removeaudio == "y" or removeaudio == "Y":
            print(f"\nRemoving audio from the background video!")
            bgnosnd.write_videofile(f"{bgnomp4}nosound.mp4") #writes a new file as ___nosound.mp4
            bgnosnd = VideoFileClip(f"{bgnomp4}nosound.mp4") #redefines bgnosnd as the video without sound
        else:
            bgnosnd = VideoFileClip(f"{bgnomp4}.mp4")

if folder == 1:
    removeaudio = input(f"Remove audio from files in {bgfolder}? y/n: ")

# if os.path.exists(f"{bgnomp4}cropped.mp4"): #if the no sound version already exists
#     print(f"\n\"{bgnomp4}cropped.mp4\" already exists, skipping video cropping removal")
#     pass
# else:
#     if bgnosnd.size[0] / bgnosnd.size[1] != 9/16 :
#         not916 = input("\nYour video file does not match the aspect ratio! Crop it?(Only use this if your video is 16:9) y/n: ")
#         if not916 == "n" or not916 == "N":
#             pass
#         else:
#             if bgnosnd.size != [1920, 1080]:
#                 bgnosnd = bgnosnd.resize( (1920, 1080) )
#                 bgcrop = vfx.crop(bgnosnd,  x_center=960 , y_center=540, width=1080, height=1920)
#                 bgcrop.write_videofile(f"{bgnomp4}cropped.mp4")

# the above code does NOT work.

volx = input("Would you like to increase clip sound? y/n: ")
if volx == "Y" or "y":
    per = int(input("Percent? 1 is 100% volume, 2 is 200% volume, etc.: "))
else:
    per = 1

print(f"\nProcessing {amtfiles} files!\n")
for x in newfiles:
    x = x + ".mp4"
    xstr = x
    xstr2 = xstr.replace(".mp4", "")
    x = VideoFileClip(x)
    x = x.resize(width=720)
    durationsecs = x.duration
    if folder == 1:
        bgvid = bgfolder + "/" + str(random.choice(os.listdir(bgfolder)))
        bgnosnd = bgv.without_audio()
        bgnomp4 = bgvid.replace(".mp4", "")
        if removeaudio == "y" or removeaudio == "Y":
            bgnosnd.write_videofile(f"{bgnomp4}nosound.mp4")
            bgnosnd = VideoFileClip(f"{bgnomp4}nosound.mp4")
        else:
            bgnosnd = VideoFileClip(f"{bgnomp4}.mp4")
        if bgnosnd.size != [720, 1080]:
            bgnosnd = bgnosnd.resize( (720, 1080))
    fullclip = CompositeVideoClip([bgnosnd.set_position((0,0)).set_end(durationsecs), x.set_position((0,20))], size=(720, 1080))
    textclip = TextClip(f"Part {xstr2}", font="fjalla-one.ttf",fontsize=125, color="white", stroke_color="black", stroke_width=5)
    textclip = textclip.set_position('center').set_duration(durationsecs) 
    fullclip = CompositeVideoClip([fullclip, textclip])
    fullclip = fullclip.volumex(per)
    fullclip = vfx.make_loopable(fullclip, 0.5)
    fullclip.write_videofile(f"final{xstr}", codec="libx264", audio_codec="aac")

# if not916 != "n" or not916 != "N":
#     removecrop = input(f"Would you like to remove {bgnomp4}cropped.mp4? y/n: ")
#     if removecrop == "Y" or removecrop == "y":
#         if os.path.exists(f"{bgnomp4}cropped.mp4"):
#             os.remove(f"{bgnomp4}cropped.mp4")
if removeaudio == "y" or removeaudio == "Y":
    removesound = input(f"Would you like to remove {bgnomp4}nosound.mp4? y/n: ")
    if removesound == "Y" or removesound == "y":
        if os.path.exists(f"{bgnomp4}nosound.mp4"):
            os.remove(f"{bgnomp4}nosound.mp4")