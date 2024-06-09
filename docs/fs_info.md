# Terminology
Root word - stored in rootWordTable. It stores the translation directly and so won't update if it's constituents change.
Complex word - stored in the wordTable. Defined in terms of other words and so can be updated if those words change.
# Commands

## Defining Words
- `DEFROOT <wordEng> <wordFira> <params>`: Define a root word. `<wordEng>` is a string with the English word and `<wordFira>` is another string with it's Fira translation.
  - `END <m|M|f|F|n|N|p|P>`: Adds a gendered or other ending to the word: `m` = Masculine, `f` = Feminine, `n` = Neutral, `p` = Plural. Use a capitalised letter to replace the last letter of the word instead of appending to it.
  - `NOTE <string>` Adds a note in the .db file next to this word's entry.
- `DEFWORD <wordEng1> FROM <wordEngs> <params>`: Define a complex (non-root) word using other words.
  - `WITH <withType>`: By default, all constituents are appended to each other to form the new word. A `WITH <>` command can be used to change the concatenation type. This must immediately follow the `DEFWORD ... FROM ...`.
    - `WITH SLICE <ints>`: Appends all words together, but additionally removes a number of characters from the start and end of each word as specified by the `<ints>`. The order of the ints is as follows: word1start word1end word2start word2end etc. Putting a 0 at the end of a word will make it go to the end, so `2 0` will be interpreted as `[2:]`.
    - `WITH JOIN <string>`:  Adds the string between each word. If no string is provided, it defaults to `""`.
  - `END <m|M|f|F|n|N|p|P>`: Adds a gendered or other ending to the word: `m` = Masculine, `f` = Feminine, `n` = Neutral, `p` = Plural. Use a capitalised letter to replace the last letter of the word instead of appending to it.
  - `NOTE <string>` Adds a note in the .db file next to this word's entry.

## Retrieving Words
- `LIST <string> <params>`: Lists all words that match the string. Leave blank to list all words.
  - `LANG <e|f>`: Only searches words in a certain language. `e` = English, `f` = Fira.
  - `TYPE <r|c>`: Only searches a specific table. `r` = Root word table, `c` = Complex word table.
  - `NOTE`: Prints any notes stored matching entries.
- `TRANSLATE <string> TO <f|e>`: Outputs the translation of a word to the specified language

## Modifying Words
- `UPDATE <wordEng> <wordFira>`: Overrides the previous value of wordEng to wordFira. Only works on root words.
- `DELETE <wordEng>`: Deletes the specified word. Searches both English and Fira for both root & complex words.

## Other commands
  - `HELP`: Prints this page to the console.
  - `READ <file location>`: Reads the file at the specified address and executes it. It must be a .fira file!
  - `DEBUG <debug command>`: Groups commands used for debugging
    - `SILENT <T|F>`: Sets whether to call top-level commands silently. Boolean `<T|F>` is optional and, if excluded, toggles the current silent value.
    - `MAX-RECUR <int>`: Changes the max recursion depth to `<int>`. This is relevant to files that read other files. `<int>` is optional and defaults to 10.
  - `# <string>`: Used to leave comments in the code
  - `EXIT`: Exits the program.

# General terminology
  - Command: One line, consisting of an instruction and any relevant parameters.
    - Example: **READ test.fira**
  - Instruction: The start of a command that specifies what it should do. Sometimes an instruction is broken into multiple parts across the command, such as in DEFWORD ... FROM ... .
    - Example: **DEFROOT** "Past Tense" "łem"
  - Parameter: Any changeable part of a command., i.e. anything other than the instruction
    - Example: DEFWORD **"Flame"** FROM **"r_Flame"** **END** **f**
  - Subcommand: A parameter that acts as another instruction that must be completed in order to complete the primary instruction of a command.
    - Example: DEFWORD "Flame" FROM "r_Flame" **END** **f**
