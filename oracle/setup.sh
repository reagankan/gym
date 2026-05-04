#!/bin/bash
set -e

echo "=== Gym Tracker Server Setup ==="

# Install system packages
apt update
apt install -y python3-venv python3-pip nginx apache2-utils

# Create /opt/gym owned by ubuntu
mkdir -p /opt/gym
chown ubuntu:ubuntu /opt/gym

# Create venv if it doesn't exist
if [ ! -d /opt/gym/venv ]; then
    sudo -u ubuntu python3 -m venv /opt/gym/venv
fi

# Install Python dependencies
sudo -u ubuntu /opt/gym/venv/bin/pip install -r /opt/gym/requirements.txt --quiet

# Install systemd service
cp /opt/gym/oracle/gym-server.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable gym-server

# Install nginx config
cp /opt/gym/oracle/nginx-gym.conf /etc/nginx/sites-available/gym
ln -sf /etc/nginx/sites-available/gym /etc/nginx/sites-enabled/gym
rm -f /etc/nginx/sites-enabled/default
systemctl enable nginx

# Create htpasswd file for basic auth
htpasswd -cb /etc/nginx/.htpasswd admin admin
chmod 640 /etc/nginx/.htpasswd
chown root:www-data /etc/nginx/.htpasswd

# Start/restart services
systemctl restart gym-server
nginx -t
systemctl restart nginx

# Open port 80 in iptables (idempotent: check before adding)
if ! iptables -C INPUT -p tcp --dport 80 -j ACCEPT 2>/dev/null; then
    iptables -I INPUT 5 -p tcp --dport 80 -j ACCEPT
fi

# Persist iptables rules
DEBIAN_FRONTEND=noninteractive apt install -y iptables-persistent
netfilter-persistent save

echo ""
echo "=== Setup Complete ==="
systemctl status gym-server --no-pager
echo ""
echo "Nginx status:"
systemctl status nginx --no-pager
