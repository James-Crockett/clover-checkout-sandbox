## Initial setup

Added uv for installing dependencies
Added .gitignore

Added the following libs:
fastapi - API framework
uvicorn - for interacting with sockets
requests - for making HTTP requests
python-dotenv - for loading secret tolkens from .env file

## Rough Structure

Before I go into building the application, I forgot to go into the structure of the assignment/breaking it down.

# Objective of the assignment

A web based checkout app integrated with a clover api

# Input

By the requirements, the user has to give:
    - An amount - int
    - Product name - char
    - A trigger after entering or submit action

# Inupt from backend

Clover would have config values, at this stage not sure what values id be using, have to refer the docs

# Backend

After the submission, the backend should:
    - Validate the amount
    - Convert to cents since this is a starndard, not complicating with money var
    - Create clover order
    - Added line item to order
    - Initiate payment
    - Fetch the payment status
    - Log the transaction
    - Return the status to the front end