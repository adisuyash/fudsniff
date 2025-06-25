#!/bin/bash
echo "Setting up FudSniff..."

# Frontend setup
echo "Installing frontend dependencies..."
cd frontend && npm install && cd ..

# Backend setup
echo "Setting up Python virtual environment..."
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

echo "Setup complete! 🐕"
echo "Don't forget to add your API keys to backend/.env"