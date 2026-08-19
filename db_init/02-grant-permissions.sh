mysql -u root -p"${MYSQL_ROOT_PASSWORD}" << EOF

-- Grant ALL PRIVILEGES to root@'%' from any host
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '${MYSQL_ROOT_PASSWORD}' WITH GRANT OPTION;

-- Grant permissions to the app user
GRANT ALL PRIVILEGES ON \`${MYSQL_DATABASE}\`.* TO '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_PASSWORD}';

FLUSH PRIVILEGES;
EOF

if [ $? -eq 0 ]; then
    echo "✓ User permissions granted successfully"
else
    echo "✗ Error granting permissions"
    exit 1
fi
