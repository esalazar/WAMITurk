import sys
import random

def createHITFile():
    modifyFile("hit.txt","new_hit.txt")
    shuffleFile("new_hit.txt","shuffled_hit.txt")

def modifyFile(inFile, outFile):
    fp = open(inFile)
    new_fp = open(outFile, "w")
    for i, line in enumerate(fp):
        line = line.strip()
        if (len(line.split(' ')) > 4 and len(line.split(' ')) < 18) and (len(line) > 15 and len(line) < 50) and filterLine(line):
            new_fp.write(line + "\n")
    fp.close()
    new_fp.close()

def shuffleFile(inFile, outFile):
    fp = open(inFile)
    shuffled_fp = open(outFile, "w")
    lines = fp.readlines()
    random.shuffle(lines)
    for line in lines:
        shuffled_fp.write(line)
    fp.close()
    shuffled_fp.close()

def filterLine(line):
    # list of dirty words I found in the sample list that might offend the turkers
    bad_words = []
    if any(bad_word in line.lower() for bad_word in bad_words):
        return False
    # don't allow people to say the letters of a word
    single_letter_words = ["a", "i", "p", "m"]
    split_line = line.split(' ')
    for word in split_line:
        bool_single = True
        if len(word) == 1:
            for letter in single_letter_words:
                if word.lower() == letter.lower():
                    bool_single = True
                    break
                else:
                    bool_single = False
        if bool_single == False:
            return False
    return True

def createInputFile():
    fp = open("input_1001_2000_hit.txt", "w")
    fp.write("hit\n")
    for x in range(1001,2001):
        fp.write(str(x) + "\n")
    fp.close()
