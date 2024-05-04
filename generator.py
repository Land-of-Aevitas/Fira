import data.common as common

'''def create_word(location, trim1=2, trim2=0):
    words = trimArray((location+"").split("+"))
    if len(words) == 2: # If the input info requires compoundWord
        return compoundWord(words[0], words[1], trim1, trim2)
    elif len(words) > 2: # for multiCompoundWord
        #return words[0]+words[1]+words[2]
        return multiCompoundWord(trim1, ...words, trim2)
    elif len(words) == 1:
        words = words[0].split("of")
        words = trimArray(words)
        if len(words) > 1: # for deriveWord
            if ["verb", "plural"].indexOf(words[0].toLowerCase()) >= 0: # Checks to see if words[0].toLowerCase() is "verb" or "plural"
                return deriveWord(words[1], words[0], "p", trim1, trim2)
        data = words[0].split(" ")
        #return words[1]+"|"+data[1]+"|"+data[0]+"|"+trim1+"|"+trim2
        return deriveWord(words[1], data[1], data[0], trim1, trim2)
    return len(words)'''

def update_words(debug = False):
    word_list = common.read_file(f"{common.DATA_FILE_LOCATION}/word_list.tsv", subsplit_char="\t" , debug=debug)
    for i in range(len(word_list[0])):
        if "type" in word_list[0][i].lower():
            index_type = i
        if "english" in word_list[0][i].lower():
            index_eng = i
        elif word_list[0][i].lower() in ["fira", "fīra"]:
            index_fir = i
    #exec()
    return

if __name__ == "__main__":
    update_words()

