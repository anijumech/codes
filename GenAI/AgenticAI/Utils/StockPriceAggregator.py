from massive import RESTClient
from datetime import datetime, timedelta

def getAggregatedStockPrice(ticker, startDate, endDate):
    client = RESTClient("NfSKB_Sb_4Qm0esmGyfzWUZtqqIx9t0b")

    aggs = []
    for a in client.list_aggs(
            # "AAPL",
            ticker,
            1,
            "day",
            # "2026-08-12",
            startDate,
            # "2026-09-11",
            endDate,
            adjusted="true",
            sort="asc",
            limit=120,
        ):
        aggs.append(a)

    return aggs


def getStockPriceList(startDate, ticker):
    endDate = (datetime.today() - timedelta(days=2)).strftime("%Y-%m-%d")
    aggs = getAggregatedStockPrice(ticker, startDate, endDate)

    stockPriceList = []
    for dailyStockDetail in aggs:
        stockPriceList.append((dailyStockDetail.open,dailyStockDetail.close,dailyStockDetail.high,dailyStockDetail.low))

    # Print the Stock Price List in the format -> list of tupples, each tupple in the format (Open Price, Closing Price, Max Price, Min Price)
    print(stockPriceList)


def main():
    startDate = input("Enter the start data ->")
    ticker = "AAPL"
    getStockPriceList(startDate, ticker)

if __name__ == "__main__":
    main()