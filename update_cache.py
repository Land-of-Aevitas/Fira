import data.spreadsheet as sheets
import data.common as common

def get_translations(debug = False):
    
    formulas = common.read_file(f"{common.DATA_FILE_LOCATION}/formulas.txt", debug=debug)
    for i in range(len(formulas)):
        if len(formulas[i]) == 0 or formulas[i][0] != "=":
            formulas[i] = "-"
        else:
            replace_bank = [
                ["=addGender", "add_gender"],
                ["=createWord", "create_word"],
                ["=multiCompoundWord", "compound_word"],
                ["=compoundWord", "compound_word"],
                ["=numberWord", "number_word"],
            ]
            for j in replace_bank:
                #print(j, len(j[0]), formulas[i][:len(j[0])])
                if formulas[i][:len(j[0])].lower() == j[0].lower():
                    formulas[i] = f"{j[1]}{formulas[i][len(j[0]):]}"
    
    sheet_id = "13KDITzV5F0D-_dOVp5ZiHeFLWGx1e0V6SV9oRrzeODw"
    scopes = ["https://www.googleapis.com/auth/drive.readonly", "https://www.googleapis.com/auth/spreadsheets.readonly"]
    token_location = f"{common.DATA_FILE_LOCATION}/token.json"
    credentials_location = f"{common.DATA_FILE_LOCATION}/credentials.json"

    translation_list = ["Type (0=base,1=synonym/plural)\tEnglish\tFira\tFormula\tNote"]
    if debug: print("Retrieving translations from spreadsheet (1/3)")
    lex1_list, lex1_index = sheets.retrieve_range_with_index(sheet_id, "Lexicon", scopes, token_location, credentials_location)
    if debug: print("Retrieving translations from spreadsheet (2/3)")
    lex2_list, lex2_index = sheets.retrieve_range_with_index(sheet_id, "Extended Lexicon", scopes, token_location, credentials_location)
    if debug: print("Retrieving translations from spreadsheet (3/3)")
    lex3_list, lex3_index = sheets.retrieve_range_with_index(sheet_id, "Plural Lexicon", scopes, token_location, credentials_location)
    if debug: print("All translations recieved")
    
    itotal = 0
    for i in lex1_list[1:]:
        itotal += 1
        if not common.empty(i[lex1_index['English']]) and not common.empty(i[lex1_index['Fīra']]):
            translation_list.append(f"0\t{i[lex1_index['English']]}\t{i[lex1_index['Fīra']]}\t{formulas[itotal]}\t{i[lex1_index['Notes']]}")
    for i in lex2_list[1:]:
        itotal += 1
        if not common.empty(i[lex2_index['English']]) and not common.empty(i[lex2_index['Fīra']]):
            translation_list.append(f"1\t{i[lex2_index['English']]}\t{i[lex2_index['Fīra']]}\t{i[lex2_index['Formula']]}\t-")
    for i in lex3_list[1:]:
        itotal += 1
        if not common.empty(i[lex3_index['Plural English']]) and not common.empty(i[lex3_index['Plural Fīra']]):
            translation_list.append(f"1\t{i[lex3_index['Plural English']]}\t{i[lex3_index['Plural Fīra']]}\t{i[lex3_index['Formula']]}\t-")
    translation_list.append("0\tThe\t\t-\t-") # Since 'The' translates to nothing, the code won't retrieve it by default so I need to add it manually.
    
    with open(f"{common.DATA_FILE_LOCATION}/cache.tsv","w",encoding="utf16") as file:
        for i in translation_list:
            file.write(f"{i}\n")
        #file.writelines(translation_list)
    return

if __name__ == "__main__":
    get_translations(True)