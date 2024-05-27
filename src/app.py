import csv
import time
import requests
import pandas as pd
import pandas_ta as ta
from datetime import datetime
from fyers_apiv3 import fyersModel
from datetime import datetime, timedelta
from fyers_apiv3.FyersWebsocket import data_ws
from src.login import login_app
from src.logger import logging
from config import Config

token = login_app.generate_token()

logging.info("Token generated") if token else logging.critical("Token not generated")

fyers = fyersModel.FyersModel(
    client_id=Config.CLIENT_ID, is_async=False, token=token, log_path=""
)

stocks = [name[0] for name in csv.reader(open("stocks.csv"))]
today = datetime.now().date()
today_str = str(datetime.now().date())
range_from = str(today - timedelta(days=14))
stock_hist_data = {}
stocks_to_buy = []
stock_signal = []


def getdata(stock, ma_1, ma_2, vma):
    attempts = 3
    while True:
        cdata = {
            "symbol": stock,
            "resolution": "30",
            "date_format": "1",
            "range_from": range_from,
            "range_to": today_str,
            "cont_flag": "0",
        }
        response = fyers.history(data=cdata)
        if "candles" in response:
            break
        if attempts == 0:
            break
        attempts -= 1
        print(response)
        print(stock)
        time.sleep(0.5)
    data = pd.DataFrame.from_dict(response["candles"])
    cols = ["datetime", "open", "high", "low", "close", "volume"]
    data.columns = cols
    data["datetime"] = (
        pd.to_datetime(data["datetime"], unit="s")
        .dt.tz_localize("utc")
        .dt.tz_convert("Asia/Kolkata")
        .dt.tz_localize(None)
    )
    data = data.set_index("datetime")
    data[f"ema-{ma_1}"] = data.ta.ema(ma_1)
    data[f"ema-{ma_2}"] = data.ta.ema(ma_2)
    data["rsi"] = data.ta.rsi(14)
    data[f"volEma{vma}"] = data[["volume"]].rolling(vma).mean()
    data["return"] = ((data["close"] - data["close"].shift(1)) / data["close"]) * 100

    data.dropna(inplace=True)

    stock_hist_data.update({stock: data.tail(7)})


def update_data():
    for stock in stocks:
        getdata(stock, 75, 85, 7)


update_data()

logging.info("Data updated")


def send_telegram_message(symbol, buy_price, target_price, sl_price):
    message = f"SYMBOL {symbol.replace('&', ' ')}, BUY: {buy_price}, TARGET = {target_price}, STOP-LOSS = {sl_price}, DATE-TIME = {datetime.now()}"
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_API_TOKEN}/sendMessage?chat_id={int(Config.TELEGRAM_CHAT_ID)}&text={message}"
    requests.get(url).json()
    logging.info("Message sent")


def onmessage(msg):
    """
    Callback function to handle incoming msgs from the FyersDataSocket WebSocket.

    Parameters:
        msg (dict): The received msg from the WebSocket.

    """
    t = time.localtime()
    chour, cmin, csec = (
        time.strftime("%H", t),
        time.strftime("%M", t),
        time.strftime("%S", t),
    )
    condition = (
        (int(cmin) % 15 == 0 or int(cmin) % 45 == 0)
        and (int(cmin) != 30)
        and (int(cmin) != 0)
    ) and (int(csec) < 2)
    if condition:
        print("30 ema data updated", f"{chour}:", f"{cmin}:", f"{csec}")
        update_data()
        time.sleep(2)

    symbol = msg.get("symbol")
    if symbol:
        stk_data = stock_hist_data.get(symbol)
        prev_close_price = stk_data["close"].iloc[-2]
        prev_volume = stk_data["volume"].iloc[-2]

        condi1 = (prev_close_price > stk_data["ema-75"].iloc[-2]) and (
            prev_close_price > stk_data["ema-85"].iloc[-2]
        )  # prev candle close above ema
        condi2 = (prev_volume > stk_data["volume"].iloc[-3]) and (
            prev_volume > stk_data["volEma7"].iloc[-2]
        )  # avg vol and prev volum higher
        condi3 = (stk_data["close"].iloc[-3] < stk_data["ema-75"].iloc[-3]) and (
            stk_data["close"].iloc[-3] < stk_data["ema-85"].iloc[-3]
        )  # prevOfprv candle close belove ema
        condi4 = (
            (prev_close_price - stk_data["open"].iloc[-2])
            / (stk_data["high"].iloc[-2] - stk_data["low"].iloc[-2])
        ) > 0.6  # candle has more than 60% body

        if condi1 and condi2 and condi3 and condi4:
            if str(symbol) not in stocks_to_buy:
                stocks_to_buy.append(str(symbol))
                print("Buy: ", str(symbol))

        for stock in [s for s in stocks_to_buy if s == symbol]:
            if (
                (stock == str(symbol))
                and (float(msg.get("ltp")) < float(stk_data["low"].iloc[-2]))
                and (str(symbol) not in stock_signal)
            ):
                stocks_to_buy.remove(symbol)
            if (
                (stock == str(symbol))
                and (float(msg.get("ltp")) > float(stk_data["high"].iloc[-2]))
                and (str(symbol) not in stock_signal)
            ):
                stock_signal.append(str(symbol))
                buy = round(float(msg.get("ltp")), 2)
                sl = round(
                    float(stk_data["low"].iloc[-2])
                    - (float(stk_data["low"].iloc[-2]) * 0.005),
                    2,
                )
                target = round(buy + ((buy - sl) * 2), 2)
                send_telegram_message(
                    symbol=symbol, buy_price=buy, target_price=target, sl_price=sl
                )
    else:
        print("Response:", msg)


def onerror(message):
    """
    Callback function to handle WebSocket errors.

    Parameters:
        message (dict): The error message received from the WebSocket.


    """
    print("Error:", message)


def onclose(message):
    """
    Callback function to handle WebSocket connection close events.
    """
    print("Connection closed:", message)


def onopen():
    """
    Callback function to subscribe to data type and symbols upon WebSocket connection.

    """
    # Specify the data type and symbols you want to subscribe to
    data_type = "SymbolUpdate"

    # Subscribe to the specified symbols and data type
    symbols = stocks
    fyers_ws.subscribe(symbols=symbols, data_type=data_type)

    # Keep the socket running to receive real-time data
    fyers_ws.keep_running()


# Create a FyersDataSocket instance with the provided parameters
fyers_ws = data_ws.FyersDataSocket(
    access_token=token,  # Access token in the format "appid:accesstoken"
    log_path="",  # Path to save logs. Leave empty to auto-create logs in the current directory.
    litemode=False,  # Lite mode disabled. Set to True if you want a lite response.
    write_to_file=False,  # Save response in a log file instead of printing it.
    reconnect=True,  # Enable auto-reconnection to WebSocket on disconnection.
    on_connect=onopen,  # Callback function to subscribe to data upon connection.
    on_close=onclose,  # Callback function to handle WebSocket connection close events.
    on_error=onerror,  # Callback function to handle WebSocket errors.
    on_message=onmessage,  # Callback function to handle incoming messages from the WebSocket.
)


def app():
    # Establish a connection to the Fyers WebSocket
    fyers_ws.connect()
