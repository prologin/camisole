#!/usr/bin/env bash

PASSWORD=$(/usr/bin/openssl passwd -crypt 'camisole')

echo "==> Enabling SSH"
# Vagrant-specific configuration
/usr/bin/useradd --password ${PASSWORD} --comment 'Vagrant User' --create-home --user-group camisole
echo 'Defaults env_keep += "SSH_AUTH_SOCK"' > /etc/sudoers.d/10_camisole
echo 'camisole ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers.d/10_camisole
/usr/bin/chmod 0440 /etc/sudoers.d/10_camisole
/usr/bin/systemctl start sshd.service
