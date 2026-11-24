import logging
import yfinance as yf
from django.core.cache import cache
from .models import Stock

# Set up a logger for this module
logger = logging.getLogger(__name__)

# dictionary to map symbols to display names
COMPANIES = {
    "^GSPC": "S&P 500",
    "^DJI": "Dow Jones",
    "^IXIC": "Nasdaq",
    "^RUT": "Russell 2000",
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOG": "Alphabet",
    "NVDA": "Nvidia",
}


# function allows for either a custom list or defaults to a predefined set of symbols
def get_market_snapshot(symbols=None):
    """
    Fetches market snapshot data for the given symbols using yfinance.
    Caches the result for 5 minutes to reduce API calls.
    """
    if symbols is None:
        symbols = ["^GSPC", "^DJI", "^IXIC", "^RUT", "AAPL", "MSFT", "GOOG", "NVDA"]

    # Normalize order and casing so identical symbol sets share a cache key
    normalized_symbols = [s.strip().upper() for s in symbols]
    clean_key = "_".join(sorted(normalized_symbols)).replace("^", "IDX_")
    cache_key = f"market_snapshot_{clean_key}"

    # Check if the data is already cached
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        by_symbol = {item["ticker_code"]: item for item in cached_data}
        return [by_symbol[s] for s in normalized_symbols if s in by_symbol]

    results = []

    # joins the list into a single space-separated string for yfinance
    tickers = yf.Tickers(" ".join(normalized_symbols))

    for symbol in normalized_symbols:
        company = COMPANIES.get(
            symbol, symbol
        )  # Look up display name or default to symbol

        # wraps the data extraction in an error handler because yfinace can frequently throw exceptions on bad tickers or network timeouts
        try:
            fi = tickers.tickers[
                symbol
            ].fast_info  # Use fast_info for quicker access to price data
            price = fi.last_price
            prev_close = fi.previous_close

            # Verifies both numberes exist and prev_close isn't zero to avoid ZeroDivisionError
            if price is not None and prev_close:
                change = price - prev_close
                pct_change = (change / prev_close) * 100

                results.append(
                    {
                        "company": company,
                        "display_name": company,
                        "ticker_code": symbol,
                        "price": f"{price:,.2f}",
                        "change": f"{change:+,.2f}",  # Adds '+' sign for positive gains
                        "pct_change": f"{pct_change:+,.2f}",
                        "is_positive": change >= 0,
                        "error": False,
                    }
                )

            else:
                # runs if yfinance returned None for the price flagging item as an error
                logger.warning("Price data missing for %s", symbol)
                results.append(
                    {"company": company, "ticker_code": symbol, "error": True}
                )

        # runs if yfinance throws an exception, logs the error, and flags the item as an error
        except Exception as e:
            logger.warning("Error fetching %s: %s", symbol, e)
            results.append({"company": company, "ticker_code": symbol, "error": True})

    # checks if at least one ticker succeeded before caching the results to avoid caching a full error response
    if any(not item["error"] for item in results):
        cache.set(cache_key, results, timeout=300)

    return results


def attach_asset_types(rows):
    symbols = [row["ticker_code"] for row in rows]
    stored = dict(
        Stock.objects.filter(ticker_code__in=symbols).values_list(
            "ticker_code", "asset_type"
        )
    )
    for row in rows:
        code = stored.get(
            row["ticker_code"], Stock.infer_asset_type(row["ticker_code"])
        )
        row["asset_type"] = code
        row["asset_type_label"] = Stock.AssetType(code).label
    return rows
