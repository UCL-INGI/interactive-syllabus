yum install -y https://centos6.iuscommunity.org/ius-release.rpm 
yum install -y git python35u python35u-pip python35u-devel gcc httpd httpd-devel
yum install -y python35u-mod_wsgi.x86_64
cp /vagrant/httpd_config/httpd.conf /etc/httpd/conf/httpd.conf
cp /vagrant/httpd_config/sysconfig_httpd /etc/sysconfig/httpd
setenforce 0
cp /vagrant/selinux/sysconfig_selinux /etc/sysconfig/selinux
python3.5 -m ensurepip


# Install Interactive-Syllabus
cd /var/www/
git clone https://github.com/OpenWeek/interactive-syllabus.git
chown apache interactive-syllabus -R
cd interactive-syllabus
cp /vagrant/syllabus.wsgi ./
pip3.5 install .

# Start httpd

service httpd enable
service httpd start
