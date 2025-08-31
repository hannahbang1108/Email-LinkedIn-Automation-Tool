# Library for data manipulation and analysis
import pandas as pd
# Library for interacting with the file system
import os.path
# Library for encoding binary data into a URL-safe format
import base64
# Library for constructing email messages
from email.message import EmailMessage
# Class to create text-based email parts
from email.mime.text import MIMEText
# Library to make requests to Google's API
from google.auth.transport.requests import Request
# Library to manage user authentication and authorization
from google.oauth2.credentials import Credentials
# Library to handle the OAuth 2.0 authorization flow for desktop apps
from google_auth_oauthlib.flow import InstalledAppFlow
# Library to create a service object for the Gmail API
from googleapiclient.discovery import build
# Library to handle errors from Google's API
from googleapiclient.errors import HttpError
# Library to sanitize filenames for security
from werkzeug.utils import secure_filename
# Library for common string operations
import string
# Library to add delays to the code execution
import time

# Defines the list of authorization scopes required to access the user's Gmail account
SCOPES = ["https://mail.google.com/", "https://www.googleapis.com/auth/gmail.settings.sharing", "https://www.googleapis.com/auth/gmail.settings.basic"]

# Defines the Sales class to manage contact-related actions
class Sales:
    # Initializes the Sales object with personal and contact data
    def __init__(self, first_name, last_name, email, role, mobile, csv, subject=None, body_text=None,linkedin_text=None):
        # Stores the first name of the sender
        self.first_name = first_name
        # Stores the last name of the sender
        self.last_name = last_name
        # Stores the email of the sender
        self.email = email
        # Stores the role of the sender
        self.role = role 
        # Stores the mobile number of the sender
        self.mobile = mobile
        # Stores the list of uploaded CSV files containing contacts
        self.contacts = csv
        # Stores the subject line for the email
        self.subject = subject
        # Stores the body text for the email
        self.body_text = body_text
        # Stores the LinkedIn message text
        self.linkedin_text = linkedin_text

    # Reads the CSV file, authenticates with Gmail, and sends emails to each contact
    def send_email(self):
        """
        Reads in CSV file containing sales contacts and sends appropriate email to each
        """
        # Initializes the credentials variable to None
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time
        # Checks if the token.json file exists
        if os.path.exists("token.json"):
            # Loads credentials from the token.json file
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in
        # Checks if credentials are not valid or not present
        if not creds or not creds.valid:
            # If credentials are expired and a refresh token exists, refreshes them
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            # Otherwise, initiates the authorization flow to get new credentials
            else:
                # Creates an InstalledAppFlow object from the client secrets file
                flow = InstalledAppFlow.from_client_secrets_file(
                    os.environ.get('GOOGLE_CREDENTIALS_PATH'), SCOPES
                )
                # Runs the local server to handle the authentication redirect and get credentials
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            # Writes the new credentials to the token.json file for future use
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        # Starts a try-except block to handle potential API errors
        try:
            # Iterates through each uploaded contact file
            for file in self.contacts:
                # Declares 'service' as a global variable
                global service
                # Builds a Gmail API service object using the authenticated credentials
                service = build("gmail", "v1", credentials=creds)
                # Opens the contact CSV file
                contacts_file = open(os.environ('CONTACTS_CSV_PATH') + "\\" + {file.filename})
                # Reads the CSV file into a pandas DataFrame
                df = pd.read_csv(contacts_file)
                # Extracts the 'Email' column and converts it to a list
                emails = df['Email'].tolist()
                # Generates the email signature
                signature = self.create_signature()

                # Iterates through the list of email addresses
                for i in range(len(emails)):
                    # Creates the personalized email body
                    body = self.create_body(df, i)
                    # Creates the personalized email subject
                    subject = self.create_subject(df, i)
                    # Creates a MIMEText message object with the body and signature in HTML format
                    message = MIMEText(f"<!DOCTYPE html>\n<html>\n<body>\n" + body + signature + "\n</body<\n</html>", "html")

                    # Sets the 'From' header of the email.
                    message["From"] = self.email
                    # Sets the 'To' header of the email.
                    message["To"] = emails[i]
                    # Sets the 'Subject' header of the email.
                    message["Subject"] = subject

                    # encoded message
                    # Encodes the email message into a URL-safe base64 string.
                    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

                    # Creates a dictionary with the encoded message for the API call
                    create_message = {"raw": encoded_message}
                    # Sends the message using the Gmail API
                    send_message = (
                        service.users()
                        .messages()
                        .send(userId="me", body=create_message)
                        .execute()
                    )
                    # Pauses for 10 seconds to avoid hitting API rate limits
                    time.sleep(10)
        # Catches and prints any HttpError that occurs during the API call
        except HttpError as error:
            print(f"An error occurred: {error}")
            # Sets send_message to None in case of an error
            send_message = None
        # Returns the result of the last send message API call
        return send_message

    # Creates the personalized email body by replacing placeholders with data from the DataFrame
    def create_body(self, df, i):
        # Initializes an empty string to store the formatted body
        body = ""
        # Splits the body text into a list of lines
        lines = self.body_text.splitlines()
        # Iterates through all lines except the last one
        for x in range(len(lines)-1):
            # Gets the current line
            line = lines[x]
            # Skips the line if it is empty
            if line == "":
                continue
            # Adds a starting HTML paragraph tag to the line
            new_line = "<p>" + line
            # Continues replacing placeholders as long as a '{' is found
            while("{" in new_line):
                # Extracts the column name from inside the curly braces
                column_name = new_line[new_line.index("{")+1: new_line.index("}")]
                # Replaces the placeholder with the corresponding data, formatted with title case
                new_line = new_line.replace(new_line[new_line.index("{"): new_line.index("}")+1], df[column_name][i].lower().title())
            # If the current line is the second to last line, appends the last line with a line break
            if x == len(lines) - 2:
                new_line += f"<br>{lines[-1]}"
            # Adds a closing HTML paragraph tag and a newline character
            new_line += "</p>\n"
            # Appends the new line to the body string
            body += new_line
        # Returns the complete, formatted body string
        return body

    # Creates the personalized email subject by replacing placeholders with data from the DataFrame
    def create_subject(self, df, i):
        # Creates a copy of the subject string
        new_subject = self.subject
        # Continues replacing placeholders as long as a '{' is found
        while("{" in new_subject):
            # Extracts the column name from inside the curly braces
            column_name = new_subject[new_subject.index("{")+1: new_subject.index("}")]
            # Replaces the placeholder with the corresponding data, formatted with title case
            new_subject = new_subject.replace(new_subject[new_subject.index("{"): new_subject.index("}")+1], df[column_name].tolist()[i].lower().title())
        # Returns the complete, personalized subject string
        return new_subject

    # This function creates the email signature from user input and returns it in html format
    # The reasoning was because the message was formatted strangely if it wasn't in html
    def create_signature(self):
        # Formats the mobile number into a standard format
        formatted_mobile = f"({self.mobile[:3]}) {self.mobile[3:6]}-{self.mobile[6:]}"
        # Concatenates the first and last name to form the full name
        full_name = self.first_name + " " + self.last_name
        # Checks if the role is "Founder" to format the title differently
        if self.role == "Founder":
            # Returns the HTML signature for a "Founder" role
            return f"<p><b>{full_name}</b><br>{self.role} of Company Name<br>Company Addrress<br>Company City and State<br>Mobile: {formatted_mobile}<br>Website: <a href=\"www.company.com\">company url</a></p>"
        # Returns the HTML signature for all other roles
        return f"<p><b>{full_name}</b><br>{self.role} at Company Name<br>Company Address<br>Company City and State<br>Mobile: {formatted_mobile}<br>Website: <a href=\"www.company.com\">company url</a></p>"

    # Generates a list of LinkedIn URLs with personalized messages that can be copied
    def linkedin_list(self):
        # Initializes a counter for the LinkedIn links
        link_num = 1
        # Defines a string containing all allowed characters for the message
        all_alphanumeric = string.ascii_letters + string.digits + " " + "\"\'?!,[]@#$%^&*." # Contains all letters and numbers
        # Opens the HTML template file in write mode to create the list
        with open(os.environ.get('LINKEDIN_OUTREACH_PATH'),"w") as f:
            # Writes the starting HTML ordered list tag
            f.write("<ol class=\"formbold-form-input\">\n")
            # Iterates through each uploaded contact file
            for file in self.contacts:
                # Opens the current contact file, ignoring encoding errors
                file = open(os.environ('CONTACTS_CSV_PATH') + "\\" + {file.filename},errors="ignore")
                # Reads the CSV file into a pandas DataFrame
                df = pd.read_csv(file)
                # Extracts the 'Person Linkedin Url' column and converts it to a list
                linkedln_urls = df['Person Linkedin Url'].tolist()
                # Initializes an empty string to store the list of links
                linkedin_list = ""
                # Iterates through the list of LinkedIn URLs
                for i in range(len(linkedln_urls)):
                    # Initializes an empty string for the personalized message
                    message = ""
                    # Iterates through each line of the provided LinkedIn text
                    for line in self.linkedin_text.splitlines():
                        # Skips the line if it is empty
                        if line == "":
                            continue
                        # Continues replacing placeholders as long as a '{' is found
                        while "{" in line:
                            # Extracts the column name from inside the curly braces
                            column_name = line[line.index("{")+1: line.index("}")]
                            # Gets the value from the DataFrame for the current column and row
                            val = df[column_name].tolist()[i]
                            # Replaces the placeholder with the value
                            line = line.replace(line[line.index("{"): line.index("}")+1], val)
                        # Iterates through each character in the line to clean it
                        for char in line:
                            # If a '/' is found, truncates the line at that point
                            if char == "/":
                                line = line[:line.index(char)]
                                break
                            # If the character is not alphanumeric, removes it
                            if char not in all_alphanumeric:
                                line = line.replace(char, "")
                        # Adds a new line character after each line
                        line += "\n\n"
                        # Appends the formatted line to the message string
                        message += line
                    # Replaces smart quotes with standard single quotes
                    message = message.replace("’","\'")
                    # Replaces single quotes with a different single quote for consistency
                    message = message.replace("'","\'")
                    # Creates an HTML list item with a link that copies the message to the clipboard on click
                    linkedin_list += f"<li><a href=\"{linkedln_urls[i]}\" onclick = \"navigator.clipboard.writeText(`{message}`)\" target=\"_blank\">Link {link_num}</a></li>\n"
                    # Increments the link counter
                    link_num += 1
                # Writes the generated list of links to the HTML file
                f.write(linkedin_list)
            # Adds the closing ordered list tag
            linkedin_list += "</ol>\n"
            # Writes a block of CSS to style the generated HTML
            # CSS pulled from a template on Formbold: https://formbold.com/templates
            # All credit for this section of styling goes to them
            f.write("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    }
    
    body {
    font-family: 'Inter', sans-serif;
    }
    
    .formbold-mb-3 {
    margin-bottom: 15px;
    }
    
    .formbold-main-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 48px;
    }
    
    .formbold-form-wrapper {
    margin: 0 auto;
    max-width: 570px;
    width: 100%;
    background: white;
    padding: 40px;
    }
    
    .formbold-img {
    display: block;
    margin: 0 auto 45px;
    }
    
    .formbold-input-wrapp>div {
    display: flex;
    gap: 20px;
    }
    
    .formbold-input-flex {
    display: flex;
    gap: 20px;
    margin-bottom: 15px;
    }
    
    .formbold-input-flex>div {
    width: 50%;
    }
    
    .formbold-form-input {
    width: 100%;
    padding: 13px 22px;
    border-radius: 5px;
    border: 1px solid #dde3ec;
    background: #ffffff;
    font-weight: 500;
    font-size: 16px;
    color: #536387;
    outline: none;
    resize: none;
    }
    
    .formbold-form-input::placeholder,
    select.formbold-form-input,
    .formbold-form-input[type='date']::-webkit-datetime-edit-text,
    .formbold-form-input[type='date']::-webkit-datetime-edit-month-field,
    .formbold-form-input[type='date']::-webkit-datetime-edit-day-field,
    .formbold-form-input[type='date']::-webkit-datetime-edit-year-field {
    color: rgba(83, 99, 135, 0.5);
    }
    
    .formbold-form-input:focus {
    border-color: #6a64f1;
    box-shadow: 0px 3px 8px rgba(0, 0, 0, 0.05);
    }
    
    .formbold-form-label {
    color: #07074D;
    font-weight: 500;
    font-size: 14px;
    line-height: 24px;
    display: block;
    margin-bottom: 10px;
    }
    
    .formbold-form-file-flex {
    display: flex;
    align-items: center;
    gap: 20px;
    }
    
    .formbold-form-file-flex .formbold-form-label {
    margin-bottom: 0;
    }
    
    .formbold-form-file {
    font-size: 14px;
    line-height: 24px;
    color: #536387;
    }
    
    .formbold-form-file::-webkit-file-upload-button {
    display: none;
    }
    
    .formbold-form-file:before {
    content: 'Upload file';
    display: inline-block;
    background: #EEEEEE;
    border: 0.5px solid #FBFBFB;
    box-shadow: inset 0px 0px 2px rgba(0, 0, 0, 0.25);
    border-radius: 3px;
    padding: 3px 12px;
    outline: none;
    white-space: nowrap;
    cursor: pointer;
    color: #637381;
    font-weight: 500;
    font-size: 12px;
    line-height: 16px;
    margin-right: 20px;
    }
    
    .formbold-btn {
    text-align: center;
    width: 100%;
    font-size: 16px;
    border-radius: 5px;
    padding: 14px 25px;
    border: none;
    font-weight: 500;
    background-color: #6a64f1;
    color: white;
    cursor: pointer;
    margin-top: 25px;
    }
    
    .formbold-btn:hover {
    box-shadow: 0px 3px 8px rgba(0, 0, 0, 0.05);
    }
    
    .formbold-w-45 {
    width: 45%;
    }
    
    .tooltip {
    position: relative;
    display: inline-block;
    border-bottom: 1px dotted black;
    }
    
    .tooltip .tooltiptext {
    visibility: hidden;
    width: 360px;
    background-color: black;
    color: #fff;
    text-align: center;
    border-radius: 6px;
    padding: 5px 0;
    
    /* Position the tooltip */
    position: absolute;
    z-index: 1;
    top: -5px;
    left: 105%;
    }
    
    .tooltip:hover .tooltiptext {
    visibility: visible;
    }
    
    table,
    th,
    td {
    border: 1px solid black;
    }
    
    .vline
    {
    position:fixed;
    top:0;
    left:50%;
    bottom:0; margin:0;
    border:none;
    border-right:solid 1px black;
    z-index:10;
    }""")
            # Closes the file.
            f.close()