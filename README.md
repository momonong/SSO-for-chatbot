# OAuth Integration with Flask

This project demonstrates how to integrate OAuth into a Flask application for authenticating users via the National Cheng Kung University (NCKU) OAuth service.

## Prerequisites

- Python 3.10
- Flask
- requests-oauthlib
- A valid domain name configured to redirect to your application for OAuth callbacks.

## Setup

Ensure you have Poetry installed. If you haven't, install it following the instructions on the [official Poetry website](https://python-poetry.org/docs/).

## Installation

Navigate to the project directory and run the following command to install dependencies:

```
poetry install
poetry update
```

## Configuration
Before running the application, ensure the following environment variables are properly set in your .env file:

```
CLIENT_ID: The client ID provided by NCKU.
CLIENT_SECRET: The client secret provided by NCKU.
AUTHORIZATION_BASE_URL: URL to initiate the OAuth authorization flow.
TOKEN_URL: URL to fetch the OAuth tokens after successful authorization.
REDIRECT_URI: The URI to which the OAuth service will redirect after successful authentication.
```

## Running the App
Activate the poetry environment and start the application with:

```
poetry shell
flask run --port=5000
```

The app will start a local server on `http://localhost:5000.`

## OAuth Flow
When you navigate to `http://localhost:5000`, the Flask app initiates the OAuth login process by redirecting to the NCKU OAuth login page for authentication. After successful login, NCKU redirects back to the /callback route with an authorization code.

The Flask app then:

Exchanges the authorization code for an access token.
Stores the access token and any other user info in the session.
Redirects to a form where additional information can be filled in.

## Form Submission
On the form page:

User's basic information, fetched using the access token, is displayed.
Users can fill in additional information like nationality.
Upon submission, the data is sent to the backend, where it can be processed further.

## Error Handling
If you encounter errors during the OAuth process, check the Flask logs and your OAuth service configuration for debugging.

## Contributing
Contributions are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgements
National Cheng Kung University for providing the OAuth service.
Flask and requests-oauthlib contributors.
