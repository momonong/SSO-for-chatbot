nginxCopy code
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