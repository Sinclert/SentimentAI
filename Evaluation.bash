#!/bin/bash

############################## VARIABLE DECLARATION ############################
algorithms=("Logistic-Regression"
			"Naive-Bayes"
			"Linear-SVC"
			"Random-Forest")

train_files=("Neutral.txt Polarized.txt"
			"Positive.txt Negative.txt")

cls_types=(	"Polarity"
			"Sentiment")

output_file="evaluation.txt"
max_pct=5


############################## CREATING OUTPUT FILE ############################
echo "Creating evaluation file..."
rm $output_file 2>/dev/null
touch $output_file


############################## PERFORMING EVALUATION ###########################
echo "Starting algorithms evaluation..."
echo

# Loop through the list of algorithms
for alg in ${algorithms[@]}; do
	echo "Evaluating $alg"
	echo "Evaluating $alg" >> evaluation.txt

	# While word percentage is lower than the max
	for ((words_pct=1 ; words_pct<=$max_pct ; words_pct++)); do

		# While bigram percentage is lower than the max
		for ((bigrams_pct=0 ; bigrams_pct<=$max_pct ; bigrams_pct++)); do
			echo "	$words_pct% words | $bigrams_pct% bigrams"
			echo "	$words_pct% words | $bigrams_pct% bigrams" >> $output_file

			# For each classifier type (polarized VS sentiment)
			for ((i=0 ; i<${#cls_types[@]} ; i++)); do
				files=${train_files[$i]}
				output=$(python3 Parser.py Train 	$alg \
													$files \
													$words_pct \
													$bigrams_pct \
													None)

				score=$(echo $output | cut -d" " -f 6)
				echo "		${cls_types[$i]}: $score"
				echo "		${cls_types[$i]}: $score" >> $output_file
			done
		done
	done

	echo
	echo >> $output_file
done
