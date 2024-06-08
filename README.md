# The software for the electro-vibration display (FeelSurf)
This repository contains all the code files for the experiment where we aimed to explore whether adding an image of the texture on the electro-vibration display can improve the perceived realism of virtual textures on an electro-vibration display.

## User interface
The main code for the user interface is in the file 'ui_classes.py'. The user interface automates filling in the conditions, textures, and scores for the participants. In this way, we only had to fill in the score and click next. The user interface can also be used to calibrate the textrure per participant however the code for actually rendering the textures on the NiMax would often throw an out of range error. 

## Randomizer
The randomizer automatically makes a list of an order of textures per condition per participant and saves it in 'order.csv'. (The 'order.csv' in the repo is the one used in our experiment)

## Data
The raw data of the participant was saved in the folder data. The data is combined with the file 'combine_data.ipynb' and saved in the file 'all_data.csv'. After that we used the data in SPSS for the analysis and in 'generate_stacked_barchart.ipynb' to create the plot of the data.
