from multiprocessing.sharedctypes import Value
import os, random
from moviepy.editor import *
from pathlib import Path
import configparser
config = configparser.ConfigParser()

if not os.path.exists("config.ini"):
    config['Default'] = {
        'appVersion':'1.1'
    }
    config['VidSplitter'] = {
        'clipLength':'30s',
        'outputPath':f'{Path.cwd()}'
    }
    config['TikGen'] = {
        'batch':'True',
        'volumeMultiplier':'1',
        'looptime':'0',
        'partText':'True',
        'subText':'',
        'fontFile':'fjalla-one.ttf',
        'fontColor':'white',
        'strokeColor':'black',
        'outputPath':f'{Path.cwd()}',
        'partNumber':'1'
    }
    config.write(open("config.ini", "w"))
    print("Config file created!")
else:
    config.read("config.ini")

def isWholeNumber(integer):
    if integer - int(integer) == 0:
        return True
    else:
        return False

def isFloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def isInt(num):
    try:
        int(num)
        return True
    except ValueError:
        return False

def toSecs(clipLength):
    if clipLength.endswith("s"): # convert all to seconds
        clipLength = int(clipLength.rstrip("smh"))
    elif clipLength.endswith("m"):
        clipLength = int(clipLength.rstrip("smh")) * 60
    elif clipLength.endswith("h"):
        clipLength = int(clipLength.rstrip("smh")) * 3600
    return clipLength

def filePath(path):
    path = Path(path)
    if path.exists():
        return True, str(path.absolute())
    else:
        return False, str(Path.cwd)
        

def selectFile(file):
    outputPath = input(f"Input {file.lower()} path: ")
    while not filePath(outputPath)[0]:
        print(f"{file.title()} not found! Did you properly path to it?")
        outputPath = input(f"Input {file.lower()} path: ")
    return filePath(outputPath)[1]

'''
 __     ___     _ ____        _ _ _   _            
 \ \   / (_) __| / ___| _ __ | (_) |_| |_ ___ _ __ 
  \ \ / /| |/ _` \___ \| '_ \| | | __| __/ _ \ '__|
   \ V / | | (_| |___) | |_) | | | |_| ||  __/ |   
    \_/  |_|\__,_|____/| .__/|_|_|\__|\__\___|_|   
                       |_|                         
'''

