#makeReps-VaryN.py: generates SLURM job scripts to run all of the simulations
#that vary N and a limited number of other parameters.
#each job script simulates a number of replicates for a specific parameter set.

file = """#!/bin/bash -l
#SBATCH --time=96:00:00
#SBATCH --ntasks=1
#SBATCH --mem=4g
#SBATCH --mail-type=END  
#SBATCH --output={abbr}{num}.out
#SBATCH --error={abbr}{num}.err

cd ~/load || exit

((rep = {rep}))

for j in {{1..{jmax}}}
    do ~/build/slim -d "replicate = $rep" \\
                    -d "N = {N}" \\
                    -d "randPairs = {randPairs}" \\
                    -d "mutMod = {mutMod}" \\
                    -d "selecR = {selecR}" \\
                    -d "selfR = {selfR}" \\
                    -d "inD = {inD}" \\
                    -d "simInfoOut = '{simInfoOut}'" \\
                    -d "generationsOut = '{gensOut}'" \\
                    -d "finalOut = '{finalOut}'" \\
                    SlimScripts/adaptiveLoad10k.slim || exit
    ((rep += 1))
done
"""

abbr = "repsVN" #prefix to job script file names
jmax = 5 #number of simulation replicates to run per job file

r = 1 #replicate number to start at
num = 1 #file number to start at

#fixed simulation parameters
mutMod = 100 #mutation rate modifier
inD = 1 #inbreeding depression

#iterate over simulation parameters of interest
for randPairs in [0, 1]: #sibling vs random pairs
    for N in [100, 500, 1000, 5000]: #population carrying capacity
        for selfR in [0.1, 0.2, 0.3]: #selfing rate
            for selecR in [-(x+1) / 5 for x in range(5)]:
                #format number for this file
                numFormatted = "{:03}".format(num)
                
                #define output paths
                simInfoOut = "DataVaryN/SimInfo/si_{}.csv".format(numFormatted)
                gensOut = "DataVaryN/Gens/g_{}.csv".format(numFormatted)
                finalOut = "DataVaryN/Final/f_{}.csv".format(numFormatted)

                #create job file with parameters 
                contents = file.format(abbr = abbr,
                                       num = numFormatted,
                                       jmax = jmax,
                                       rep = r,
                                       N = N,
                                       randPairs = randPairs,
                                       mutMod = mutMod,
                                       selecR = selecR,
                                       selfR = selfR,
                                       inD = inD,
                                       simInfoOut = simInfoOut,
                                       gensOut = gensOut,
                                       finalOut = finalOut)

                #write job file
                with open("{}{}.sh".format(abbr, numFormatted), "w") as fn:
                    fn.write(contents)

                #increment replicate numbering & file numbering
                r += jmax
                num += 1

print(r) #1351
print(num) #271
