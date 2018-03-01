#!/bin/sh

# Program to evaluate the algorithms changing the number of features
# Usage: ./evaluate.sh

# Adding trap in case of cancelling this script
trap "kill -15 -$$" SIGHUP SIGINT SIGQUIT SIGABRT SIGTERM

# Indicating this directory as root
cd $(dirname $0)

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

clf_types=(	"Polarity"
			"Sentiment")

clf_profiles=(	"subjectivity.json"
				"sentiment.json")

max_pct=10


############################# FUNCTIONS DECLARATION ############################
function print_progress() {
	algorithm=$1
	features_pct=$2

	# If it is the first call (0%) avoid the message
	if [ ${features_pct} != 1 ]; then
		completed=$(( (($features_pct-1) * ($max_pct+1)) ))
		total=$(( $completed * 100 / ($max_pct * ($max_pct+1) ) ))
		echo "$algorithm: $total%"
	fi
}


function algorithm_eval() {
	algorithm=$1
	output=$2

	echo "Starting $algorithm evaluation"
	echo "############# Evaluating $algorithm #############" >> ${output}

	# While the features percentage is lower than the max
	for ((features_pct = 1 ; features_pct <= $max_pct ; features_pct++)); do
		echo >> ${output}

		print_progress ${algorithm} ${features_pct}
		echo "	$features_pct% features" >> ${output}

		# For each classifier type (polarized VS sentiment)
		for ((i = 0 ; i < ${#clf_types[@]} ; i++)); do
			profile=${clf_profiles[$i]}
			score=$(python3 ../src/main.py train_model -a ${algorithm} \
													 -f ${features_pct} \
													 -l 'english' \
													 -o None \
													 -p ${profile})

			score=$(echo ${score} | cut -d " " -f 1)
			echo "		${clf_types[$i]}: $score" >> ${output}
		done
	done

	echo "$algorithm: 100%"
}


############################### EVALUATION START ###############################
for ((i = 0 ; i < ${#algorithms[@]} ; i++)); do
	algorithm_eval ${algorithms[$i]} ${eval_files[$i]} &
done

# Wait until the processes finish or they are killed
wait
