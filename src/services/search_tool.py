import logging
from ddgs import DDGS

logger = logging.getLogger(__name__)

class SearchTool:
    
    # --------------------------------------------------------------------------
    # TOOL: WEB SEARCH (DuckDuckGo)
    # Used for: EVERYTHING (Facts, Stocks, News, Lore)
    # Why: Single reliable source. The LLM processes the raw text.
    # --------------------------------------------------------------------------
    def search_web(self, query: str, max_results=3):
        """
        Searches the web using DuckDuckGo (Best Effort).
        """
        logger.debug(f"Web Search Query: '{query}'")
        try:
            with DDGS() as ddgs:
                try:
                    results = ddgs.text(query, region='us-en', max_results=max_results, timelimit='w')
                except TypeError:
                    # timelimit parameter may not be supported in some versions
                    results = ddgs.text(query, region='us-en', max_results=max_results)
                
                if not results:
                    return "No web search results found."
                
                summary = ""
                for i, r in enumerate(results):
                    summary += f"{i+1}. {r['title']} ({r.get('href', 'No URL')}): {r['body']}\n"
                return summary
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return f"Web search failed: {e}"

    # --------------------------------------------------------------------------
    # TOOL: STOCK PRICE (YFinance)
    # --------------------------------------------------------------------------
    def get_stock_price(self, ticker: str):
        """
        Fetches current stock price and recent change.
        """
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            info = stock.info
            price = info.get("currentPrice") or info.get("regularMarketPrice")
            currency = info.get("currency", "USD")
            change = info.get("regularMarketChangePercent")
            
            if price:
                return f"Symbol: {ticker}, Current Price: {price} {currency}, Change: {change:.2f}%"
        except ImportError:
            logger.warning("yfinance not installed, falling back to web search")
        except Exception as e:
            logger.warning(f"Stock API failed: {e}, falling back to web search")
            
        return self.search_web(f"{ticker} stock price")

    def get_wiki_summary(self, topic: str):
        """
        Fetches a summary from Wikipedia.
        """
        try:
            import wikipedia
            return wikipedia.summary(topic, sentences=3)
        except ImportError:
            logger.warning("wikipedia package not installed, falling back to web search")
        except Exception as e:
            logger.warning(f"Wikipedia API failed: {e}, falling back to web search")
            
        return self.search_web(f"Who/What is {topic} - wikipedia summary")
