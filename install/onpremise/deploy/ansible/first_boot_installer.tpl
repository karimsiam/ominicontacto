#!/bin/bash

COMPONENT_REPO=https://gitlab.com/omnileads/ominicontacto.git
COMPONENT_RELEASE=master
SRC=/usr/src
PATH_DEPLOY=install/onpremise/deploy/ansible

# Set your Cloud Provider
#CLOUD=digitalocean
#CLOUD=onpremise
#CLOUD=linode
#CLOUD=vultr

# Set the variable or user_data terraform parameter like ${TZ}
NIC=${NIC} #eth1
TZ=${TZ} #America/Argentina/Cordoba
ami_user=${ami_user} #omnileadami
ami_password=${ami_password} #5_MeO_DMT
dialer_user=${dialer_user} #demo
dialer_password=${dialer_password} #demoadmin
pg_database=${pg_database} #omnileads
pg_username=${pg_username} #omnileads
pg_password=${pg_password} #098098ZZZ
extern_ip=none

PG_HOST=NULL #${pg_host}
PG_PORT=NULL #${pg_port}

RTPENGINE_HOST=NULL #${rtpengine_host}
RTPENGINE_UDP_INI=20000
RTPENGINE_UDP_END=30000

REDIS_HOST=NULL
DIALER_HOST=NULL #${dialer_host}
MYSQL_HOST=NULL #${mysql_host}
NGINX_HOST=NULL #${nginx_host}
WEBSOCKET_HOST=NULL #${websocket_host}

ENVIRONMENT_INIT=true #${init_env}

# KAMAILIO_BRANCH=develop
# ASTERISK_BRANCH=develop
# RTPENGINE_BRANCH=develop
# NGINX_BRANCH=develop
# REDIS_BRANCH=develop
# POSTGRES_BRANCH=develop
# WEBSOCKET_BRANCH=develop

echo "******************** IPV4 address config ***************************"
echo "******************** IPV4 address config ***************************"
case $CLOUD in
  digitalocean)
    echo -n "DigitalOcean"
    export PUBLIC_IPV4=$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address)
    export PRIVATE_IPV4=$(curl -s http://169.254.169.254/metadata/v1/interfaces/private/0/ipv4/address)
    ;;
  linode)
    echo -n "Linode"
    export PRIVATE_IPV4=$(ip addr show $NIC |grep "inet 192.168" |awk '{print $2}' | cut -d/ -f1)
    export PUBLIC_IPV4=$(curl checkip.amazonaws.com)
    ;;
  onpremise)
    echo -n "Onpremise CentOS7 Minimal"
    export PRIVATE_IPV4=$(ip addr show $PRIVATE_NIC | grep "inet\b" | awk '{print $2}' | cut -d/ -f1)
    if [ $PUBLIC_NIC ]; then
      export PUBLIC_IPV4=$(ip addr show $PUBLIC_NIC | grep "inet\b" | awk '{print $2}' | cut -d/ -f1)
    else
      export PUBLIC_IPV4=$(curl ifconfig.co)
    fi
    ;;
  *)
    echo -n "you must to declare CLOUD variable"
    ;;
esac

echo "******************** Cloud fix /etc/hosts ***************************"
echo "******************** Cloud fix /etc/hosts ***************************"
case $CLOUD in

  digitalocean)
    echo -n "DigitalOcean"
    sed -i 's/127.0.0.1 '$(hostname)'/#127.0.0.1 '$(hostname)'/' /etc/hosts
    sed -i 's/::1 '$(hostname)'/#::1 '$(hostname)'/' /etc/hosts
    ;;
  vultr)
    echo -n "Linode"
    TEMP_HOSTNAME=$(hostname)
    sed -i 's/127.0.0.1 '$TEMP_HOSTNAME'/#127.0.0.1 '$TEMP_HOSTNAME'/' /etc/hosts
    sed -i 's/::1       '$TEMP_HOSTNAME'/#::1 '$TEMP_HOSTNAME'/' /etc/hosts
    ;;
  *)
    echo -n "you must to declare CLOUD variable"
    ;;
esac

echo "******************** SElinux and Firewalld disable ***************************"
echo "******************** SElinux and Firewalld disable ***************************"
setenforce 0
sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/sysconfig/selinux
sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/selinux/config
systemctl disable firewalld > /dev/null 2>&1
systemctl stop firewalld > /dev/null 2>&1

