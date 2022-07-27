import os
from moviepy.editor import *

newfiles = [] #define newfiles
files = os.listdir() #create a list of every file in directory
for x in files:
    x = str(x.replace(".mp4", "")) # get rid of file extension
    newfiles.append(x) #create a new list without extensions
newfiles = [s for s in newfiles if s.isdigit()] #remove non-numbers from the list
newfiles.sort(key=int) #sort by number
amtfiles = len(newfiles)

bgvid = input("\nFilename of background clip? Include extension, use 9:16 aspect ratio: ")

bgv = VideoFileClip(bgvid)
if bgv.duration < VideoFileClip(newfiles[0] + ".mp4").duration: # if the background vid is shorter than the clip duration
    duration = int(VideoFileClip(newfiles[0] + ".mp4").duration) / 60 # turn video duration into minutes 
    bgduration = int(bgv.duration) / 60 # turn background duration into minutes
    askduration = input(f"\nIt looks like your videos are {duration} minutes long, but your background video is only {bgduration} minutes long. Continue? Y/N: ")
    if askduration == "n" or askduration == "N":
        quit()
    #basically if the background video is too short it'll ask if you want to continue

bgnosnd = bgv.without_audio()
bgnomp4 = bgvid.replace(".mp4", "")

if os.path.exists(f"{bgnomp4}nosound.mp4"): #if the no sound version already exists
    print(f"\n\"{bgnomp4}nosound.mp4\" already exists, skipping audio removal")
    pass
else:
    print(f"\nRemoving audio from the background video!")
    bgnosnd.write_videofile(f"{bgnomp4}nosound.mp4") #writes a new file as ___nosound.mp4
    bgnosnd = VideoFileClip(f"{bgnomp4}nosound.mp4") #redefines bgnosnd as the video without sound

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

if bgnosnd.size != [720, 1080]:
    bgnosnd = bgnosnd.resize( (720, 1080))

print(f"\nProcessing {amtfiles} files!\n")
for x in newfiles:
    x = x + ".mp4"
    xstr = x
    xstr2 = xstr.replace(".mp4", "")
    x = VideoFileClip(x)
    x = x.resize(width=720)
    durationsecs = x.duration
    fullclip = CompositeVideoClip([bgnosnd.set_position((0,0)).set_end(durationsecs), x.set_position((0,20))], size=(720, 1080))
    textclip = TextClip(f"Part {xstr2}", font="fjalla-one.ttf",fontsize=125, color="white", stroke_color="black", stroke_width=5)
    textclip = textclip.set_pos('center').set_duration(durationsecs) 
    fullclip = CompositeVideoClip([fullclip, textclip])
    fullclip = fullclip.volumex(4)
    fullclip = vfx.make_loopable(fullclip, 0.5)
    fullclip.write_videofile(f"final{xstr}")

# if not916 != "n" or not916 != "N":
#     removecrop = input(f"Would you like to remove {bgnomp4}cropped.mp4? y/n: ")
#     if removecrop == "Y" or removecrop == "y":
#         if os.path.exists(f"{bgnomp4}cropped.mp4"):
#             os.remove(f"{bgnomp4}cropped.mp4")
removesound = input(f"Would you like to remove {bgnomp4}nosound.mp4? y/n: ")
if removesound == "Y" or removesound == "y":
    if os.path.exists(f"{bgnomp4}nosound.mp4"):
        os.remove(f"{bgnomp4}nosound.mp4")