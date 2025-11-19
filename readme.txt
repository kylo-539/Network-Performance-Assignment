Appendix A in the report details each file used in the report and Appendix B names each image used for all questions. 

For question A, the code can be run by executing the scripts "QuestionA-Part1.py" and "QuestionA-Part2.py"
These will execute providing the folder "QuestionA" is in the same directory as the scripts are being run from.
The folder contains all the scripts used for the analysis done as part of Question A - the naming of the scripts was changed for part 2.
Part 2's files all have the designated bit rate in the title, e.g. "DataOfUser1-1759410141-1000kbps-.sca"
Part 1's file is the default file in this folder - indicating all the parameters are default.
A CSV has been provided with all the results from the files collated IF the corrector wishes to do the analysis in Excel,
however, the provided python files will reproduce all the analysis and figures used in the report.

Question B follows a similar format, however, there is a crucial distinction between Q. A and Q. B - for question B 
there are 2 folders with different files. Question B had several problems with respect to connectivity after 50m, "QuestionB-Original-Sim"
contains the files that highlight these issues and all the images included in this folder support the claims made in the report.
QuestionB-Altered-Sim contains all the files used for the actual analysis done on key performance metrics vs distance. This 
folder has several images in it that are unused in the final report but were used for design decisions, such as changing the
bit rate to produce more realistic scenarios. A CSV of these results has also been included in this folder. 

Question C's files for WiFi 6 can be found inside the folder QuestionC -> "QuestionC/Wifi6/". This folder solely contains
the files used for WiFi6 analysis. Subsequently, the subfolder "Wifi7" contains all the files used for the WiFi7 analysis.
The main folder, "QuestionC", contains the CSV produced, alongside all the images used in the report. 

During the installation of NS3, there were several issues that had to be addressed before the examples would work properly.
The changes to all these files were made to the .cc file and .h files located in the folder "NS3-Fix". The folder is named this 
so I could easily distinguish between the file I was currently altering vs the files I was overwriting within the NS3 environment.
This was necessary as I was copy and pasting the changed file, "wifi-example-sim-updated.cc", into the folder in NS3 in Ubuntu. 
This was done from File Explorer so I wanted to maintain clarity between tabs, especially for a project that spanned mutliple
weeks. 

The code has also been added to a repository on GitHub, url:  