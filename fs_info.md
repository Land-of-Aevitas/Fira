# Commands

## Defining Words
- `DEFROOT <wordEng> <wordFira> <params>`: Define a root word. `<wordEng>` is a string with the English word and `<wordFira>` is another string with it's Fira translation.
  - `GENDER <m|M|f|F|n|N|p|P>`: Adds a gendered ending to the word: `m` = Masculine, `f` = Feminine, `n` = Neutral, `p` = Plural. Use a capitalised letter to replace the last letter of the word instead of appending to it.
  - `NOTE <string>` Adds a note in the .db file next to this word's entry.
- `DEFWORD <wordEng1> FROM <wordEngs> <params>`: Define a complex (non-root) word using other words.
  - `WITH-<SLICE>`: By default, all consituents are appended to each other to form the new word. A `WITH-<>` command can be used to change the concatenation type. This must immediately follow the `DEF FROM`.
    - `WITH-SLICE <ints>`: Appends all words together, but additionally removes a number of characters from the start and end of each word as specified by the `<ints>`. The order of the ints is as follows: word1start word1end word2start word2end etc.
  - `GENDER <m|M|f|F|n|N|p|P>`: Adds a gendered ending to the word: `m` = Masculine, `f` = Feminine, `n` = Neutral, `p` = Plural. Use a capitalised letter to replace the last letter of the word instead of appending to it.
  - `NOTE <string>` Adds a note in the .db file next to this word's entry.

## Retrieving Words
- `LIST <regexString> <params>`: Lists all words that match the regex string.
  - `LANG <e|f>`: Only searches words in a certain language. `e` = English, `f` = Fira.
  - `TYPE <r|c>`: Only searches a secific table. `r` = Root word table, `c` = Complex word table.
  - `NOTE`: Prints any notes stored matching entries.
- `TRANSLATE <string> TO <f|e>`: Outputs the translation of a word to the specified language

## Other commands
  - `HELP`: Prints this page to the console.
  - `EXIT`: Exits the program.
  - `READ <file location>`: Reads the file at the specified address and executes it. It must be a .fira file!
  - `DEBUG <debug command>`: Groups commands used for debugging
    - `SILENT`: Toggles whether to call top-level commands silently.

# General terminology
  - Command: One line, consisting of an instruction and any relevant parameters.
    - Example: **READ test.fira**
  - Instruction: The start of a command that specifies what it should do. Sometimes an instruction is broken into multiple parts across the command, such as in DEFWORD ... FROM ... .
    - Example: **DEFROOT** "Past Tense" "łem"
  - Parameter: Any changeable part of a command.
    - Example: DEFWORD **"Flame"** FROM **"r_Flame"** **GENDER** **f**
  - Subcommand: A paramater that acts as another instruction that must be completed in order to somplete the primary instruction of a command.
    - Example: DEFWORD "Flame" FROM "r_Flame" **GENDER** **f**
