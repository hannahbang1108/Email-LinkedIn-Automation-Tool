# library to run the app
from app import app
# Import the function from the library
from dotenv import load_dotenv

# Call the function to load environment variables from the .env file
load_dotenv()

#runs the app
if __name__ == '__main__':

    app.run()
