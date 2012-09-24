import csv
import os
import urllib2
import subprocess
import wave

def audioURL(appname, code, hit, prompt, audio_format):
    return "http://" + appname.lower() + ".appspot.com/audio?name=" + audioName(code.lower(), hit, prompt, audio_format.lower())

def audioName(code, hit, prompt, audio_format):
    return "-".join([code.lower(), hit, prompt]) + "." + audio_format.lower()

def promptName(code, hit):
    return "-".join([code.lower(), hit]) + ".txt"

def promptURL(appname, hit):
    return "http://" + appname.lower() + ".appspot.com/hit?hit=" + hit

def statURL(appname, code, hit, prompt, audio_format):
    return "http://" + appname.lower() + ".appspot.com/stat?name=" + audioName(code.lower(), hit, prompt, audio_format.lower())

def parseStatURL(content):
    top_url = content.split("?")
    bottom_url = top_url[1].split("&")
    ordering = ["version", "model", "manufacturer", "brand", "net"]
    for item in bottom_url:
        item_split = item.split("=")
        if  item_split[0] == "version":
            ordering[0] = item_split[1]
        if  item_split[0] == "model":
            ordering[1] = item_split[1]
        if  item_split[0] == "manufacturer":
            ordering[2] = item_split[1]
        if  item_split[0] == "brand":
            ordering[3] = item_split[1]
        if  item_split[0] == "net":
            ordering[4] = item_split[1]
    return ordering

def getStatData(appname, worker, code, hit, audio_format):
    stats = []
    try:
        u = urllib2.urlopen(statURL(appname, code, hit, "0", audio_format))
        stats = [worker, audioName(code,hit,"0", audio_format)]
        stats = stats + parseStatURL(u.read())
    except:
        stats = [worker, audioName(code,hit,"0", audio_format), "version", "model", "manufacturer", "brand", "net"]
    return stats

def createInHeaderMap(header):
    mapping = {}
    need = ["WorkerId", "AcceptTime", "WorkTimeInSeconds", "Input.hit", "Answer.Code"]
    col_num = 0
    for item in header:
        if item in need:
            mapping[item] = col_num
        col_num += 1
    return mapping

# goes through our sanity checks and returns an error or empty string
def check(audio_path):
    error = ""
    try:
        wave_file = wave.open(audio_path, "r")
	time = (1.0 * wave_file.getnframes() / wave_file.getframerate())
        if time < 1:
            error = "small time at " + str(time) + "s"
	wave_file.close()
    except:
        error = "can't open file " + audio_path
    return error

def convertAudio(audio_path, from_format, to_format):
    new_audio_path = audio_path
    if from_format != to_format:
	new_audio_path = audio_path.replace("." + from_format, "." + to_format)
        if not os.path.isfile(new_audio_path):
	    try:
	        command = ["sox", audio_path, new_audio_path]
    	        subprocess.Popen(command)
	    except:
	        return "error"
    return new_audio_path

def main(mTurk_file, appname, num_prompts, audio_format, to_audio_format):
    root_path = "audio/"
    headerIn = {}
    turk  = open(mTurk_file, "rb")
    reader = csv.reader(turk)

    # create result file
    headerOut = ["WorkerId", "Answer.Code", "Input.hit", "Prompt", "Error"]
    result_file = open("error_result.csv", 'wb')
    writer = csv.writer(result_file)
    writer.writerow(headerOut)

    # create stat file
    headerStatOut = ["WorkerId", "name", "version", "model", "manufacturer", "brand", "net"]
    result_stat_file = open("stat_result.csv", 'wb')
    writer_stat = csv.writer(result_stat_file)
    writer_stat.writerow(headerStatOut)

    # go through the mTurk results list
    row_num = 0
    for row in reader:
        if row_num == 0:
            headerIn = createInHeaderMap(row)
        elif row_num == 3:
            break
        else:
            # record stat for one hit default prompt = 0
            writer_stat.writerow(getStatData(appname, row[headerIn["WorkerId"]], row[headerIn["Answer.Code"]], row[headerIn["Input.hit"]], audio_format))
            # create worker path
            worker_path = root_path + row[headerIn["WorkerId"]] + "/"
            if not os.path.isdir(worker_path):
               os.makedirs(worker_path)
            # create hit path within worker path
            hit_path = worker_path + row[headerIn["Input.hit"]] + "/"
            if not os.path.isdir(hit_path):
               os.makedirs(hit_path)
            # get the prompts
            prompt_path = hit_path + promptName(row[headerIn["Answer.Code"]], row[headerIn["Input.hit"]])
            prompt_url = promptURL(appname, row[headerIn["Input.hit"]])
            if not os.path.isfile(prompt_path):
                try:
                    u = urllib2.urlopen(prompt_url)
                    prompt_file = open(prompt_path, 'wb')
                    prompt_file.write(u.read())
                    prompt_file.close()
                except:
                    print "error retrieving: " + prompt_url
            # go through each prompt to download the file
            for prompt in range(num_prompts):
                error = ""
                # download the audio file
                audio_url = audioURL(appname, row[headerIn["Answer.Code"]], row[headerIn["Input.hit"]], str(prompt), audio_format)
                audio_path = hit_path + audioName(row[headerIn["Answer.Code"]], row[headerIn["Input.hit"]], str(prompt), audio_format)
                try:
                    if not os.path.isfile(audio_path):
                        u = urllib2.urlopen(audio_url)
                        audio_file = open(audio_path, 'wb')
                        audio_file.write(u.read())
                        audio_file.close()
                    # run checks
		    audio_path = convertAudio(audio_path, audio_format, to_audio_format)
                    error = check(audio_path)
                except:
                    error = "error retrieving: " + audio_url
                    print error
                if error != "":
                    writer.writerow([row[headerIn["WorkerId"]], row[headerIn["Answer.Code"]], row[headerIn["Input.hit"]], str(prompt), error])
        row_num += 1
    turk.close()
    result_stat_file.close()
    result_file.close()

if __name__ == "__main__":
    main("batch_results.csv", "wamiturk", 10, "flac", "wav")
