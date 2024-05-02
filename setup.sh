# Install gunicorn
pip install gunicorn

# Setting up wsgi server by running wsgi.py
gunicorn wsgi:app
# Enable all other ip address to access
gunicorn --bind 0.0.0.0 wsgi:app
# Enable specific ip address 
gunicorn --bind <ip_address> wsgi:app

# If we want to start for short
cd <repo_dir>
vi <start_script.sh>
# Copy the shell scripts we want to run
# Remember to check the file permission
chmod <permission> <start_script.sh>
./<start_script.sh>

# Install nginx
sudo apt update
sudo apt install nginx

# Create and edit nginx config file
cd /etc/nginx/conf.d
sudo vi flask.conf
	server {
	  listen 80; 
	  server_name 192.168.1.177; # ip address or domain name to client access 
	  location / { # '/' for root index
	    include proxy_params;
	    proxy_pass http://127.0.0.1:8000;
	  }
	}

# Start nginx
sudo systemctl start nginx
# Check running status
sudo systemctl status nginx
# Enable nginx boot autorun
sudo systemctl enable nginx 