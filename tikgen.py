from multiprocessing.sharedctypes import Value
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

volx = input("Would you like to increase clip sound? y/n: ")
if volx == "Y" or "y":
    per = int(input("Percent? 1 is 100% volume, 2 is 200% volume, etc.: "))
else:
    per = 1

loopable = input("Would you like to make the main video loopable? y/n: ")
if loopable.lower() == "y":
    loopamt = input("How many seconds of loop time? Recommended 0.5: ")
    try:
        float(loopamt) # test if it works as a float
    except ValueError: # value error is the exception you'll get if it can't be a float
        print("Invalid input! Disabling loop...")
        loopable = "n"
    else: # else runs only if try doesn't have an exception
        if float(loopamt) <= 0:  # if it's negative
            print("Invalid input! Disabling loop...")
            loopable = "n"
else: # if you don't put in y
    print("Not looping video!")
    loopable = "n"


addsubtext = input("Add subtext to the videos? y/n: ") # subtext is just another loop in the ending code
if addsubtext.lower() == "y":
    subtextstr = input("What will the subtext be?: ")
else:
    addsubtext = "n" #any input besides y will make it become n

print(f"\nProcessing {amtfiles} files!\n") # cosmetic
for x in newfiles: # loops for every file that follows the 1.mp4, 2.mp4 structure
    x = x + ".mp4" # add back the file extension
    xstr = x # i dunno clones x for some reason
    xstr2 = xstr.replace(".mp4", "") # has a string version that has no .mp4
    x = VideoFileClip(x) # convert to videofileclip
    x = x.resize(width=720) # height will be computed
    durationsecs = x.duration # duration of the file in seconds
    if folder == 1: # if folder mode is enabled
        bgvid = bgfolder + "/" + str(random.choice(os.listdir(bgfolder))) # random file from the folder you chose,
        print(f"Using {bgvid} for final{xstr}!")
        bgnosnd = bgv.without_audio() # defines the nosound version
        bgnomp4 = bgvid.replace(".mp4", "") # remove the extension
        if removeaudio == "y" or removeaudio == "Y": # if removing audio is enabled
            bgnosnd.write_videofile(f"{bgnomp4}nosound.mp4")
            bgnosnd = VideoFileClip(f"{bgnomp4}nosound.mp4")
        else:
            bgnosnd = VideoFileClip(f"{bgnomp4}.mp4") # i don't even know if this is necessary but why not
        if bgnosnd.size != [720, 1080]: # make sure it's 720x1080, or 720p
            bgnosnd = bgnosnd.resize( (720, 1080))
    fullclip = CompositeVideoClip([bgnosnd.set_position((0,0)).set_end(durationsecs), x.set_position((0,20))], size=(720, 1080))
    textclip = TextClip(f"Part {xstr2}", font="fjalla-one.ttf",fontsize=125, color="white", stroke_color="black", stroke_width=5)
    textclip = textclip.set_position('center').set_duration(durationsecs) 
    # ^^^ all just stuff about placing the clips properly and adding text
    fullclip = CompositeVideoClip([fullclip, textclip]) #combine the video with the text we just define
    fullclip = fullclip.volumex(per) # if you enabled multiplying volume, this would add more sound to the clip
    if loopable != "n": # if looping the clip is enabled, add that in
        fullclip = vfx.make_loopable(fullclip, float(loopamt))
    if addsubtext != "n": # if subtext is enabled, add that in
        subtext = TextClip(subtextstr, font="fjalla-one.ttf",fontsize=75, color="white", stroke_color="black", stroke_width=3)
        subtext = subtext.set_position(("center", 650)).set_duration(durationsecs) 
        fullclip = CompositeVideoClip([fullclip, subtext])
    fullclip.write_videofile(f"final{xstr}", codec="libx264", audio_codec="aac") # write the file