import pickle
from pathlib import Path
import pandas as pd


MODEL_PATH = Path(__file__).with_name("best_spam_classifier.pkl")


def main():
    spam_classifier = None

    with MODEL_PATH.open("rb") as model_file:
        spam_classifier = pickle.load(model_file)
    
    email_dic = {}
    email = ""

    # Choose either to read email content from user input or from a text file. Uncomment the desired option below.
    
    # Approach1: read email content from user input
    # email = input("Enter the email content to check if it's spam or not: ")


    # Approach2: read email content from a text file
    with open("sampleemail.txt", "r") as f:
        email = f.read()

    for word in email.split():
        if word in email_dic:
            email_dic[word] += 1
        else:
            email_dic[word] = 1

    sample = pd.DataFrame([email_dic])
    
    # sample = pd.DataFrame([{
    #         "the": 1,
    #         "to": 2,
    #         "free": 3,
    #         "win": 1,
    #         "winner": 1,
    #         "click": 2,
    #         "offer": 1,
    #         "money": 1,
    #         "urgent": 1,
    #         "hello": 1
    #     }])

    # load the features used during training
    feature_columns = pd.read_csv("dataset.csv").columns[1:-1]  # all columns except Email No. and Prediction

    # fill other feature columns with 0
    for col in feature_columns:
        if col not in sample.columns:
            sample[col] = 0

    # reorder columns exactly as trained
    sample = sample[feature_columns]

    prediction = spam_classifier.predict(sample)[0]
    # print("Prediction:", prediction)

    if isinstance(prediction, str):
        is_spam = prediction.strip().lower() in {"spam", "true", "yes", "1"}
    else:
        is_spam = bool(prediction)

    print("This email is spam." if is_spam else "This email is not spam.")


if __name__ == "__main__":
	main()