echo "******************** yum update and install packages ***************************"
echo "******************** yum update and install packages ***************************"
yum -y update && yum -y install git python3 python3-pip kernel-devel

echo "******************** install ansible ***************************"
echo "******************** install ansible ***************************"
sleep 5
pip3 install --upgrade pip
pip3 install --user 'ansible==2.9.2'
export PATH="$HOME/.local/bin/:$PATH"

echo "********************************** sngrep SIP sniffer install *********************************"
echo "********************************** sngrep SIP sniffer install *********************************"
yum install ncurses-devel make libpcap-devel pcre-devel \
    openssl-devel git gcc autoconf automake -y
cd /root && git clone https://github.com/irontec/sngrep
cd sngrep && ./bootstrap.sh && ./configure && make && make install
ln -s /usr/local/bin/sngrep /usr/bin/sngrep


echo "***************************** git clone omnileads repo ******************************"
echo "***************************** git clone omnileads repo ******************************"
cd $SRC
git clone --recurse-submodules --branch $COMPONENT_RELEASE $COMPONENT_REPO
cd ominicontacto

echo "***************************** inventory setting *************************************"
echo "***************************** inventory setting *************************************"
sleep 5
python3 $PATH_DEPLOY/edit_inventory.py --self_hosted=yes \
  --ami_user=$ami_user \
  --ami_password=$ami_password \
  --dialer_user=$dialer_user \
  --dialer_password=$dialer_password \
  --ecctl=$ECCTL \
  --postgres_database=$pg_database \
  --postgres_user=$pg_username \
  --postgres_password=$pg_password \
  --sca=$SCA \
  --schedule=$schedule \
  --extern_ip=$extern_ip \
  --TZ=$TZ

if [[ "$PG_HOST"  != "NULL" ]]; then
  sed -i "s/#postgres_host=/postgres_host=$PG_HOST/g" $PATH_DEPLOY/inventory
fi
if [[ "$DIALER_HOST" != "NULL" ]]; then
  sed -i "s/#dialer_host=/dialer_host=$DIALER_HOST/g" $PATH_DEPLOY/inventory
fi
if [[ "$MYSQL_HOST" != "NULL" ]]; then
  sed -i "s/#mysql_host=/mysql_host=$MYSQL_HOST/g" $PATH_DEPLOY/inventory
fi
if [[ "$RTPENGINE_HOST" != "NULL" ]]; then
  sed -i "s/#rtpengine_host=/rtpengine_host=$RTPENGINE_HOST/g" $PATH_DEPLOY/inventory
fi
if [[ "$REDIS_HOST" != "NULL" ]]; then
  sed -i "s/#redis_host=/redis_host=$REDIS_HOST/g" $PATH_DEPLOY/inventory
fi
if [[ "$NGINX_HOST" != "NULL" ]]; then
  sed -i "s/#nginx_host=/nginx_host=$NGINX_HOST/g" $PATH_DEPLOY/inventory
fi
if [[ "$WEBSOCKET_HOST" != "NULL" ]]; then
  sed -i "s/#websocket_host=/websocket_host=$WEBSOCKET_HOST/g" $PATH_DEPLOY/inventory
fi

echo "******************************** deploy.sh execution *******************************"
echo "******************************** deploy.sh execution *******************************"
sleep 5

cd $PATH_DEPLOY
./deploy.sh -i --iface=$NIC

if [ -d /usr/local/queuemetrics/ ]; then
  systemctl stop qm-tomcat6 && systemctl disable qm-tomcat6
  systemctl stop mariadb && systemctl disable mariadb
fi

echo "********************************** setting demo environment *********************************"
echo "********************************** setting demo environment *********************************"
if [[ "$ENVIRONMENT_INIT" == "true" ]]; then
  /opt/omnileads/bin/manage.sh inicializar_entorno
fi


echo "********************************** Exec task if RTP run AIO *********************************"
echo "********************************** Exec task if RTP run AIO *********************************"
if [[ "$RTPENGINE_HOST" != "NULL" && "$CLOUD" != "onpremise" ]]; then
  echo -n "CLOUD rtpengine"
  echo "OPTIONS="-i $PUBLIC_IPV4 -o 60 -a 3600 -d 30 -s 120 -n 127.0.0.1:22222 -m $RTPENGINE_UDP_INI -M $RTPENGINE_UDP_END -L 7 --log-facility=local1""  > /etc/rtpengine-config.conf
  systemctl start rtpengine
fi

reboot
