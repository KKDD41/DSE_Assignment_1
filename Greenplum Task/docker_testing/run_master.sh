/usr/sbin/sshd
echo "a" | passwd gpadmin --stdin
su gpadmin
cd /home/gpadmin
source /usr/local/gpdb/greenplum_path.sh
