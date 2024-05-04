import data.common as common

def is_number(s):
  for i in s:
    if i not in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
      return False
  return True

def number_word(user_input: str, translation_list):
    user_input = user_input.lower()
    number_word_array = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    join = "-"
    zero_stop = translate("and", translation_list)

    final_string = translate(number_word_array[int(user_input[0])], translation_list)
    user_input = user_input[1:]
    
    zero_count = 0
    while len(user_input) > 0:
        if user_input[0] == "0":
            zero_count += 1
        else:
            if zero_count > 0:
                final_string = final_string + join + translate(number_word_array[0], translation_list)
                if zero_count > 1:
                    final_string = final_string + join + translate(str(zero_count), translation_list)
                final_string = final_string + join + zero_stop
                zero_count = 0
            final_string = final_string + join + translate(number_word_array[int(user_input[0])], translation_list)
        user_input = user_input[1:]
    if zero_count > 0:
        final_string = final_string + join + translate(number_word_array[0], translation_list)
        if zero_count > 1:
            final_string = final_string + join + number_word(zero_count, translation_list)
    return final_string

def eng_to_fira(word_eng: str, translation_list: list[list[str]], ignore_punctuation = False, debug = False):
    if debug: print("eng_to_fira", word_eng)
    word_eng = word_eng.lower()
    # If no word is passed, return
    if not len(word_eng):
        return word_eng
    # Manage punctuation
    if not ignore_punctuation:
        punctuation = ["!", ",", ".", "?", "-", "+", "<", ">", "/", "(", ")", "[", "]", "{", "}", ":", ";", "@", "'", '"', "%"]
        found_punctuation = ["", ""]
        if word_eng[0] in punctuation:
            return f"{word_eng[0]}{eng_to_fira(word_eng[1:], translation_list)}"
        if word_eng[-1] in punctuation:
            return f"{eng_to_fira(word_eng[:-1], translation_list)}{word_eng[-1]}"

    # Check for numbers
    if is_number(word_eng):
        return number_word(word_eng, translation_list)
    
    for i in range(len(translation_list[0])):
        if translation_list[0][i].lower() in ["eng", "english"]:
            index_eng = i
        elif translation_list[0][i].lower() in ["fira", "fīra"]:
            index_fir = i
    for i in range(1, len(translation_list)):
        if not common.empty(translation_list[i]) and word_eng == translation_list[i][index_eng].lower():
            return translation_list[i][index_fir]
    return word_eng

def translate(text: str, translation_list: list[list[str]], debug = False):
    if debug: print("Translate", text)
    
    text = text.lower().split(" ")
    if common.empty(text): # Check for empty input
        return ""
    final_text, curr_word = "", ""
    keep_eng, last_was_combined = False, False
    c = 0
    
    if len(text) > 1: # If the input has multiple words
        for c in range(len(text)-1):
            last_was_combined = False
            keep_eng = False
            curr_word = text[c] + " " + text[c+1]
            if debug: print("c", c, "curr_word", curr_word)
             # Check for vairous special cases:
            if eng_to_fira(curr_word, translation_list, True) == curr_word: # If it's not a combined word (e.g. "one hundred")
                if debug: print("not combined")
                curr_word = text[c]
                if eng_to_fira(f"to {curr_word}", translation_list) == f"to {curr_word}": # if 'to <word>' fails to translate, i.e. it's not a conjugated verb
                    if debug: print("not verb")
                    if eng_to_fira(curr_word, translation_list) == curr_word: # If it's not a recognised word
                        if debug: print("not found")
                        keep_eng = True
                    if debug: print("found")
                else:
                    if debug: print("verb")
                    curr_word = f"to {curr_word}"
            else:
                if debug: print("combined")
                last_was_combined = True
                c += 1
                final_text =  f"{final_text} {curr_word}"
             # Update final_text
            if keep_eng:
                final_text =  f"{final_text} {curr_word}"
            elif eng_to_fira(curr_word, translation_list) != "":
                final_text = f"{final_text} {eng_to_fira(curr_word, translation_list)}"
            if debug: print("f", final_text, "lwc", last_was_combined)
        if not last_was_combined: # If the last two words were not a combined word
            if eng_to_fira(f"to {text[-1]}", translation_list) == f"to {text[-1]}": # if 'to <word>' fails to translate, i.e. it's not a conjugated verb
                if debug: print("last curr_word", curr_word)
                curr_word = eng_to_fira(text[-1], translation_list)
                if curr_word == text[-1]: # If it's not a recognised word
                    final_text = f"{final_text} {text[-1]}"
                elif curr_word != "":
                    final_text = f"{final_text} {curr_word}"
            else:
                final_text = f"{final_text} {eng_to_fira(f'to {text[-1]}', translation_list)}"
    else: # If the input is a single word
        if eng_to_fira(f"to {text[0]}", translation_list) == f"to {text[0]}": # if 'to <word>' fails to translate, i.e. it's not a conjugated verb
            curr_word = eng_to_fira(text[0], translation_list)
            if curr_word == text[0]: # If it's not a recognised word
                final_text = f"{final_text} {text[0]}"
            elif curr_word != "":
                final_text = f"{final_text} {curr_word}"
        else:
            final_text = f"{final_text} {eng_to_fira(f'to {text[0]}', translation_list)}"
    return final_text.strip()

def main(text: str, debug = False):
    word_list = common.read_file(f"{common.DATA_FILE_LOCATION}/word_list.tsv", subsplit_char="\t" , debug=debug)
    return translate(text, word_list, debug)

if __name__ == "__main__":
    darkside = ["We're not in love","We share no stories","Just something in your eyes","Don't be afraid","The shadows know me","Let's leave the world behind","Take me through the night","Fall into the dark side","We don't need the light","We'll live on the dark side","I see it, let's feel it","While we're still young and fearless","Let go of the light","Fall into the dark side","Fall into the dark side","Give into the dark side","Let go of the light","Fall into the dark side","Beneath the sky","As black as diamonds","We're running out of time (time, time)","Don't wait for truth","To come and blind us","Let's just believe their lies","Believe it, I see it","I know that you can feel it","No secrets worth keeping","So fool me like I'm dreaming","Take me through the night","Fall into the dark side","We don't need the light","We'll live on the dark side","I see it, let's feel it","While we're still young and fearless","Let go of the light","Fall into the dark side","Fall into the dark side","Give into the dark side","Let go of the light","Fall into the dark side","Take me through the night","Fall into the dark side","We don't need the light","We'll live on the dark side","I see it, let's feel it","While we're still young and fearless","Let go of the light","Fall into the dark side"]

    #print(main("yes"))
    print(main("1005", True))
    #print(main("empire will protect you"))

    #for i in darkside:
    #    print(main(i))

    #print(main(input())+"_")

