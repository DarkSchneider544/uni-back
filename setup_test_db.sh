a#!/bin/bash

# Script to setup test database for running tests

echo "Setting up test database for Unified Office Management System..."

# Drop existing test database if it exists
echo "1. Dropping existing test database..."
sudo -u postgres psql -c "DROP DATABASE IF EXISTS office_management_test;"

# Create fresh test database
echo "2. Creating fresh test database..."
sudo -u postgres psql -c "CREATE DATABASE office_management_test;"

# Grant permissions
echo "3. Granting permissions to office_admin..."
sudo -u postgres psql -d office_management_test -c "GRANT ALL PRIVILEGES ON DATABASE office_management_test TO office_admin;"
sudo -u postgres psql -d office_management_test -c "GRANT ALL ON SCHEMA public TO office_admin;"

echo "✅ Test database created successfully!"
echo ""
echo "Database details:"
echo "  Database: office_management_test"
echo "  User: office_admin"
echo "  Password: office_password"
echo "  Connection string: postgresql://office_admin:office_password@localhost:5432/office_management_test"
echo ""
echo "You can now run tests with:"
echo "  pytest test_all.py -v"
