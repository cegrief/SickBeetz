#!/bin/bash 
if [[ $UID != 0 ]]; then
    echo "Please run this script with sudo:"
    echo "sudo bash $0 $*"
    exit 1
fi
spinner()
{
    local pid=$1
    local delay=0.1
    local spinstr='|/-\'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

update(){
	{
 		apt-get -y update
 		apt-get -y install curl
		apt-get -y install gcc
		apt-get -y install libsm6
		apt-get -y install bzip2
		apt-get -y install libxrender1
		
	} 1> /dev/null
}

node(){
  {
     curl -sL https://deb.nodesource.com/setup | sudo bash -
     apt-get -y install nodejs
  } 1> /dev/null
}

dependencies(){
  {
     cd web
     npm install
     npm install pm2 -g
     npm install bower -g
     sudo -u ${SUDO_USER:-$USER} bower install

  } 1> /dev/null
}

mini(){

  if [ `uname -m` == 'x86_64' ]
  then
  {
     curl https://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh -o ~/miniconda.sh
  } &> /dev/null
  else
  {
     curl https://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86.sh -o ~/miniconda.sh
  } &> /dev/null
  fi
}

pydepends(){
  
  {
     /home/${SUDO_USER:-$USER}/miniconda/bin/conda install numpy
     /home/${SUDO_USER:-$USER}/miniconda/bin/conda install scipy
     /home/${SUDO_USER:-$USER}/miniconda/bin/conda install matplotlib
     /home/${SUDO_USER:-$USER}/miniconda/bin/conda install scikit-learn
     /home/${SUDO_USER:-$USER}/miniconda/bin/pip install librosa==0.3.1

  } 1> /dev/null
}

forward(){
  {
     iptables -A INPUT -i eth0 -p tcp --dport 80 -j ACCEPT
     iptables -A INPUT -i eth0 -p tcp --dport 5000 -j ACCEPT
     iptables -A PREROUTING -t nat -i eth0 -p tcp --dport 80 -j REDIRECT --to-port 5000
  }
}

startit(){
  sudo -u ${SUDO_USER:-$USER} pm2 start app.js -f
}

printf "\nUpdating system...\n"
update & spinner $!
printf " done\n"

printf "\nInstalling node...\n"
node & spinner $!
printf " done\n"

printf "\nInstalling dependencies...\n"
dependencies
printf " done\n"

printf "\nInstalling Miniconda...\n"
mini & spinner $!
bash ~/miniconda.sh
printf " done\n"

printf "\nInstalling Python Packages...\n"
pydepends & spinner $!
printf " done\n"

printf "\nForwarding Ports...\n"
forward & spinner $!
printf " done\n"

printf "\nStarting App in the background...\n"
startit & spinner $!
printf " done\n"

printf "\nSick Beetz has been succesfully installed."
printf "\nYou may stop the app at anytime by typing pm2 stop 0\n"
printf "\nView the readme for more information"
