from flask import Flask, render_template, flash, request, redirect, url_for
import math
import re

app = Flask(__name__)

#function to calculate cracking time using brute force
def calculate_time_to_crack(password, guesses_per_second=1000000000):
    # Assuming a brute-force attack and using a basic estimation formula
    # Adjust guesses_per_second based on the attacker's hardware capabilities

    # Number of possible characters in a password (assuming alphanumeric)
    possible_characters = 62  # 26 letters (uppercase and lowercase) + 10 digits
    entropy_mulplier = 1 # used to mutiply the entropy based on character being more than 8, special characters, Upper case characters numeric character
	
	# Special Character
    specialMatch = re.search(r'([^a-zA-Z0-9]+)', password, re.M)

	# More than 8 characters
    lenMin = False
    if len(password) > 8:
        lenMin = True
	# Uppercase Character
    ucMatch = re.search(r'([A-Z])', password, re.M)
    
	#numeric character
    numMatch = re.search(r'([0-9])', password, re.M)

    if lenMin:
        entropy_mulplier = 1
    if specialMatch and ucMatch and numMatch:
        entropy_mulplier = 1.5

    if ucMatch and numMatch:
        entropy_mulplier = 1
    if specialMatch and numMatch:
        entropy_mulplier = 1.5
    if specialMatch and ucMatch:
        entropy_mulplier = 1.5

    # Calculate the entropy of the password
    entropy = math.log2(possible_characters) * len(password) * entropy_mulplier

    # Calculate the number of guesses needed for a brute-force attack
    total_guesses = 0.5 * 2**entropy

    # Calculate the time to crack in seconds
    time_to_crack_seconds = total_guesses / guesses_per_second

    return time_to_crack_seconds

def second_conversions(secs):
	if secs < 60:
		time = str(secs) + " seconds"
		return time
	else:
		time_min = secs/60
		if time_min < 60:
			seconds = secs % 60
			time = str(int(time_min)) + " minutes and " + str(seconds) + " seconds"
			return time
		else:
			time_hrs = int(time_min)/60
			if time_hrs < 24:
				minutes = int(time_min) % 60
				time =str(int(time_hrs)) + " hours and " + str(minutes) + " minutes"
				return time
			else:
				time_days = time_hrs/24
				if time_days < 7:
					hours = int(time_hrs) % 24
					time = str(int(time_days)) + " days and " + str(hours) + " hours"
					return time
				else:
					weeks = time_days/7
					if weeks < 4:
						dayss = int(time_days) % 7
						time = str(int(weeks)) + " weeks and " + str(dayss) + " days"
						return time
					else:
						months = weeks/4
						if months < 12:
							weekss = int(weeks) % 4
							time = str(int(months)) + " months and " + str(weekss) + " weeks"
							return time
						else:
							years = months/12
							monthss = int(months) % 12
							time = str(int(years))+" years and " + str(monthss) + " months"
							return time
print(second_conversions(3880))

@app.route('/')
def homepage():
    return render_template("index.html")

@app.route('/main/', methods = ["GET", "POST"])
def mainPage():
	if request.method == "POST":
		enteredPassword = request.form['password']


		from sklearn import svm


		with open('test.txt','w') as test:
			testData = str(enteredPassword) + '|' + str(2)
			test.write(testData)

		# Returns feature & label arrays [ feature, label ]
		def parseData(data):
			features = list()
			labels = list()
			passwords = list()

			with open(data) as f:
				for line in f:
					if line != "":

						both = line.replace('\n', '').split("|")
						password = both[0]
						label = both[1]

						feature = [0,0,0,0,0]

						# FEATURES
						lenMin = False; # more than 8 chars
						specChar = False # special character
						ucChar = False # uppercase character
						numChar = False # numeric character

						# More than 8 characters
						if len(password) > 8:
							lenMin = True

						# Special Character
						specialMatch = re.search(r'([^a-zA-Z0-9]+)', password, re.M)
						if specialMatch:
							specChar = True

						# Uppercase Character
						ucMatch = re.search(r'([A-Z])', password, re.M)
						if ucMatch:
							ucChar = True

						# Numeric Character
						numMatch = re.search(r'([0-9])', password, re.M)
						if numMatch:
							numChar = True

						# Create rules
						if lenMin:
							feature[0] = 1

						if specChar and ucChar and numChar:
							feature[1] = 3

						if ucChar and numChar:
							feature[2] = 1

						if specChar and numChar:
							feature[3] = 2

						if specChar and ucChar:
							feature[4] = 2

						features.append(feature)
						labels.append(int(label))
						passwords.append(password)

			return [features,  labels, passwords]


		# Prepare the data
		trainingData = parseData( 'training.txt' )
		testingData = parseData( 'test.txt' )

		#A SVM Classifier
		clf = svm.SVC(kernel='linear', C = 1.0)

		#Training the classifier with the passwords and their labels.
		clf = clf.fit(trainingData[0], trainingData[1])

		#Predicting a password Strength
		prediction = clf.predict(testingData[0])

		target = len(testingData[1])
		current = 0
		incorrect = 0
		for index in range(target):
				if(prediction[index] == 0):
					predicted = "Very Weak Password"
					time_to_crac = calculate_time_to_crack(enteredPassword)
					time_to_crack = second_conversions(time_to_crac)
				elif(prediction[index] == 1):
					predicted = "Weak Password"
					time_to_crac = calculate_time_to_crack(enteredPassword)
					time_to_crack = second_conversions(time_to_crac)
				elif(prediction[index] == 2):
					predicted = "Strong Password"
					time_to_crac = calculate_time_to_crack(enteredPassword)
					time_to_crack = second_conversions(time_to_crac)
				elif(prediction[index] == 3):
					predicted = "Very Strong Password"
					time_to_crac = calculate_time_to_crack(enteredPassword)
					time_to_crack = second_conversions(time_to_crac)
	return render_template("main.html", predicted = predicted, target = len(trainingData[1]), time_to_crack = time_to_crack)


if __name__ == "__main__":
    app.run(debug=True)
