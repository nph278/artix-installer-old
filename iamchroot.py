#!/usr/bin/env python

import sys

from subprocess import run, check_output

# Input vars
print("Region", end=": ")
region = input().strip()
print("City", end=": ")
city = input().strip()

disk = ""
while True:
    run("fdisk -l", shell=True)
    print("\nDisk to install to", end=": ")
    disk = input().strip()
    if len(disk) > 0:
        break

# Boring stuff you should probably do
run(f"ln -sf /usr/share/zoneinfo/{region}/{city} /etc/localtime", shell=True)
run("hwclock --systohc", shell=True)
run("hwclock --systohc", shell=True)

# Configure pacman
run("nvim /etc/pacman.conf", shell=True)
run("printf '\nkeyserver hkp://keyserver.ubuntu.com\n' >> /etc/pacman.d/gnupg/gpg.conf", shell=True)
run("pacman-key --populate artix", shell=True)

run("yes | pacman -Syu bat fd exa ripgrep neofetch", shell=True)

# Localization
print("Uncomment locales.")
input()
run("nvim /etc/locale.gen", shell=True)
run("locale-gen", shell=True)
print("LANG", end="=")
lang = input().strip()
if len(lang) < 2:
    lang = "en_US.UTF-8"

print("KEYMAP", end="=")
keymap = input().strip()
if len(keymap) < 2:
    keymap = "us"

run(f"printf 'LANG={lang}\n' > /etc/locale.conf", shell=True)
run(f"printf 'KEYMAP={keymap}\n' > /etc/vconsole.conf", shell=True)

# Host stuff
hostname = ""
while True:
    print("Hostname", end=": ")
    hostname = input().strip()
    if len(hostname) > 1:
        break
run(f"printf '{hostname}\n' > /etc/hostname", shell=True)
run(f"printf '\n127.0.0.1\tlocalhost\n::1\t\tlocalhost\n127.0.1.1\t{hostname}.localdomain\t{hostname}\n' > /etc/hosts", shell=True)

# Install boot loader
run("yes | pacman -S efibootmgr refind amd-ucode intel-ucode", shell=True)

disk3uuid = check_output("sudo blkid /dev/mapper/cryptroot -o value -s UUID", shell=True).strip()
run(f"printf '\"Boot with standard options\"  \"cryptdevice=UUID={disk3uuid}:cryptroot root=/dev/mapper/cryptroot resume=/dev/mapper/cryptswap rootflags=subvol=@ rw initrd=amd-ucode.img initrd=intel-ucode.img initrd=initramfs-linux.img\"\n' > /boot/refind_linux.conf", shell=True)

run("refind-install", shell=True)
run(f"refind-install --usedefault {disk}1", shell=True)

# Local.start
run(f"printf 'rfkill unblock wifi\nneofetch >| /etc/issue\n' > /etc/local.d/local.start", shell=True)
run("chmod +x /etc/local.d/local.start", shell=True)

# Add default user
run("yes | pacman -S zsh openrc-zsh-completions zsh-autosuggestions zsh-completions zsh-syntax-highlighting", shell=True)
run("chsh -s /bin/zsh", shell=True)
print("\nChanging root password...")
run("passwd", shell=True)
run("rm /etc/skel/.bash*", shell=True)
run("useradd -D -s /bin/zsh", shell=True)
username = ""
while True:
    print("Username", end=": ")
    username = input().strip()
    if len(username) > 1:
        break
run(f"useradd -m {username}", shell=True)
run(f"passwd {username}", shell=True)
run(f"usermod -a -G wheel {username}", shell=True)
run(f"usermod -a -G video {username}", shell=True)
run(f"usermod -a -G games {username}", shell=True)
print("Allow wheel users to use sudo.")
input()
run("EDITOR=nvim visudo", shell=True)

# Other stuff you should do or you'll be sad
run("yes | pacman -S dhcpcd wpa_supplicant connman-openrc", shell=True)
run("rc-update add connmand", shell=True)
print("MOTD", end=": ")
motd = input().strip()
run(f"printf '\n{motd}\n' > /etc/motd", shell=True)

run("printf '/dev/mapper/cryptswap\tswap\tswap\tdefaults\t0 0' >> /etc/fstab", shell=True)
print("Remove duplicate 'subvol's from fstab.")
print("And use '/dev/mapper/cryptroot instead of UUID.'")
input()
run("nvim /etc/fstab", shell=True)

# Finally fix swap
swapuuid = check_output("sudo blkid /dev/mapper/cryptswap -o value -s UUID", shell=True).strip()
run("printf 'run_hook() {\n\tcryptsetup open /dev/disk/by-uuid/" + swapuuid + " cryptswap\n}\n' > /etc/initcpio/hooks/openswap", shell=True)
run("printf 'build() {\n\tadd_runscript\n}\n' > /etc/initcpio/install/openswap", shell=True)
print("Add '/usr/bin/btrfs' to BINARIES")
print("Use these hooks:")
hooks_comment = "#HOOKS=(... autodetect keyboard keymap modconf block encrypt openswap resume filesystems ...)"
print(hooks_comment)
run(f"printf '{hooks_comment}' >> /etc/mkinitcpio.conf", shell=True)
input()
run("nvim /etc/mkinitcpio.conf", shell=True)
run("mkinitcpio -P", shell=True)

print("\nTasks completed. You should exit and reboot.")
