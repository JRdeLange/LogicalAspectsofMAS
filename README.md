# Kripke model generation for The Crew

This program simulates a simplified version of the game The Crew. During gameplay it keeps track of the common knowledge shared by the agents during the game. It also tracks which facts become common knowledge based on the common knowledge already revealed.

Using this the program can then warm any player when they should know that the current round can be won.

# How to run

1. Download mlsolver from https://github.com/erohkohl/mlsolver and follow the installation instructions (Alternatively, if unable to install mlsolver, move the "formula.py" file from the "emergency" folder to the "TheCrew" folder, and replace "from mlsolver.formula"(line 2) in "TheCrew.py" with "from formula")

2. Run "python TheCrewAlpha/TheCrewAlpha.py"
