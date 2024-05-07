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

## Server Setup and Deployment with Gunicorn and Nginx

This section provides a guide on setting up a WSGI server using Gunicorn and configuring Nginx as a reverse proxy for a Flask application.

**Install Gunicorn**  
Gunicorn is used as the WSGI HTTP server for Python applications. To install Gunicorn, run:
```poetry add gunicorn```

**Run the Application with Gunicorn**  
To start the application using Gunicorn, navigate to your project directory and run:
```gunicorn "wsgi:app" --bind 0.0.0.0:8000```
This command will bind the Gunicorn server to all network interfaces on port 8000, making it accessible via your server's IP address or domain name.

### Configure Nginx as a Reverse Proxy
Nginx can be used to efficiently serve static files, handle more HTTP requests, and provide SSL/TLS termination. 
Here's how you can set up Nginx to work with Gunicorn:

```
# Install Nginx

sudo apt update
sudo apt install nginx
```
Create and Configure Nginx Server Block:
```
# Navigate to the Nginx configuration directory and create a new configuration file for your application

cd /etc/nginx/sites-available
sudo vim myapp.conf
```
Add the following configuration to the file:
```
server {
    listen 80;
    listen [::]:80;
    server_name example.com;  # 更換為你的域名或公網 IP 地址
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name example.com;  # 更換為你的域名或公網 IP 地址

    ssl_certificate /etc/ssl/certs/mycertificate.crt;
    ssl_certificate_key /etc/ssl/private/mykey.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers "EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH";

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;  # 確保這裡指向你的 Flask 應用
    }
}
```
Enable the Configuration:Link your configuration file from sites-available to sites-enabled:  
```sudo ln -s /etc/nginx/sites-available/myapp.conf /etc/nginx/sites-enabled/```  
Test and Restart Nginx:Test your Nginx configuration for syntax errors:  
```sudo nginx -t```  
If everything is ok, restart Nginx to apply the changes:  
```sudo systemctl restart nginx```  

Secure the Application with SSL/TLS:If you're using a domain name, it's recommended to secure your application with an SSL/TLS certificate. 
You can obtain a free certificate from Let's Encrypt using Certbot:
```
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d mydomain.com
```
Follow the prompts, and Certbot will automatically configure SSL for your domain and modify the Nginx configuration accordingly.

Ensure that both Gunicorn and Nginx start automatically at boot:
```
sudo systemctl enable nginx
sudo systemctl enable gunicorn
```
You may need to create a systemd service file for Gunicorn if you require it to start automatically.

Conclusion
With these settings, your Flask application is now served by Gunicorn, with Nginx acting as a reverse proxy that handles client requests and serves static files efficiently.

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
