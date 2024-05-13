server {
    listen 80;
    listen [::]:80;

    server_name login.nckuoiachatbot.software;

    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;

    server_name login.nckuoiachatbot.software;

    ssl_certificate         /etc/ssl/new.pem;
    ssl_certificate_key     /etc/ssl/key.pem;
    ssl_protocols           TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers "EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH";

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:5000;  # 指向 Flask 應用
    }
}
