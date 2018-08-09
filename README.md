# Analyze-Xray
Flask app that does a diagnosis based of uploaded image

## Deployment steps
1. Create virtual environment
```bash
python3 -m virtualenv ~/Analyze-Xray -p /root/anaconda3/bin/python
source bin/activate
```
2. Install requirements
```bash
pip install -r requirements.txt
pip install gunicorn
```
3. Create service
```bash
sudo nano /etc/systemd/system/flask_xray.service
```
4. Copy the following to the flask_xray.service file
```
[Unit]
Description=Gunicorn instance to serve Flask_xray
After=network.target

[Service]
User=root
Group=www-data
PIDFile=/tmp/gunicorn_Flask_xray.pid
WorkingDirectory=/root/Analyze-Xray
Environment="PATH=/root/Analyze-Xray/bin"
ExecStart=/root/Analyze-Xray/bin/gunicorn --workers 3 --bind 0.0.0.0:5001 -m 007 wsgi:app --timeout 180 --error-log /var/log/gunicorn/error.log --access-logfile /var/log/gunicorn/access.log --log-file /var/log/gunicorn/gunicorn.log

[Install]
WantedBy=multi-user.target
```
5. Activate service
```bash
sudo mkdir /var/log/gunicorn
sudo systemctl start flask_xray
sudo systemctl enable flask_xray
```
6. Configuring Nginx to Proxy Requests
```bash
sudo nano /etc/nginx/sites-available/default
```
7. Copy the following to the end of /etc/nginx/sites-available/default file
```
location /chestxray {
    include proxy_params;
    fastcgi_read_timeout 300;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    proxy_pass http://localhost:5001;
}
```
8. Edit the /etc/nginx/nginx.conf file and the following lines in the http section:
```
proxy_headers_hash_max_size 1024;
proxy_headers_hash_bucket_size 128; 
proxy_read_timeout 300;
```