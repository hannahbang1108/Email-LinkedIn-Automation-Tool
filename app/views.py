# Library to access the Flask application instance 'app' from the 'app' module
from app import app
# Library to handle incoming HTTP requests from the Flask library
from flask import render_template, request
# Class to send out emails automatically
from Sales import Sales
# Library to interact with the operating system
import os       
# Library for data manipulation and analysis        
import pandas as pd

# Creates variable to serve as container for name of directory where files will be stored
UPLOAD_FOLDER = 'uploads'
# Assigns value to 'UPLOAD_FOLDER' within the application's configuration object
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Creates global variable to store Sales object
sales = None


# Renders the 'upload.html' template when the user navigates to the root URL
@app.route('/')
def index():
    return render_template('upload.html')

# Defines a route for deleting a specific person based on their first and last name
@app.route('/person-deleted', methods=['GET', 'POST'])
def delete_client():
    # Retrieves the first name of the person to be removed from the submitted form data
    first_name = request.form['firstname']
    # Retrieves the last name of the person to be removed ' from the submitted form data
    last_name = request.form['lastname']
    # Retrieves the file path to where the person is stored from the submitted form data
    path = request.form['path']
    # Iterates over each file in the specified directory path
    for file in os.listdir(path):
        # Read the excel file into a pandas DataFrame
        df = pd.read_csv(path + "\\" + file)
        # Filter out rows where the specified column matches the value to delete
        # Iterates through the rows of the 'First Name' column
        for i in range(len(df['First Name'])):
            # Checks if the first and last names match the submitted form data
            if first_name == df['First Name'][i] and last_name == df['Last Name'][i]:
                # Drops the row with the matching index.
                df = df.drop(i)
                # Reset the index after dropping the row
                # Resets the DataFrame index to ensure it's sequential
                df = df.reset_index(drop=True)
                # Writes the updated DataFrame back to the CSV file without the index
                df.to_csv(path + "\\" + file,index=False)
                # Returns a success message.
                return "Successfully removed client!"
    # Returns a failure message if the client is not found after iterating through all files
    return "Couldn't find client"

# Defines a route for deleting all people from a specific company
@app.route('/company-deleted', methods=['GET', 'POST'])
def delete_company():
    # Retrieves the name of the company to be removed from the submitted form data
    company_name = request.form['companyname']
    # Retrieves the file path where people from the company are stored from the submitted form data
    path = request.form['path']
    # Iterates over each file in the specified directory path
    for file in os.listdir(path):
        # Read the excel file into a pandas DataFrame
        df = pd.read_csv(path + "\\" + file)
        # Filter out rows where the specified column matches the value to delete
        # Declares 'ind' as a global variable.
        global ind
        # Initializes the index variable 'ind' to 0
        ind = 0
        # Iterates through the rows of the 'Company' column
        for i in range(len(df['Company'])):
            # Checks if the company name at the current index matches the submitted form data
            if company_name == df['Company'][ind]:
                # Drops the row with the matching index
                df = df.drop(ind)
                # Reset the index after dropping the row
                # Resets the DataFrame index to ensure it's sequential
                df = df.reset_index(drop=True)
                # Writes the updated DataFrame back to the CSV file without the index
                df.to_csv(path + "\\" + file,index=False)
                # Decrements the index to account for the dropped row
                ind -= 1
            # Increments the index for the next iteration
            ind += 1
    # Returns a success message after all matching entries have been processed
    return f"Removed all people from {company_name}!"

# Defines a route to store the user's information to create a valid email signature and store csv file containing contacts
@app.route('/action', methods = ['POST'])
def action():
    # Retrieves the first name from the submitted form data
    first_name = request.form['firstname']
    # Retrieves the last name from the submitted form data
    last_name = request.form['lastname']
    # Retrieves the email from the submitted form data
    email = request.form['email']
    # Retrieves the role from the submitted form data (i.e, data scientist, software engineer, or founder)
    role = request.form['role']
    # Retrieves the phone # from the submitted form data
    mobile = request.form['phone']
    # Retrieves the list of uploaded files with the name upload
    csv = request.files.getlist('upload')
    # Declares 'sales' as a global variable.
    global sales
    # Creates an instance of the 'Sales' class with the form data and uploaded files
    sales = Sales(first_name, last_name, email, role, mobile, csv)
    # Renders the 'action.html' template
    return render_template('action.html')

# Defines a route to handle email sending
@app.route('/email-sent', methods = ['POST'])
def email_sent():
    # Retrieves the subject from the submitted form data
    subject = request.form['subject']
    # Retrieves the message from the submitted form data
    body_text = request.form['message']
    # Assigns the subject to the 'sales' object
    sales.subject = subject
    # Assigns the body text to the 'sales' object
    sales.body_text = body_text
    # Calls the 'send_email' method of the 'sales' object
    sales.send_email()
    # Returns a success message.
    return "Successfully sent all emails!"

# Defines a route to handle LinkedIn outreach
@app.route('/linkedin-outreach', methods=['GET', 'POST'])
def linkedin_outreach():
    # Retrieves the linkedin_message from the submitted form data
    linkedin_text = request.form['linkedin_message']
    # Assigns the LinkedIn message to the 'sales' object
    sales.linkedin_text = linkedin_text
    # Calls the 'linkedin_list' method of the 'sales' object
    sales.linkedin_list()
    # Renders the 'linkedin_outreach.html' template
    return render_template('linkedin_outreach.html')