#!/usr/bin/env bash

# stop on errors
set -eu

DISK='/dev/sda'
FQDN='camisolevm'
LANGUAGE='en_US.UTF-8'
PASSWORD=$(/usr/bin/openssl passwd -crypt 'camisole')

CONFIG_SCRIPT='/usr/local/bin/arch-config.sh'
CONFIG_USER_SCRIPT='/usr/local/bin/arch-config-user.sh'
ROOT_PARTITION="${DISK}1"
TARGET_DIR='/mnt'
COUNTRY=${COUNTRY:-US}
MIRRORLIST="https://www.archlinux.org/mirrorlist/?country=${COUNTRY}&protocol=http&protocol=https&ip_version=4&use_mirror_status=on"

echo "==> Setting local mirror"
curl -s "$MIRRORLIST" |  sed 's/^#Server/Server/' > /etc/pacman.d/mirrorlist

echo "==> Clearing partition table on ${DISK}"
/usr/bin/sgdisk --zap ${DISK}

echo "==> Destroying magic strings and signatures on ${DISK}"
/usr/bin/dd if=/dev/zero of=${DISK} bs=512 count=2048
/usr/bin/wipefs --all ${DISK}

echo "==> Creating /root partition on ${DISK}"
/usr/bin/sgdisk --new=1:0:0 ${DISK}

echo "==> Setting ${DISK} bootable"
/usr/bin/sgdisk ${DISK} --attributes=1:set:2

echo '==> Creating /root filesystem (ext4)'
/usr/bin/mkfs.ext4 -O ^64bit -F -m 0 -q -L root ${ROOT_PARTITION}

echo "==> Mounting ${ROOT_PARTITION} to ${TARGET_DIR}"
/usr/bin/mount -o noatime,errors=remount-ro ${ROOT_PARTITION} ${TARGET_DIR}

echo '==> Bootstrapping the base installation'
/usr/bin/pacstrap ${TARGET_DIR} base base-devel gptfdisk openssh syslinux \
                                expac yajl git perl

/usr/bin/arch-chroot ${TARGET_DIR} syslinux-install_update -i -a -m
/usr/bin/sed -i "s|sda3|${ROOT_PARTITION##/dev/}|" "${TARGET_DIR}/boot/syslinux/syslinux.cfg"
/usr/bin/sed -i 's/TIMEOUT 50/TIMEOUT 10/' "${TARGET_DIR}/boot/syslinux/syslinux.cfg"

echo '==> Generating the filesystem table'
/usr/bin/genfstab -p ${TARGET_DIR} >> "${TARGET_DIR}/etc/fstab"

echo '==> Generating the system configuration script'
/usr/bin/install --mode=0755 /dev/null "${TARGET_DIR}${CONFIG_SCRIPT}"
/usr/bin/install --mode=0755 /dev/null "${TARGET_DIR}${CONFIG_USER_SCRIPT}"

cat <<-EOF > "${TARGET_DIR}${CONFIG_SCRIPT}"
    echo '${FQDN}' > /etc/hostname
    /usr/bin/sed -i 's/#${LANGUAGE}/${LANGUAGE}/' /etc/locale.gen
    /usr/bin/locale-gen
    /usr/bin/mkinitcpio -p linux
    /usr/bin/usermod --password ${PASSWORD} root
    # https://wiki.archlinux.org/index.php/Network_Configuration#Device_names
    /usr/bin/ln -s /dev/null /etc/udev/rules.d/80-net-setup-link.rules
    /usr/bin/ln -s '/usr/lib/systemd/system/dhcpcd@.service' '/etc/systemd/system/multi-user.target.wants/dhcpcd@eth0.service'
    /usr/bin/sed -i 's/#UseDNS yes/UseDNS no/' /etc/ssh/sshd_config
    /usr/bin/systemctl enable sshd.service

    /usr/bin/useradd --password ${PASSWORD} --comment 'Camisole User' --create-home --user-group camisole
    echo 'Defaults env_keep += "SSH_AUTH_SOCK"' > /etc/sudoers.d/10_camisole
    echo 'camisole ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers.d/10_camisole
    /usr/bin/chmod 0440 /etc/sudoers.d/10_camisole
    /usr/bin/install --directory --owner=camisole --group=camisole --mode=0700 /home/camisole/.ssh
EOF

cat <<-EOF > "${TARGET_DIR}${CONFIG_USER_SCRIPT}"
    mkdir -p /tmp/pacaur_install
    cd /tmp/pacaur_install

    export PATH="/usr/bin/core_perl:$PATH"

    if [ ! -n "$(pacman -Qs cower)" ]; then
        curl -o PKGBUILD https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h=cower
        makepkg PKGBUILD --skippgpcheck --install --needed --noconfirm
    fi

    if [ ! -n "$(pacman -Qs pacaur)" ]; then
        curl -o PKGBUILD https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h=pacaur
        makepkg PKGBUILD --install --needed --noconfirm
    fi

    rm -rf /tmp/pacaur_install

    pacaur -S camisole-git camisole-languages --noconfirm --noedit
    sudo systemctl enable camisole

    # clean up
    sudo /usr/bin/pacman -Rcns --noconfirm gptfdisk

    /usr/bin/yes | sudo /usr/bin/pacman -Scc
    sudo /usr/bin/pacman-optimize
    sudo pacman -Rsn \$(pacman -Qdtq)

    # Write zeros to improve virtual disk compaction.
    zerofile=\$(/usr/bin/mktemp /zerofile.XXXXX)
    /usr/bin/dd if=/dev/zero of="\$zerofile" bs=1M
    /usr/bin/rm -f "\$zerofile"
EOF

echo '==> Entering chroot and configuring system'
/usr/bin/arch-chroot ${TARGET_DIR} ${CONFIG_SCRIPT}
/usr/bin/arch-chroot ${TARGET_DIR} su -c ${CONFIG_USER_SCRIPT} camisole
rm "${TARGET_DIR}${CONFIG_SCRIPT}"
rm "${TARGET_DIR}${CONFIG_USER_SCRIPT}"

/usr/bin/sync
echo '==> Installation complete!'
/usr/bin/sleep 3
/usr/bin/umount ${TARGET_DIR}
