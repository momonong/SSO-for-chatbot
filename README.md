# SSO Integration with Flask using pysaml2

This project demonstrates how to integrate Single Sign-On (SSO) into a Flask application using the pysaml2 library. It includes steps for setting up the SSO process with SSOCircle as an Identity Provider (IdP).

## Prerequisites

- Python 3.10
- Flask
- pysaml2
- A valid domain name configured for your application to communicate with the SSOCircle IdP.

## Setup

Ensure you have Poetry installed. If you haven't, install it following the instructions on the [official Poetry website](https://python-poetry.org/docs/).

## Installation

Navigate to the project directory and run the following command to install dependencies:

```
poetry install
poetry update
```

## Configuration
Before running the application, configure the SAML client in app.py:

Update metadata_path with the correct path to your SAML metadata file.
Replace 'YOUR_SECRET_KEY' with a strong secret key for Flask sessions.
Ensure your entityid matches the one registered on SSOCircle.

## Running the App
Activate the poetry environment and start the application with:

```
poetry shell
flask run --port=5000
```

The app will start a local server on `http://localhost:5000.`

## SSO Flow
When you navigate to `http://localhost:5000`, the Flask app initiates the SSO login process by redirecting to the SSOCircle login page for authentication. After successful login, SSOCircle redirects back to the /saml/acs/ route with a SAMLResponse.

The Flask app then:

Parses the SAMLResponse.
Extracts the user information.
Stores user information in the session.
Redirects to a form where additional information can be filled in.

## Form Submission
On the form page:

User's name, student ID, and department, extracted from the SSO process, are pre-filled.
Users are asked to fill in their nationality.
Upon submission, the data is sent to the backend, where it can be processed further.

## Error Handling
If you encounter errors during the SSO process, check the Flask logs and SSOCircle configuration for debugging.

## Contributing
Contributions are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgements
SSOCircle for providing a free IdP for SAML testing.
Flask and pysaml2 contributors.
