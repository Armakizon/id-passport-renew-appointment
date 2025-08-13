# ID Passport Renewal Appointment Finder

[Bookgov.onrender.com](https://Bookgov.onrender.com/)

An automation system for finding and notifying available passport renewal appointments at Israeli government offices (Govisit). 

## Project Overview

This system periodically monitors the Israeli government's GoVisit portal for available passport renewal appointments across multiple branches. It workks like that:

- **Automatically logging in** using Selenium web automation
- **SMS verification handling** for mobile authentication
- **Auth token pulling** after logging in succesfully
- **API requesting** with the token we got from logging in
- **API sending to the server** for updating my site with the new appointments
- **Notifying mail subscribers** based on which parameters each person subscribed with

## Project Structure

```
id-passport-renew-appointment/
├── main.py                          # Main updating script
├── access_govisit.py               # Automated logging in
├── govisit_requests.py             # Both Get API requests from Govisit and Post to my own server
├── mailsender.py                   # Email notification system
├── appointment_site/               # Web application
│   ├── app.py                     # Flask main application
│   ├── api.py                     # API endpoints
│   ├── templates/                 # HTML templates
│   └── static/                    # CSS, JS, and assets
├── Helpware/                      # Utility scripts and tools, mainly one time use scripts for getting and converting branch sites data
├── email_templates/               # Email notification templates
├── smsreceiver/                   # Mobile app running on my phone to foward my SMS verification
├── pythoneverywhere.py            # PythonAnywhere server code
└── render.yaml                    # Render deployment configuration
```

## Core Scripts

### `main.py`
**Main orchestration script that runs the updating part**
- Coordinates token retrieval, appointment monitoring, and email notifications
- Runs continuously with 1-hour intervals between monitoring cycles
- Skip a run incase of captcha

### `access_govisit.py`
**Handles authentication with the GoVisit portal**
- Uses Selenium WebDriver to automate Firefox browser
- Manages SMS verification code retrieval
- Extracts authentication tokens for API access
- Includes anti-detection measures (profile management, user-agent spoofing)

### `govisit_requests.py`
**Handles most of all the incoming and outgoing API calls**
- Iterates through all government branch IDs from CSV file
- Makes API calls to check available dates for each branch
- Posts available appointments to the web dashboard

### `mailsender.py`
**Email notification and subscription management system**
- Fetches subscriber preferences from the pythoneverywhere.py
- Sends email notifications for new appointments

### `pythoneverywhere.py`
**PythonAnywhere server script**
- Handles SMS verification code reception
- Manages subscription database operations


## Utility Scripts



### `pythoneverywhere.py`
**PythonAnywhere deployment script**
- Handles SMS verification code reception
- Manages subscription database operations
- Provides external API endpoints for the main system
- Handles authentication and data validation

### `Helpware/` Directory
**Collection of utility and testing scripts**
- `captchaenjoyer.py` - Firefox profile management for captcha evasion (NOT IN USE CURRENTLY)
- `SQLcreater.py and others` - Database creation utilities

## Mobile Application

### `smsreceiver/`
**Android SMS catcher application**
-Checks for SMS messages from Govisit
-Sends the API request to the pythoneverywhere server

## Deployment

### Render Configuration (`render.yaml`)
- Defines service configuration for Render hosting
- Sets up environment variables and dependencies
- Configures build and runtime requirements

## Requirements

Realistically im the only one that is suppose to run it but incase someone wanna modify this software for other purposes:

Android Studio for building the app on your phone (and android phone)
Email
Alot of python libraries (you can find most of them in requirements)
Selenium
Firefox browser (can probably be easily used on chrome as well with minor tweaking) 

## Environment Variables

Create a `.env` file with the following variables:
```env
PASSWORD=personal password for blocking users from certian routes
PHONE_NUMBER=you phone number
ID_NUMBER=your id number
EMAIL_ADDRESS=The email that sends the subscription messages
EMAIL_PASSWORD=your email password or API password 
``` 

##Contact

**Author:** Shaked Diba | [shake901@gmail.com](mailto: shake901@gmail.com) | [LinkedIn](https://www.linkedin.com/in/shaked-diba-8a843b2a3/)


 
