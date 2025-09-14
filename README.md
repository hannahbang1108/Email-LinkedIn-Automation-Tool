# Email-LinkedIn-Automation-Tool
This project is a website that automates email and part of LinkedIn prospecting, originally made as a personal project to aid my work as an intern at Stateable before we transitioned to creating a higher-level in-house tool.

## Description
This automation tool is a website that connects to the Google Cloud Console and automatically sends out emails to contacts in a CSV file. The tool also formats LinkedIn profile links, assumed to be in the CSV, in an organized format to make it easier to manually send out connection requests.

There are 3 main files:
1) run.py, which is where you run the code to start up the app
2) Sales.py, which is a class that stores user information and contians methods for automatically sending out properly formatted emails
3) view.py, which contains methods for the Flask application and provides web routes for user interaction, allowing them to upload contact lists, send personalized emails, and generate LinkedIn outreach messages while also having the functionality to delete specific contacts or entire companies from the uploaded data

There are 3 main templates:
1) upload.html, which is the default home page that lets you fill in your information to generate an email signature, or delete specific contacts or entire companies from the uploaded data
2) action.html, which shows text boxes for inputting email and LinkedIn message content
3) linkedin_outreach.html, which shows a formatted list of all linkedIn urls for every contact in the CSV

## Main Technologies / Libraries Used
* HTML: Structures the web page content and user interface with elements like forms and buttons.
* CSS: Styles the HTML, controlling the visual design, layout, and appearance of the web pages.
* JavaScript: Adds interactivity and dynamic behavior to the web page, running directly in the browser.
* Python: Handles all the backend logic, processing data and connecting to APIs.
* Flask: The web framework used to create the web interface and handle requests.
* pandas: The library used for data manipulation, specifically for reading and processing the contact CSV files.
* Google Cloud Console: The platform used to manage and configure the project, enable the Gmail API, and generate the necessary credentials.
* Google Gmail API: The service that allows the application to send emails on a user's behalf.
* Git: The version control system used to track changes and manage the project.
   
## Getting Started

### Installing

Prerequesites: 
* Python 3.10.5
* pip
* Google Account
* Google Console Project

To install the project, download all the content in this folder.

### Setup

1.  **Clone the Repository**:
    ```sh
    git clone https://github.com/hannahbang1108/Email-LinkedIn-Automation-Tool.git
    cd Email-LinkedIn-Automation-Tool
    ```
    
1.  **Install Necessary Libraries**:
    ```sh
    pip install pandas Flask google-auth google-auth-oauthlib google-api-python-client
    ```

2.  **Configure Your Google Cloud Project**:
    This application uses the Gmail API to send emails. You need to create your own credentials to use it.

    * Go to the Google Cloud Console and create a new project (https://developers.google.com/workspace/guides/create-project)
    * Enable the **Gmail API** from the API Library (https://developers.google.com/workspace/guides/enable-apis)
    * Navigate to the **OAuth consent screen** and set the "User type" to **External**. Complete the required verification details (https://developers.google.com/workspace/guides/configure-oauth-consent)
    * Go to the **Credentials** page, create an **OAuth 2.0 Client ID**, and choose "Desktop app" as the application type (https://developers.google.com/workspace/guides/create-credentials)

## Executing Program

In order to execute the project on your device, run run.py and follow the produced link.

## Credits

* Most of the CSS was pulled from a template from Formbold: https://formbold.com/templates
* The starting point for automatically sending emails using the Gmail API was pulled from code on the Gmail API documentation: https://developers.google.com/workspace/gmail/api/guides/
