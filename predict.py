import joblib
from format.messageform import InputForm

class APIService:
    def predict(userInput: InputForm):
        try:
            # model = joblib.load('models/heart_disease_classification_model.pkl') # Load the model

            model = joblib.load('models/Random_Forest.pkl') # Load the model
            

            features = [
                userInput.Age,
                userInput.Sex,
                userInput.ChestPainType,
                userInput.RestingBP,
                userInput.Cholesterol,
                userInput.FastingBS,
                userInput.RestingECG,
                userInput.MaxHR,
                userInput.ExerciseAngina,
                userInput.Oldpeak,
                userInput.ST_Slope,
                userInput.NumMajorVessels,
                userInput.Thal
            ]
            
            prediction = model.predict([features])[0]
            
            # if prediction == 0:
            #     return False
            # else:
            #     return True

            # return prediction == 0 ? False : True

            return False if prediction == 0 else True

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise e
            
        

