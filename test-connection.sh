#!/bin/bash

echo "Testing backend connection..."
curl -s http://localhost:4000/health || echo "Backend not responding"

echo -e "\nTesting frontend connection..."
curl -s http://localhost:3000 | head -5 || echo "Frontend not responding"

echo -e "\nChecking processes..."
ps aux | grep -E "(main|node)" | grep -v grep