def vidsplitter():
    print(" __     ___     _ ____        _ _ _   _            \n \ \   / (_) __| / ___| _ __ | (_) |_| |_ ___ _ __ \n  \ \ / /| |/ _` \___ \| '_ \| | | __| __/ _ \ '__|\n   \ V / | | (_| |___) | |_) | | | |_| ||  __/ |   \n    \_/  |_|\__,_|____/| .__/|_|_|\__|\__\___|_|   \n                       |_|                         ")
    print(f"Vidsplitter v{config['Default']['appVersion']}")

    if os.path.exists("config.ini"):
        useConfigQuery = input("Use configuration? y/n, or enter \"print\" to print configuration: ").lower()
        while useConfigQuery == "print":
            print(f"Clip Length = {config['VidSplitter']['clipLength']}")
            print(f"Output path = {config['VidSplitter']['outputPath']}")
            useConfigQuery = input("Use configuration? y/n, or enter \"print\" to print configuration: ").lower()
        if useConfigQuery == "y":
            useConfig = True
        else:
            useConfig = False

    if useConfig == True:
        clipLength = config["VidSplitter"]["clipLength"]
        print(f"Skipping clip length selection! Set to {clipLength}")
    else:
        clipLength = input("How long should each clip be? Enter the amount and then the unit, i.e. \"10s\": ")
        while not clipLength.rstrip("smh").isdigit() or clipLength.isdigit() or not int(clipLength.rstrip("smh")) > 0: # while it's not a number when you remove s, m, and h from the end or if it's less than 1
            print("Invalid input!")
            clipLength = input("How long should each clip be? Enter the amount and then the unit, i.e. \"10s\": ")

    clipLength = toSecs(clipLength)

    fullVideo = selectFile("file")

    while not fullVideo.endswith(".mp4"): # if it's like an mkv or something
        if input("Video is not mp4! Re-encode? y/n: ").lower() == "y":
            newfile = Path(Path.cwd()).joinpath(input('Filename of converted video?: ') + ".mp4")
            VideoFileClip(fullVideo).write_videofile(f"{newfile}", codec="libx264",audio_codec="aac")
            fullVideo = newfile
        else:
            print("Cannot continue! Exiting...")
            quit()
    
    fullVideoDurationSecs = VideoFileClip(fullVideo).duration # duration in seconds + milliseconds, like [1179.45] being 1179 seconds and 45 ms
    
    if not isWholeNumber(fullVideoDurationSecs):
        int_fullVideoDurationSecs = int(fullVideoDurationSecs) + 1 # if it's not a whole number, cut off the ms and then add 1 to the seconds
    else:
        int_fullVideoDurationSecs = int(fullVideoDurationSecs)
    # the purpose for this is to round up the length of the video to the next second

    if int_fullVideoDurationSecs % clipLength != 0: # if the video length isn't divisible by the clips length
        int_fullVideoDurationSecs_clip = (int_fullVideoDurationSecs - (int_fullVideoDurationSecs % clipLength)) + clipLength

    start = 0
    if input("Start first clip at certain time? y/n: ").lower() == "y":
        end = input("What time, in seconds, should the clip start at?: ")
        while not end.isdigit() or not int(end) > 0:
            print("Invalid input!")
            end = input("What time, in seconds, should the clip start at?: ")
        end = int(end)
    else:
        end = 0
    times = []
    while not end >= int_fullVideoDurationSecs_clip:
        start = end # end of previous clip
        end = end + clipLength # increment by the length of each clip
        times.append((start, end))

    if useConfig == True:
        outputPath = config["VidSplitter"]["outputPath"]
        print(f"Skipping output path selection! Set to \"{outputPath}\"")
    else:
        if input("Write files to other directory? y/n: ").lower() == "y":
            outputPath = selectFile("folder")
        else:
            outputPath = Path.cwd()

    # now we have all of the variables we'd possibly need. the length of the video in minutes and seconds, and also the same thing but rounded up to the nearest minute/second.

    if input("Offset clip naming? i.e. starting at 70.mp4 instead of 1.mp4, y/n: ").lower() == "y":
        offset = input("Offset: ")
        while not offset.isdigit() or not int(offset) > 0: # if it's not a number or is less than zero
            print("Invalid input!")
            offset = input("Number to start at: ")
        offset = int(offset) - 1 # we'll be adding it to the number later so i.e. if we want to start at 70 and it's starting at 1 it would start at 71
    else:
        offset = 0

    for i in range(len(times)):
        starttime = times[i][0]
        endtime = times[i][1]
        if endtime >= fullVideoDurationSecs:
            print(f"Cropping endtime from {endtime} to {fullVideoDurationSecs} seconds!")
            endtime = None # none is null which means it goes as far as it can 
        currentclip = VideoFileClip(fullVideo).subclip(starttime, endtime)
        filename = Path(outputPath).joinpath(f"{str(i + 1 + offset)}.mp4")
        currentclip.write_videofile(filename, audio_codec='aac')
    
    if input("Complete! Would you like to save your settings? y/n: ").lower() == "y":
        config['VidSplitter']['clipLength'] = clipLength
        config['VidSplitter']['outputPath'] = outputPath
        print("Complete!")
    quit()
        

print("  _____ _ _     ____            \n |_   _(_) | __/ ___| ___ _ __  \n   | | | | |/ / |  _ / _ \ '_ \ \n   | | | |   <| |_| |  __/ | | |\n   |_| |_|_|\_\\____|\___|_| |_|\n")
print(f"TikGen v{config['Default']['appVersion']}")

if input("Use Vidsplitter? y/n: ").lower() == "y":
    for i in range (30):
        print("\n")
    vidsplitter()

