#!/bin/bash

#get the package_manager of the user
declare package_manager

if [ -f "/etc/debian_version" ]; then
	package_manager="apt"
elif [ -f "/etc/fedora-release" ]; then
	package_manager="dnf" #since python is a big dependencie of dnf, we don't have to check it or install any python related program, useless for now
elif [ -f "/etc/arch-release" ]; then
	package_manager="pacman" #installing python3 on pacman already gives the Python virtual environment, so only used in case the user doesn't have python
elif [ -f "/etc/products.d/openSUSE.prod" ]; then
	package_manager="zypper" #installing python3 on zypper already gives the Python virtual environment, so only used in case the user doesn't have python, test another file since the -release isn't here
else
	echo "Your distro isn't supported, the following distros and all of their forks are supported: arch, tumbleweed, fedora and debian, to run the file you have to check the setup.sh file and run_client and type the commands they need to run. If you want to add a support you can also open a pull request or an issue in the github." && exit 1
fi

#check if python is installed, if not install it
if ! python_loc="$(type -p "python3")" || [[ -z $python_loc ]]; then
	read -p "The program needs to install python. Continue? (Y/N): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
	if [ $package_manager == "apt" ]; then
		sudo apt install python3
	elif [ $package_manager == "pacman" ]; then
		sudo pacman -S python3
	elif [ $package_manager == "zypper" ]; then
		sudo zypper install python3 	
	fi
fi

if [ ! -d ".venv" ]; then #check if .venv exists, if not create it
	read -p "The program needs to create a venv folder to install the dependencies safely. Continue? (Y/N): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
	if [ $package_manager == "apt" ];  then
		sudo apt install python3-venv
	fi
	python3 -m venv .venv
fi

#install dependencies
.venv/bin/python -m pip install -r requirements.txt

