# Trading Signals with Fyres

This project helps you generate trading signals using the Fyres API. It allows you to automate the process of monitoring stocks and receiving trading signals.

## Warning

This repository is intended for educational purposes only. The implementation of the EMA strategy is arbitrary and should not be used for actual trading. Consider developing, backtesting, and implementing a different strategy.


## Setup Instructions

### 1. Clone the Repo

Clone the repository to your local machine:
```bash
git clone https://github.com/dharmik-anghan/fyres-trading-signals.git
```
Navigate to the project directory:
```bash
cd fyres-trading-signals
```

### 2. Create a Virtual Environment

First, create a virtual environment to manage your project's dependencies:

```bash
python -m venv venv
```

Activate the virtual environment:

For Windows:
```bash
venv\Scripts\activate
```

For Linux:
```bash
source venv/bin/activate
```

### 3. Install Dependencies

Install the necessary dependencies listed in the requirements.txt file:

```bash
pip install -r requirements.txt
```

### 4. Configure Your Environment Variables
Copy the sample environment file and add your secrets:
```bash
cp .env-sample .env
```
Edit the .env file and fill in your credentials and secrets:
```bash
FYERS_ID=
TOTP_KEY=
PIN=
CLIENT_ID=
SECRET_KEY=
REDIRECT_URI=
ACCESS_TOKEN=None
RESPONSE_TYPE=code
GRANT_TYPE=authorization_code
TELEGRAM_CHAT_ID=
TELEGRAM_API_TOKEN=
```

### 5. Add Your Stocks
You can add the stocks you want to monitor in the stocks.csv file. Ensure each stock is listed on a new line.

### 6. Run the Main Script
Run the main Python script to start generating trading signals:
```bash
python main.py
```

## Additional Information
- Make sure to keep your .env file private and never expose it publicly as it contains sensitive information.
- The requirements.txt should include all the necessary libraries like fyres, pandas, requests, and python-dotenv.

## Contact
For any questions or support, please contact the project maintainer. You'll find contact details on profile.
``` 
This markdown file provides a comprehensive guide for setting up and running your project. You can copy and paste this directly into a file named `README.md`.
```