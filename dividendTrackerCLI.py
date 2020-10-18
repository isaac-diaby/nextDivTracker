import argparse
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

def getTableRow(T, data, H=0.0 ):
    """
    Place the data for a given ticker in order of the command line tool
    """
    ROW = [T, H]
    lastclose = data['Last Close']
    ROW.append(lastclose)
    exDiv = data['Ex-Dividend Date']
    ROW.append(exDiv)
    PayDate = data['Pay Date']
    ROW.append(PayDate)
    lastDiv = data['Last Dividend']
    ROW.append(lastDiv)
    divYield = data['Dividend Yield']
    ROW.append(divYield)
    peR = data['P/E Ratio']
    ROW.append(peR)
    divCurrency = lastclose[0]
    try:
        Payout = round(float(lastDiv[1:]) * H, 2)
    except ValueError as naError:
        Payout = 0
    
    ROW.append(divCurrency+str(Payout))
    return ROW, Payout

def main():
    """
    The main CLI logic thatwill get the stock data and display the data to the user
    """
    # Define the CLI 
    CLI = argparse.ArgumentParser(fromfile_prefix_chars='@')
    CLI.add_argument("-T", metavar='Tickers', nargs='+', type=str, help='@myTickerList.txt || appl tsla ..', default='aapl ibm'.split())
    CLI.add_argument("-H", metavar='HoldingTickers', nargs='+', type=str, help='@myHoldingList.txt || appl,22 ibm,18 ..')

    # Parse the tickers so that we can get the data
    args = CLI.parse_args() 

    BASE_STOCK_API = "https://dividata.com/stock/"
    TK_DATA = {}
    HOLDINGS_DATA = {}
    # Parse the holdings list if it has been added 
    if args.H:
        for holding in args.H:
            tickerNdAmount = holding.strip().upper().split(',')
            HOLDINGS_DATA[tickerNdAmount[0]] = float(tickerNdAmount[1])

    print("Getting ticker data...")
    for ticker in args.T:
        ticker = ticker.upper()
        r = requests.get(f'{BASE_STOCK_API}{ticker}')
        # Check if the ticker is available 
        if (r.status_code != 200):
            print("SKIP:", ticker, "Res code:", r.status_code )
            pass

        else:
            soup = BeautifulSoup(r.content, 'html.parser')
            fields = soup.find_all('li', class_='list-group-item') # Get the fields from the website

            fields_OBJ = {} 
            for field in fields:
                # Get the field name, value and clean the values
                value = field.find('span').get_text().strip()
                fields_OBJ[field.get_text().strip(value).strip()] = value

            #Save data to the dict, mapped to the ticker
            TK_DATA[ticker] = fields_OBJ 


    # Got the Stock Data now make it displayable
    HEADERS = ['Ticker', 'Holdings', 'Close', 'Ex-Div', 'Pay Date', 'Last Div', 'Div. Yield', 'P/E', 'Next Payout']
    TABLE = []
    PAYOUT_TOTAL = 0

    # Format the data so that it can go into the table
    for ticker in TK_DATA:
        try:
            format_data, NextPayout = getTableRow(ticker, TK_DATA[ticker], HOLDINGS_DATA[ticker])
            PAYOUT_TOTAL += NextPayout
            TABLE.append(format_data)
        except KeyError as noHoldingsProvided:
            format_data, NextPayout = getTableRow(ticker, TK_DATA[ticker])
            TABLE.append(format_data)
    
    # Display the results
    print(tabulate(TABLE, headers=HEADERS, tablefmt="pretty"))
    print(f'Total Payout for next div: £{round(PAYOUT_TOTAL,2)}')
    

if __name__ == "__main__":
    main()