## 1. Overview
This Telegram bot is designed to facilitate volunteering programs by enabling users to sign up as volunteers, join activities, request certification for their service, and access helpful commands. The bot is built using Python's `telegram.ext` library and interacts with Google Sheets for data management.

## 2. Requirements
- Python 3.x
- `python-telegram-bot` library v13.13

## 3. Installation

### 3.1. Setting up the Python Environment
Before running the bot, ensure you have Python installed on your system. If not, download and install it from [python.org](https://www.python.org/).

### 3.2. Installing Dependencies
1. Install the `python-telegram-bot` library using pip:
    ```bash
    pip install python-telegram-bot==20.7
    ```

2. Install Google Sheets API dependencies:
    ```bash
    pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
    ```

### 3.3. Configuration
1. Set up `config.py`:
    - `telegram_token`: Obtain a Telegram bot token and assign it to `telegram_token`.
    - `DB_ID`: Assign the Google Sheets document ID for data storage to `DB_ID`.

2. Create `credentials.json`:
    - Create a file named `credentials.json` with the correct credentials for accessing Google Sheets API.

## 4. Roles and Actions

### 4.1. Volunteers
1. **Sign Up**: Volunteers can sign up for the service by using the `/register` command. They will be prompted to provide their name, email, phone number, and age.
2. **Join Activities**: Volunteers can join activities using the `/join` command followed by the activity ID. They need to enroll first before joining an activity.
3. **View Enrolled Activities**: Volunteers can view the activities they have joined using the `/view` command.
4. **Request Certification**: Volunteers can request certification for their service using the `/certificate` command.
5. **Help**: Volunteers can access a list of available commands using the `/help` command.

### 4.2. Admin
1. **Manage Activities**: Admins manage the list of available activities. They can add, edit, or remove activities directly from the Google Sheets document.
2. **Approve Registrations**: Admins review and approve volunteer registrations. They can change the approval status of registrations in the Google Sheets document.
3. **Generate Certificates**: Admins generate certificates for volunteers upon request. They mark the certification status in the Google Sheets document.
4. **Generate detailed reports**: Excel sheet as the data base offers flexibility to generate tables and graphs based on data collected.

## 5. Rationale for Telegram Bot and Google Sheets Integration

### 5.1. Cost-Effectiveness
- **Telegram Bot**: Telegram bots are free to create and use, making them a cost-effective solution for program management. There are no licensing fees or subscription costs associated with using Telegram bots, making it an affordable option for organizations with limited budgets.

- **Google Sheets**: Google Sheets offers a free tier for individual users and small organizations, providing ample storage and functionality for basic program management needs. Larger organizations may opt for paid Google Workspace plans for additional features and storage capacity, but the cost remains relatively low compared to maintaining on-premises databases or custom software solutions.

### 5.2. Accessibility
- **Telegram Bot**: Telegram is a widely used messaging platform with a user-friendly interface accessible on various devices, including smartphones and desktops. Integrating the program management system with Telegram ensures accessibility for volunteers and administrators, allowing them to interact with the system conveniently from anywhere.

- **Google Sheets**: Google Sheets is a cloud-based spreadsheet application accessible through any web browser. By using Google Sheets for data storage, volunteers and administrators can access and manage program-related data from any device with an internet connection. This cloud-based approach eliminates the need for complex server setups and provides real-time collaboration features.

### 5.3. Ease of Use
- **Telegram Bot**: Telegram bots provide a simple and intuitive interface for users to interact with the program management system. Volunteers can perform tasks such as registering for the program, joining activities, and requesting certification through straightforward commands without the need for a dedicated application or website.

- **Google Sheets**: Google Sheets offers a familiar spreadsheet interface that is easy to navigate and manipulate. Administrators can manage program data, such as volunteer registrations, activity details, and certification requests, using familiar spreadsheet functionalities like sorting, filtering, and data validation.

### 5.4. Data Security and Privacy
- **Telegram Bot**: Telegram provides end-to-end encryption for messages and data exchanged between users and bots, ensuring the security and privacy of sensitive information. Volunteers can trust that their personal data, such as contact details and certification records, are protected from unauthorized access or disclosure.

- **Google Sheets**: Google Sheets employs robust security measures to protect data stored in the cloud, including encryption at rest and in transit, multi-factor authentication, and access controls. Administrators can configure sharing settings and permissions to restrict access to sensitive program data and ensure compliance with data protection regulations.