for i in range (30):
    print("\n")

'''
  _____ _ _     ____            
 |_   _(_) | __/ ___| ___ _ __  
   | | | | |/ / |  _ / _ \ '_ \ 
   | | | |   <| |_| |  __/ | | |
   |_| |_|_|\_\\____|\___|_| |_|
                                
'''

def optional(inputText):
    if input(inputText).lower() == "y":
        return True
    else:
        return False

# Going forward, the background clip will be referred to as "clip" and the video clip will be referred to as "video".
def tikgen():

    print("  _____ _ _     ____            \n |_   _(_) | __/ ___| ___ _ __  \n   | | | | |/ / |  _ / _ \ '_ \ \n   | | | |   <| |_| |  __/ | | |\n   |_| |_|_|\_\\____|\___|_| |_|\n")
    print(f"TikGen v{config['Default']['appVersion']}")
    
    if os.path.exists("config.ini"):
        useConfigQuery = input("Use configuration? y/n, or enter \"print\" to print configuration: ").lower()
        while useConfigQuery == "print":
            print(f"Process multiple files = {config['TikGen']['batch']}")
            print(f"Loop time(seconds) = {config['TikGen']['loopTime']}")
            print(f"Volume Multiplier = {config['TikGen']['volumeMultiplier']}")
            print(f"Add part text = {config['TikGen']['partText']}")
            print(f"Subtext = {config['TikGen']['subText']}")
            print(f"Default font file = {config['TikGen']['fontFile']}")
            print(f"Default font color = {config['TikGen']['fontColor']}")
            print(f"Default text stroke color = {config['TikGen']['strokeColor']}")
            print(f"Output path = {config['TikGen']['outputPath']}")
            useConfigQuery = input("Use configuration? y/n, or enter \"print\" to print configuration: ").lower()
        if useConfigQuery == "y":
            useConfig = True
        else:
            useConfig = False

    if useConfig == True:
        batch = config["TikGen"].getboolean("batch")
        print(f"Skipping file count selection! Batch mode set to {batch}")
    else:
        singleorbatch = input("Would you like to process one file or multiple? Respond \"one\" or \"multiple\": ")
        while singleorbatch != "one" and singleorbatch != "multiple":
            print("Invalid Input!")
            singleorbatch = input("Would you like to process one file or multiple? Respond \"one\" or \"multiple\": ")
        if singleorbatch == "one":
            batch = False
        elif singleorbatch == "multiple":
            batch = True
    
    if useConfig == True:
        loopTime = config["TikGen"]["loopTime"]
        print(f"Skipping loop time selection! Set to {loopTime}s")
    else:
        if input("Would you like to make the video loopable? y/n: ").lower() == "y":
            loopTime = input("How many seconds should the video looping take? Recommended 0.3: ")
            while not isFloat(loopTime):
                if isInt(loopTime):
                    if int(loopTime) >= 0:
                        break
                else:
                    print("Invalid input!")
                    loopTime = input("How many seconds should the video looping take? Recommended 0.3: ")
        else:
            loopTime = 0
    
    if useConfig == True:
        volumeMultiplier = config["TikGen"]["volumeMultiplier"]
        print(f"Skipping volume multiplier selection! Set to {volumeMultiplier}x")
    else:
        if input("Would you like to multiply the video's audio? y/n: ").lower() == "y":
            volumeMultiplier = input("How many times should the volume be multiplied by?: ")
            while not isFloat(volumeMultiplier):
                if isInt(volumeMultiplier):
                    if int(volumeMultiplier) > 0:
                        break
                else:
                    print("Invalid input!")
                    volumeMultiplier = input("How many seconds should the video looping take? Recommended 0.3: ")
        else:
            volumeMultiplier = 1
    
    if useConfig == True:
        partText = config["TikGen"].getboolean("partText")
        print(f"Skipping part text selection! Set to {partText}")
    else:
        if input("Add text showing which part each video is? y/n: ").lower() == "y":
            partText = True
        else:
            partText = False

    if useConfig == True:
        if input("Use config for subtext? y/n: ").lower() == "y":
            subText = config["TikGen"]["subText"]
            print(f"Skipping subtext selection! Set to \"{subText}\"")
        else:
            if input("Add subtext to the video? y/n: ").lower() == "y":
                subText = input("What subtext should be used?: ")
            else:
                subText = ""
    else:
        if input("Add subtext to the video? y/n: ").lower() == "y":
            subText = input("What subtext should be used?: ")
        else:
            subText = ""
    
    if subText != "" or partText == True:
        if useConfig == True:
            fontFile = config["TikGen"]["fontFile"]
            fontColor = config["TikGen"]["fontColor"]
            strokeColor = config["TikGen"]["strokeColor"]
            print(f"Skipping font selection! Set to {fontFile}, color {fontColor}, stroke color {strokeColor}")
        else:
            if input("Use custom font file? y/n: ").lower() == "y":
                selectFile("file")
            else:
                if os.path.exists(config["TikGen"]["fontFile"]):
                    fontFile = config["TikGen"]["fontFile"]
            if input("Use custom font color? y/n: ").lower() == "y":
                fontColor = input("Input font color, or enter \"list\" for a list of acceptable colors: ")
                while fontColor == "list" or not fontColor in TextClip.list('color'):
                    if fontColor == "list":
                        print(f"Acceptable colors:\n\n {TextClip.list('color')}\n\n")
                        fontColor = input("Input font color, or enter \"list\" for a list of acceptable colors: ")
                    else:
                        print("Not a valid color! Enter \"list\" for a list of acceptable colors.")
                        fontColor = input("Input font color, or enter \"list\" for a list of acceptable colors: ")
            else:
                fontColor = "white"
                
            if input("Use custom text stroke color? y/n: ").lower() == "y":
                strokeColor = input("Input stroke color, or enter \"list\" for a list of acceptable colors: ")
                while strokeColor == "list" or not strokeColor in TextClip.list('color'):
                    if strokeColor == "list":
                        print(f"Acceptable colors:\n\n {TextClip.list('color')}\n\n")
                        strokeColor = input("Input font color, or enter \"list\" for a list of acceptable colors: ")
                    else:
                        print("Not a valid color! Enter \"list\" for a list of acceptable colors.")
                        strokeColor = input("Input font color, or enter \"list\" for a list of acceptable colors: ")
            else:
                strokeColor = "black"
    
    if batch == True:
        bgVidFolder = selectFile("background video folder")
        mainVidFolder = selectFile("main video folder")

        bgVid = []
        for i in os.listdir(bgVidFolder):
            if i.endswith(".mp4"):
                bgVid.append(i)

        mainVid = []
        for i in os.listdir(mainVidFolder):
            if i.endswith(".mp4"):
                for x in range(4):
                    i = i[:-1]
                mainVid.append(i)
        try:
            mainVid.sort(key=int)
        except Exception as i:
            print(i)
            print("An error occured! Are your main video files as such: (\"1.mp4\", \"2.mp4\", etc.)?")
            quit()

        if useConfig == True:
            outputPath = config["TikGen"]["outputPath"]
            print(f"Skipping output path selection! Set to \"{outputPath}\"")
        else:
            if input("Write files to other directory? y/n: ").lower() == "y":
                outputPath = selectFile("folder")
            else:
                outputPath = Path.cwd()

        if partText == True:
            if useConfig == True:
                partNumber = int(config["TikGen"]["partNumber"])
                print(f"Skipping part number selection! Set to {partNumber}")
            else:
                if input("Would you like to start at a custom part number? y/n: ") == "y":
                    partNumber = input("What part number should it start at?: ")
                    while not isInt(partNumber):
                        print("Invalid Input!")
                        partNumber = input("What part number should it start at?: ")
                    partNumber = int(partNumber)
                else:
                    partNumber = 1
        else:
            partNumber = 1

        '''
        Parameters collected:

        batch
        loopTime
        volumeMultiplier
        partText
        subText
        fontFile
        fontColor
        strokeColor
        outputPath
        partNumber
        '''


        for i in mainVid:
            mainVideo = VideoFileClip(str(Path(mainVidFolder).joinpath(f"{i}.mp4"))).resize(width=720)
            bgVideo = VideoFileClip(str(Path(bgVidFolder).joinpath(str(random.choice(os.listdir(bgVidFolder)))))).without_audio()
            if bgVideo.size != [720, 1280]:
                bgVideo = bgVideo.resize(720, 1280)
            
            finalVideo = CompositeVideoClip([bgVideo.set_position((0,0)).set_end(mainVideo.duration), mainVideo.set_position((0,50)).volumex(float(volumeMultiplier))], size=(720, 1280))
            if partText == True:
                partTextClip = TextClip(f"Part {partNumber}", font=fontFile, fontsize=125, color=fontColor, stroke_color=strokeColor, stroke_width=5).set_position("center").set_duration(mainVideo.duration)
                finalVideo = CompositeVideoClip([finalVideo, partTextClip])
            if subText != "":
                subTextClip = TextClip(subText, font=fontFile, fontsize=75, color=fontColor, stroke_color=strokeColor, stroke_width=3).set_position(("center", 725)).set_duration(mainVideo.duration)
                finalVideo = CompositeVideoClip([finalVideo, subTextClip])
            finalVideo = vfx.make_loopable(finalVideo, float(loopTime))

            filename = str(Path(outputPath).joinpath(f"final_{str(partNumber)}.mp4"))
            finalVideo.write_videofile(filename, codec="libx264", audio_codec="aac")
            partNumber = partNumber + 1
    elif batch == False:
        bgVidFile = selectFile("background video file")
        mainVidFile = selectFile("main video file")

        if partText == True:
            partNumber = input("Video part number: ")
        else:
            partNumber = 1

        mainVideo = VideoFileClip(mainVidFile).resize(width=720)
        bgVideo = VideoFileClip(bgVidFile).without_audio()
        if bgVideo.size != [720, 1280]:
            bgVideo = bgVideo.resize(720, 1280)

        finalVideo = CompositeVideoClip([bgVideo.set_position((0,0)).set_end(mainVideo.duration), mainVideo.set_position((0,50)).volumex(float(volumeMultiplier))], size=(720, 1280))
        if partText == True:
            partTextClip = TextClip(f"Part {partNumber}", font=fontFile, fontsize=125, color=fontColor, stroke_color=strokeColor, stroke_width=5).set_position("center").set_duration(mainVideo.duration)
            finalVideo = CompositeVideoClip([finalVideo, partTextClip])
        if subText != "":
            subTextClip = TextClip(subText, font=fontFile, fontsize=75, color=fontColor, stroke_color=strokeColor, stroke_width=3).set_position(("center", 725)).set_duration(mainVideo.duration)
            finalVideo = CompositeVideoClip([finalVideo, subTextClip])
        finalVideo = vfx.make_loopable(finalVideo, float(loopTime))

        filename = str(Path(outputPath).joinpath(f"final_{str(partNumber)}.mp4"))
        finalVideo.write_videofile(filename, codec="libx264", audio_codec="aac")

    if input("Complete! Would you like to save your settings? y/n: ").lower() == "y":
        config['TikGen']['batch'] = batch
        config['TikGen']['volumeMultiplier'] = volumeMultiplier
        config['TikGen']['loopTime'] = loopTime
        config['TikGen']['partText'] = partText
        config['TikGen']['subText'] = subText
        config['TikGen']['fontFile'] = fontFile
        config['TikGen']['fontColor'] = fontColor
        config['TikGen']['strokeColor'] = strokeColor
        config['TikGen']['outputPath'] = outputPath
        config['TikGen']['partNumber'] = partNumber
        print("Complete!")
    quit()


tikgen()
