#!/bin/sh

# Program to evaluate the algorithms changing the number of features
# Usage: ./Evaluate.sh

# Adding trap in case of cancelling this script
trap "kill -15 -$$" SIGHUP SIGINT SIGQUIT SIGABRT SIGTERM

# Security flags
set -e
set -u
stty -echoctl


############################## VARIABLE DECLARATION ############################
algorithms=("Logistic-Regression"
			"Naive-Bayes"
			"Linear-SVC"
			"Random-Forest")

eval_files=("LR_eval.txt"
			"NB_eval.txt"
			"SVM_eval.txt"
			"RF_eval.txt")

cls_types=(	"Polarity"
			"Sentiment")

cls_files=(	"Neutral.txt Polarized.txt"
			"Positive.txt Negative.txt")

folder="Evaluations"
max_pct=5


############################## CREATING THE FOLDER #############################
rm -rf $folder
mkdir $folder


############################# FUNCTIONS DECLARATION ############################
function print_progress() {
	algorithm=$1
	words_pct=$2
	bigrams_pct=$3

	# If it is the first call (0%) avoid the message
	if [ $words_pct != 1 ] || [ $bigrams_pct != 0 ]; then
		let "completed = (($words_pct-1) * $max_pct) + $bigrams_pct"
		let "total = $completed * 100 / ($max_pct * ($max_pct+1))"
		echo "$algorithm: $total%"
	fi
}


function algorithm_eval() {
	algorithm=$1
	output=$folder/$2

	echo "Starting $algorithm evaluation"
	echo "############# Evaluating $algorithm #############" >> $output

	# While word percentage is lower than the max
	for ((words_pct = 1 ; words_pct <= $max_pct ; words_pct++)); do
		echo >> $output

		# While bigram percentage is lower than the max
		for ((bigrams_pct = 0 ; bigrams_pct <= $max_pct ; bigrams_pct++)); do
			print_progress $algorithm $words_pct $bigrams_pct
			echo "	$words_pct% words | $bigrams_pct% bigrams" >> $output

			# For each classifier type (polarized VS sentiment)
			for ((i = 0 ; i < ${#cls_types[@]} ; i++)); do
				files=${cls_files[$i]}
				score=$(python3 Parser.py Train $algorithm \
												$files \
												$words_pct \
												$bigrams_pct \
												None)

				score=$(echo $score | cut -d" " -f 6)
				echo "		${cls_types[$i]}: $score" >> $output
			done

			echo >> $output
		done
	done
}


############################### EVALUATION START ###############################
for ((i = 0 ; i < ${#algorithms[@]} ; i++)); do
	algorithm_eval ${algorithms[$i]} ${eval_files[$i]} &
done

# Wait until the processes finish or they are killed
wait
