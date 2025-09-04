# Introduction
This is my implementation of the AST interpreter from (the first half of) Robert Nystrom's book "Crafting Interpreters". While I've largely stuck to Nystrom's own implementation details and structure, I've altered some parts of the interpreter structure (including minor parts of the language specification) and added a number of useful (in my opinion, anyway) features.
I've include a brief list below of the implementation's basic features which can be found in Nystrom's original Java implementation, followed by a more detailed list of my own changes or additions to the interpreter.
### Note
Due to the constantly changing nature of this project, there may be some changes which I have (unfortunately) missed within this documentation. I will certainly try to make sure that doesn't happen, but my efforts in this regard will likely be imperfect. This document will be duly updated if any changes do come to mind which have been left out.

# Regular Features of plox
* 

# Personal Modifications to plox
This a brief list of the changes I've made to the language, including additions and modifications. They're not in any particular order.
For a more detailed list with justification (brief or lengthy) for each change, please go to [Justification](./Justification.md).
* Added scoped file imports.
* Improved error messages with aesthetic display of error locations (for running files).
* Added user-defined exceptions (errors and warnings).

# Brief Q&A
This section will hopefully address some shorter questions regarding more significant design choices or simple inquiries concerning the interpreter and project as a whole.

### Are there any bugs in this implementation?
Possibly a few. I've tried my best to weed them all out with (hopefully) good solutions. If you do find any issues that I've missed, feel free to make an issue or pull request and I'll be happy to look at it. Feel free to also make non-bug-related suggestions on the implementation, which I might consider merging.

# Further Information
...