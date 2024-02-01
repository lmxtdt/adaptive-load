#compileData.R: takes all data from multiple simulations in multiple files,
#compiles it, and writes the data to two .csv files. It also adjusts how some
#of the simulation parameters are represented. for readability.

#VARIABLES TO ADJUST
#INPUT: paths to folders with simulation data
siPath <- "DataVaryN/SimInfo"  #path to SimInfo folder
gPath <- "DataVaryN/Gens"      #path to Gens folder
#OUTPUT: paths for output csv files
allGenPath <- "allGenerationsVaryN.csv"     #every simulated generation
finalGenPath <- "finalGenerationVaryN.csv"  #the final generation of each replicate
#END ADJUSTABLE VARIABLES

library(tidyverse)

#define a function that joins together all of the files in a folder
combineFiles <- function(folderPath, columnNames){
  #get list of all the csvs in the folder
  files <- list.files(folderPath, full.names = TRUE)
  
  #read the first csv in the list
  df <- read_csv(files[1], col_names = columnNames, 
                 show_col_types = FALSE)
  
  #read the rest and add them
  for (i in 2:length(files)) {
    df <- full_join(df,
                    read_csv(files[i], col_names = columnNames,
                             show_col_types = FALSE),
                    by = columnNames)
  }
  
  return(df)
}

#get all data from the sim info & generations folders
siCols <- c("replicate", "mutMod", "randPairs", "N",
            "selfR", "inD", "selecR", "genomeL", "numChr")
siDF <- combineFiles(siPath, siCols)

gCols <- c("replicate", "generation", "numMutsSim",
           "currN", "avgMutsPerInd", "avgMutFreq")
gDF <- combineFiles(gPath, gCols)

#adjust sim info columns to be more understandable
#randPairs is an integer representing pairs were random (1) or siblings (0)
#mutRate is calculated from genomeL and mutMod
randPairLabels <- c("sibling", "random")
siDF <- siDF %>% mutate(mutRate = (genomeL * 2 * mutMod) ^ -1,
                        pairType = randPairLabels[randPairs + 1])

#find the last generation for each replicate
gDF <- gDF %>% group_by(replicate) %>%
                mutate(maxGen = max(generation),
                       isMaxGen = (maxGen == generation))

#combine the two data frames
joinDF <- full_join(gDF, siDF, by = "replicate")

#create output data frames
outputCols <- c("replicate", "pairType", "mutRate", 
               "selecR", "inD", "selfR", "N",
               "generation", "numMutsSim", "currN", 
               "avgMutsPerInd", "avgMutFreq")
allGenDF <- joinDF[outputCols]

finalGenRows <- joinDF$isMaxGen
finalGenDF <- joinDF[finalGenRows, outputCols]

#write output
write_csv(allGenDF, allGenPath)
write_csv(finalGenDF, finalGenPath)
