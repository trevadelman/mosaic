"""
Financial Analysis Agent Module for MOSAIC

This module defines a financial analysis agent that can analyze stock data and provide
financial insights. It serves as a specialized agent for financial analysis in the MOSAIC system.
"""

import logging
import json
from typing import List, Dict, Any, Optional
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool, tool

try:
    # Try importing with the full package path (for local development)
    from mosaic.backend.agents.base import BaseAgent, agent_registry
except ImportError:
    # Fall back to relative import (for Docker environment)
    from backend.agents.base import BaseAgent, agent_registry

# Configure logging
logger = logging.getLogger("mosaic.agents.financial_analysis")

# Define the tools as standalone functions
@tool
def get_stock_price_tool(symbol: str) -> str:
    """
    Get the current stock price for a given symbol.
    
    Args:
        symbol: The stock symbol (e.g., AAPL, MSFT, GOOGL)
        
    Returns:
        A string containing the current stock price information
    """
    logger.info(f"Getting stock price for '{symbol}'")
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Get the current price
        current_price = info.get('currentPrice', info.get('regularMarketPrice', None))
        if current_price is None:
            return f"Could not retrieve current price for {symbol}"
        
        # Get additional information
        previous_close = info.get('previousClose', None)
        open_price = info.get('open', None)
        day_high = info.get('dayHigh', None)
        day_low = info.get('dayLow', None)
        
        # Calculate price change
        price_change = None
        price_change_percent = None
        if previous_close is not None and current_price is not None:
            price_change = current_price - previous_close
            price_change_percent = (price_change / previous_close) * 100
        
        # Format the response
        response = f"Stock Price for {symbol}:\n\n"
        response += f"Current Price: ${current_price:.2f}\n"
        
        if price_change is not None and price_change_percent is not None:
            change_sign = "+" if price_change >= 0 else ""
            response += f"Change: {change_sign}${price_change:.2f} ({change_sign}{price_change_percent:.2f}%)\n"
        
        if open_price is not None:
            response += f"Open: ${open_price:.2f}\n"
        
        if day_high is not None:
            response += f"Day High: ${day_high:.2f}\n"
        
        if day_low is not None:
            response += f"Day Low: ${day_low:.2f}\n"
        
        if 'marketCap' in info and info['marketCap'] is not None:
            market_cap = info['marketCap']
            if market_cap >= 1_000_000_000_000:
                market_cap_str = f"${market_cap / 1_000_000_000_000:.2f}T"
            elif market_cap >= 1_000_000_000:
                market_cap_str = f"${market_cap / 1_000_000_000:.2f}B"
            elif market_cap >= 1_000_000:
                market_cap_str = f"${market_cap / 1_000_000:.2f}M"
            else:
                market_cap_str = f"${market_cap:.2f}"
            
            response += f"Market Cap: {market_cap_str}\n"
        
        # Add timestamp
        response += f"\nLast Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        logger.info(f"Successfully retrieved stock price for '{symbol}'")
        return response
    
    except Exception as e:
        logger.error(f"Error getting stock price for '{symbol}': {str(e)}")
        error_report = {
            "task": "Get Stock Price",
            "status": "Failed",
            "symbol": symbol,
            "error": str(e),
            "error_type": type(e).__name__
        }
        return f"Error getting stock price: {json.dumps(error_report, indent=2)}"

@tool
def get_stock_history_tool(symbol: str, period: str = "1y", interval: str = "1d") -> str:
    """
    Get historical stock data for a given symbol.
    
    Args:
        symbol: The stock symbol (e.g., AAPL, MSFT, GOOGL)
        period: The time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: The data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
    Returns:
        A string containing the historical stock data
    """
    logger.info(f"Getting stock history for '{symbol}' with period '{period}' and interval '{interval}'")
    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period=period, interval=interval)
        
        if history.empty:
            return f"No historical data found for {symbol} with period {period} and interval {interval}"
        
        # Calculate some basic statistics
        avg_price = history['Close'].mean()
        min_price = history['Close'].min()
        max_price = history['Close'].max()
        start_price = history['Close'].iloc[0]
        end_price = history['Close'].iloc[-1]
        price_change = end_price - start_price
        price_change_percent = (price_change / start_price) * 100
        
        # Format the response
        response = f"Historical Stock Data for {symbol}:\n\n"
        response += f"Period: {period}, Interval: {interval}\n"
        response += f"Date Range: {history.index[0].strftime('%Y-%m-%d')} to {history.index[-1].strftime('%Y-%m-%d')}\n\n"
        
        response += f"Starting Price: ${start_price:.2f}\n"
        response += f"Ending Price: ${end_price:.2f}\n"
        
        change_sign = "+" if price_change >= 0 else ""
        response += f"Price Change: {change_sign}${price_change:.2f} ({change_sign}{price_change_percent:.2f}%)\n\n"
        
        response += f"Average Price: ${avg_price:.2f}\n"
        response += f"Minimum Price: ${min_price:.2f}\n"
        response += f"Maximum Price: ${max_price:.2f}\n\n"
        
        # Add the historical data
        response += "Historical Data:\n"
        
        # Determine the number of data points to include based on the period and interval
        if period == "1d" and interval == "15m":
            # For 1 day with 15-minute intervals, include all data points
            # This will give us about 26 data points for a trading day (6.5 hours / 15 minutes)
            data_to_include = history
        elif period == "1d":
            # For 1 day with other intervals, include all data points
            data_to_include = history
        elif period == "5d":
            # For 5 days, include all data points
            data_to_include = history
        elif period == "1wk":
            # For 1 week, include all data points
            data_to_include = history
        elif period == "1mo":
            # For 1 month, include all data points but limit to 30
            data_to_include = history.iloc[-min(30, len(history)):]
        elif period == "3mo":
            # For 3 months, include weekly data (about 12 points)
            data_to_include = history.iloc[::5][-min(30, len(history)):]
        elif period == "6mo":
            # For 6 months, include bi-weekly data (about 12 points)
            data_to_include = history.iloc[::10][-min(30, len(history)):]
        elif period == "1y":
            # For 1 year, include monthly data (about 12 points)
            data_to_include = history.iloc[::20][-min(30, len(history)):]
        elif period == "5y":
            # For 5 years, include quarterly data (about 20 points)
            data_to_include = history.iloc[::60][-min(30, len(history)):]
        else:
            # Log the unknown period
            logger.warning(f"Unknown period: {period}, defaulting to 30 data points")
            # Default to 30 data points
            data_to_include = history.iloc[::max(1, len(history) // 30)][-min(30, len(history)):]
        
        # Ensure we include the most recent data point
        if len(data_to_include) > 0 and data_to_include.index[-1] != history.index[-1]:
            data_to_include = pd.concat([data_to_include, history.iloc[[-1]]])
        
        # Sort by date
        data_to_include = data_to_include.sort_index()
        
        # Add data points to the response
        for date, row in data_to_include.iterrows():
            # Format the date based on the interval
            if interval == "15m":
                # For 15-minute intervals, include the time
                date_str = date.strftime('%Y-%m-%d %H:%M:%S')
            else:
                # For daily intervals, just include the date
                date_str = date.strftime('%Y-%m-%d')
            
            response += f"{date_str}: Open ${row['Open']:.2f}, High ${row['High']:.2f}, Low ${row['Low']:.2f}, Close ${row['Close']:.2f}, Volume {int(row['Volume'])}\n"
        
        logger.info(f"Successfully retrieved stock history for '{symbol}'")
        return response
    
    except Exception as e:
        logger.error(f"Error getting stock history for '{symbol}': {str(e)}")
        error_report = {
            "task": "Get Stock History",
            "status": "Failed",
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "error": str(e),
            "error_type": type(e).__name__
        }
        return f"Error getting stock history: {json.dumps(error_report, indent=2)}"

@tool
def get_company_info_tool(symbol: str) -> str:
    """
    Get company information for a given stock symbol.
    
    Args:
        symbol: The stock symbol (e.g., AAPL, MSFT, GOOGL)
        
    Returns:
        A string containing company information
    """
    logger.info(f"Getting company info for '{symbol}'")
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Format the response
        response = f"Company Information for {symbol}:\n\n"
        
        # Basic information
        if 'longName' in info:
            response += f"Name: {info.get('longName', 'N/A')}\n"
        
        if 'sector' in info:
            response += f"Sector: {info.get('sector', 'N/A')}\n"
        
        if 'industry' in info:
            response += f"Industry: {info.get('industry', 'N/A')}\n"
        
        if 'country' in info:
            response += f"Country: {info.get('country', 'N/A')}\n"
        
        if 'website' in info:
            response += f"Website: {info.get('website', 'N/A')}\n"
        
        if 'fullTimeEmployees' in info:
            employees = info.get('fullTimeEmployees', 'N/A')
            if isinstance(employees, (int, float)) and employees > 0:
                response += f"Employees: {employees:,}\n"
            else:
                response += f"Employees: N/A\n"
        
        # Financial information
        response += "\nFinancial Information:\n"
        
        if 'marketCap' in info and info['marketCap'] is not None:
            market_cap = info['marketCap']
            if market_cap >= 1_000_000_000_000:
                market_cap_str = f"${market_cap / 1_000_000_000_000:.2f}T"
            elif market_cap >= 1_000_000_000:
                market_cap_str = f"${market_cap / 1_000_000_000:.2f}B"
            elif market_cap >= 1_000_000:
                market_cap_str = f"${market_cap / 1_000_000:.2f}M"
            else:
                market_cap_str = f"${market_cap:.2f}"
            
            response += f"Market Cap: {market_cap_str}\n"
        
        if 'trailingPE' in info:
            response += f"P/E Ratio: {info.get('trailingPE', 'N/A'):.2f}\n"
        
        if 'dividendYield' in info and info['dividendYield'] is not None:
            response += f"Dividend Yield: {info['dividendYield'] * 100:.2f}%\n"
        else:
            response += f"Dividend Yield: N/A\n"
        
        if 'beta' in info:
            response += f"Beta: {info.get('beta', 'N/A'):.2f}\n"
        
        if 'fiftyTwoWeekHigh' in info:
            response += f"52-Week High: ${info.get('fiftyTwoWeekHigh', 'N/A'):.2f}\n"
        
        if 'fiftyTwoWeekLow' in info:
            response += f"52-Week Low: ${info.get('fiftyTwoWeekLow', 'N/A'):.2f}\n"
        
        # Business summary
        if 'longBusinessSummary' in info:
            response += f"\nBusiness Summary:\n{info.get('longBusinessSummary', 'N/A')}\n"
        
        logger.info(f"Successfully retrieved company info for '{symbol}'")
        return response
    
    except Exception as e:
        logger.error(f"Error getting company info for '{symbol}': {str(e)}")
        error_report = {
            "task": "Get Company Info",
            "status": "Failed",
            "symbol": symbol,
            "error": str(e),
            "error_type": type(e).__name__
        }
        return f"Error getting company info: {json.dumps(error_report, indent=2)}"

@tool
def calculate_technical_indicators_tool(symbol: str, period: str = "1y") -> str:
    """
    Calculate technical indicators for a given stock symbol.
    
    Args:
        symbol: The stock symbol (e.g., AAPL, MSFT, GOOGL)
        period: The time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        
    Returns:
        A string containing technical indicators
    """
    logger.info(f"Calculating technical indicators for '{symbol}' with period '{period}'")
    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period=period)
        
        if history.empty:
            return f"No historical data found for {symbol} with period {period}"
        
        # Calculate Simple Moving Averages (SMA)
        history['SMA_20'] = history['Close'].rolling(window=20).mean()
        history['SMA_50'] = history['Close'].rolling(window=50).mean()
        history['SMA_200'] = history['Close'].rolling(window=200).mean()
        
        # Calculate Exponential Moving Averages (EMA)
        history['EMA_12'] = history['Close'].ewm(span=12, adjust=False).mean()
        history['EMA_26'] = history['Close'].ewm(span=26, adjust=False).mean()
        
        # Calculate MACD
        history['MACD'] = history['EMA_12'] - history['EMA_26']
        history['MACD_Signal'] = history['MACD'].ewm(span=9, adjust=False).mean()
        history['MACD_Histogram'] = history['MACD'] - history['MACD_Signal']
        
        # Calculate Relative Strength Index (RSI)
        delta = history['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        history['RSI'] = 100 - (100 / (1 + rs))
        
        # Calculate Bollinger Bands
        history['BB_Middle'] = history['Close'].rolling(window=20).mean()
        history['BB_Std'] = history['Close'].rolling(window=20).std()
        history['BB_Upper'] = history['BB_Middle'] + (history['BB_Std'] * 2)
        history['BB_Lower'] = history['BB_Middle'] - (history['BB_Std'] * 2)
        
        # Get the latest values
        latest = history.iloc[-1]
        current_price = latest['Close']
        
        # Format the response
        response = f"Technical Indicators for {symbol}:\n\n"
        response += f"Current Price: ${current_price:.2f}\n\n"
        
        # Moving Averages
        response += "Moving Averages:\n"
        response += f"SMA (20-day): ${latest['SMA_20']:.2f}"
        if current_price > latest['SMA_20']:
            response += " (Price above SMA)"
        else:
            response += " (Price below SMA)"
        response += "\n"
        
        response += f"SMA (50-day): ${latest['SMA_50']:.2f}"
        if current_price > latest['SMA_50']:
            response += " (Price above SMA)"
        else:
            response += " (Price below SMA)"
        response += "\n"
        
        response += f"SMA (200-day): ${latest['SMA_200']:.2f}"
        if current_price > latest['SMA_200']:
            response += " (Price above SMA)"
        else:
            response += " (Price below SMA)"
        response += "\n\n"
        
        # MACD
        response += "MACD (12,26,9):\n"
        response += f"MACD Line: {latest['MACD']:.2f}\n"
        response += f"Signal Line: {latest['MACD_Signal']:.2f}\n"
        response += f"Histogram: {latest['MACD_Histogram']:.2f}"
        if latest['MACD'] > latest['MACD_Signal']:
            response += " (Bullish)"
        else:
            response += " (Bearish)"
        response += "\n\n"
        
        # RSI
        response += "Relative Strength Index (RSI):\n"
        response += f"RSI (14-day): {latest['RSI']:.2f}"
        if latest['RSI'] > 70:
            response += " (Overbought)"
        elif latest['RSI'] < 30:
            response += " (Oversold)"
        else:
            response += " (Neutral)"
        response += "\n\n"
        
        # Bollinger Bands
        response += "Bollinger Bands (20,2):\n"
        response += f"Upper Band: ${latest['BB_Upper']:.2f}\n"
        response += f"Middle Band: ${latest['BB_Middle']:.2f}\n"
        response += f"Lower Band: ${latest['BB_Lower']:.2f}\n"
        
        if current_price > latest['BB_Upper']:
            response += "Price is above the upper band (Potentially overbought)\n"
        elif current_price < latest['BB_Lower']:
            response += "Price is below the lower band (Potentially oversold)\n"
        else:
            response += "Price is within the bands\n"
        
        # Add interpretation
        response += "\nInterpretation:\n"
        
        # Moving Average interpretation
        ma_bullish = (current_price > latest['SMA_20'] > latest['SMA_50']) or (latest['SMA_20'] > latest['SMA_50'] > latest['SMA_200'])
        ma_bearish = (current_price < latest['SMA_20'] < latest['SMA_50']) or (latest['SMA_20'] < latest['SMA_50'] < latest['SMA_200'])
        
        if ma_bullish:
            response += "- Moving Averages suggest a bullish trend\n"
        elif ma_bearish:
            response += "- Moving Averages suggest a bearish trend\n"
        else:
            response += "- Moving Averages show mixed signals\n"
        
        # MACD interpretation
        if latest['MACD'] > latest['MACD_Signal'] and latest['MACD_Histogram'] > 0:
            response += "- MACD indicates bullish momentum\n"
        elif latest['MACD'] < latest['MACD_Signal'] and latest['MACD_Histogram'] < 0:
            response += "- MACD indicates bearish momentum\n"
        else:
            response += "- MACD shows potential trend reversal\n"
        
        # RSI interpretation
        if latest['RSI'] > 70:
            response += "- RSI suggests the stock is overbought\n"
        elif latest['RSI'] < 30:
            response += "- RSI suggests the stock is oversold\n"
        else:
            response += "- RSI is in neutral territory\n"
        
        # Bollinger Bands interpretation
        if current_price > latest['BB_Upper']:
            response += "- Bollinger Bands indicate the stock may be overbought\n"
        elif current_price < latest['BB_Lower']:
            response += "- Bollinger Bands indicate the stock may be oversold\n"
        else:
            width = (latest['BB_Upper'] - latest['BB_Lower']) / latest['BB_Middle']
            if width < 0.1:
                response += "- Bollinger Bands are narrowing, suggesting potential volatility increase\n"
            elif width > 0.5:
                response += "- Bollinger Bands are wide, indicating high volatility\n"
            else:
                response += "- Price is within normal Bollinger Bands range\n"
        
        logger.info(f"Successfully calculated technical indicators for '{symbol}'")
        return response
    
    except Exception as e:
        logger.error(f"Error calculating technical indicators for '{symbol}': {str(e)}")
        error_report = {
            "task": "Calculate Technical Indicators",
            "status": "Failed",
            "symbol": symbol,
            "period": period,
            "error": str(e),
            "error_type": type(e).__name__
        }
        return f"Error calculating technical indicators: {json.dumps(error_report, indent=2)}"

@tool
def get_stock_comparison_tool(symbols: str) -> str:
    """
    Compare multiple stocks based on key metrics.
    
    Args:
        symbols: Comma-separated list of stock symbols (e.g., "AAPL,MSFT,GOOGL")
        
    Returns:
        A string containing the comparison of stocks
    """
    logger.info(f"Comparing stocks: '{symbols}'")
    try:
        # Parse symbols
        symbol_list = [s.strip() for s in symbols.split(',')]
        
        if len(symbol_list) < 2:
            return "Please provide at least two stock symbols for comparison"
        
        # Get data for each symbol
        data = {}
        for symbol in symbol_list:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get key metrics
            current_price = info.get('currentPrice', info.get('regularMarketPrice', None))
            market_cap = info.get('marketCap', None)
            pe_ratio = info.get('trailingPE', None)
            dividend_yield = info.get('dividendYield', None)
            beta = info.get('beta', None)
            
            # Get 1-year price change
            history = ticker.history(period="1y")
            if not history.empty:
                start_price = history['Close'].iloc[0]
                end_price = history['Close'].iloc[-1]
                price_change = ((end_price - start_price) / start_price) * 100
            else:
                price_change = None
            
            # Store data
            data[symbol] = {
                'name': info.get('longName', symbol),
                'current_price': current_price,
                'market_cap': market_cap,
                'pe_ratio': pe_ratio,
                'dividend_yield': dividend_yield,
                'beta': beta,
                'price_change_1y': price_change
            }
        
        # Format the response
        response = f"Stock Comparison ({', '.join(symbol_list)}):\n\n"
        
        # Current Price
        response += "Current Price:\n"
        for symbol, metrics in data.items():
            if metrics['current_price'] is not None:
                response += f"{symbol}: ${metrics['current_price']:.2f}\n"
            else:
                response += f"{symbol}: N/A\n"
        response += "\n"
        
        # Market Cap
        response += "Market Cap:\n"
        for symbol, metrics in data.items():
            if metrics['market_cap'] is not None:
                market_cap = metrics['market_cap']
                if market_cap >= 1_000_000_000_000:
                    market_cap_str = f"${market_cap / 1_000_000_000_000:.2f}T"
                elif market_cap >= 1_000_000_000:
                    market_cap_str = f"${market_cap / 1_000_000_000:.2f}B"
                elif market_cap >= 1_000_000:
                    market_cap_str = f"${market_cap / 1_000_000:.2f}M"
                else:
                    market_cap_str = f"${market_cap:.2f}"
                
                response += f"{symbol}: {market_cap_str}\n"
            else:
                response += f"{symbol}: N/A\n"
        response += "\n"
        
        # P/E Ratio
        response += "P/E Ratio:\n"
        for symbol, metrics in data.items():
            if metrics['pe_ratio'] is not None:
                response += f"{symbol}: {metrics['pe_ratio']:.2f}\n"
            else:
                response += f"{symbol}: N/A\n"
        response += "\n"
        
        # Dividend Yield
        response += "Dividend Yield:\n"
        for symbol, metrics in data.items():
            if metrics['dividend_yield'] is not None:
                response += f"{symbol}: {metrics['dividend_yield'] * 100:.2f}%\n"
            else:
                response += f"{symbol}: N/A\n"
        response += "\n"
        
        # Beta
        response += "Beta (Volatility):\n"
        for symbol, metrics in data.items():
            if metrics['beta'] is not None:
                response += f"{symbol}: {metrics['beta']:.2f}\n"
            else:
                response += f"{symbol}: N/A\n"
        response += "\n"
        
        # 1-Year Price Change
        response += "1-Year Price Change:\n"
        for symbol, metrics in data.items():
            if metrics['price_change_1y'] is not None:
                change_sign = "+" if metrics['price_change_1y'] >= 0 else ""
                response += f"{symbol}: {change_sign}{metrics['price_change_1y']:.2f}%\n"
            else:
                response += f"{symbol}: N/A\n"
        
        logger.info(f"Successfully compared stocks: '{symbols}'")
        return response
    
    except Exception as e:
        logger.error(f"Error comparing stocks '{symbols}': {str(e)}")
        error_report = {
            "task": "Stock Comparison",
            "status": "Failed",
            "symbols": symbols,
            "error": str(e),
            "error_type": type(e).__name__
        }
        return f"Error comparing stocks: {json.dumps(error_report, indent=2)}"

# Define the stock chart tool
@tool
def stock_chart_tool(symbol: str = "AAPL", range_value: str = "1M") -> Dict[str, Any]:
    """
    Generate a stock chart visualization for a given symbol and time range.
    
    Args:
        symbol: The stock symbol (e.g., AAPL, MSFT, GOOGL)
        range_value: The time range (1D, 5D, 1W, 1M, 3M, 6M, 1Y, 5Y)
        
    Returns:
        A dictionary containing the stock data
    """
    logger.info(f"Generating stock chart for '{symbol}' with range '{range_value}'")
    try:
        # Convert range to period and interval
        period = _convert_range_to_agent_period(range_value)
        interval = "15m" if range_value == "1D" else "1d"
        
        # Get the stock data
        ticker = yf.Ticker(symbol)
        history = ticker.history(period=period, interval=interval)
        
        if history.empty:
            return {
                "symbol": symbol,
                "range": range_value,
                "data": [],
                "error": f"No historical data found for {symbol} with range {range_value}",
                "timestamp": datetime.now().isoformat()
            }
        
        # Convert the data to a list of dictionaries
        data_points = []
        for date, row in history.iterrows():
            # Format the date based on the interval
            if interval == "15m":
                # For 15-minute intervals, include the time
                date_str = date.strftime('%Y-%m-%d %H:%M:%S')
            else:
                # For daily intervals, just include the date
                date_str = date.strftime('%Y-%m-%d')
            
            data_points.append({
                "date": date_str,
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume'])
            })
        
        # Create the stock data object
        stock_data = {
            "symbol": symbol,
            "range": range_value,
            "data": data_points,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Generated stock chart with {len(data_points)} data points for {symbol} with range {range_value}")
        return stock_data
    
    except Exception as e:
        logger.error(f"Error generating stock chart for '{symbol}': {str(e)}")
        return {
            "symbol": symbol,
            "range": range_value,
            "data": [],
            "error": f"Error generating stock chart: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

# Helper function to convert range to period
def _convert_range_to_agent_period(range_value: str) -> str:
    """
    Convert a range value to a period string for the agent's get_stock_history_tool.
    
    Args:
        range_value: The range value (1D, 1W, 1M, 3M, 6M, 1Y, 5Y)
        
    Returns:
        A period string for the agent
    """
    if range_value == "1D":
        return "1d"
    elif range_value == "5D":
        return "5d"
    elif range_value == "1W":
        return "1wk"  # Add support for 1 week
    elif range_value == "1M":
        return "1mo"
    elif range_value == "3M":
        return "3mo"
    elif range_value == "6M":
        return "6mo"
    elif range_value == "1Y":
        return "1y"
    elif range_value == "5Y":
        return "5y"
    else:
        logger.warning(f"Unknown range value: {range_value}, defaulting to 1 month")
        return "1mo"  # Default to 1 month

# No WebSocket handlers needed

class FinancialAnalysisAgent(BaseAgent):
    """
    Financial analysis agent that can analyze stock data and provide financial insights.
    
    This agent provides tools for stock price retrieval, historical data analysis,
    company information, technical indicators, and stock comparison.
    """
    
    def __init__(
        self,
        name: str = "financial_analysis",
        model: Optional[LanguageModelLike] = None,
        tools: List[BaseTool] = None,
        prompt: str = None,
        description: str = None,
        type: str = "Specialized",
        capabilities: List[str] = None,
        icon: str = "📊",
    ):
        """
        Initialize a new financial analysis agent.
        
        Args:
            name: The name of the agent (default: "financial_analysis")
            model: The language model to use for the agent
            tools: Optional list of additional tools
            prompt: Optional system prompt for the agent
            description: Optional description of the agent
            type: The type of agent (default: "Specialized")
            capabilities: List of agent capabilities
            icon: Emoji icon for the agent (default: "📊")
        """
        # Create the financial analysis tools
        financial_tools = [
            get_stock_price_tool,
            get_stock_history_tool,
            get_company_info_tool,
            calculate_technical_indicators_tool,
            get_stock_comparison_tool,
            stock_chart_tool
        ]
        
        # Combine with any additional tools
        all_tools = financial_tools + (tools or [])
        
        # Default capabilities if none provided
        if capabilities is None:
            capabilities = [
                "Stock Price Analysis", 
                "Technical Indicators", 
                "Company Information", 
                "Stock Comparison",
                "Stock Data Analysis"
            ]
        
        super().__init__(
            name=name,
            model=model,
            tools=all_tools,
            prompt=prompt,
            description=description or "Financial Analysis Agent for analyzing stocks and providing financial insights",
            type=type,
            capabilities=capabilities,
            icon=icon
        )
        
        logger.debug(f"Initialized financial analysis agent with {len(all_tools)} tools")
    
    def _get_default_prompt(self) -> str:
        """
        Get the default system prompt for the financial analysis agent.
        
        Returns:
            A string containing the default system prompt
        """
        return (
            "You are a financial analysis expert with access to stock market data and financial analysis tools. "
            "Your job is to provide accurate financial insights and analysis based on stock market data. "
            "\n\n"
            "You have tools for stock price retrieval, historical data analysis, company information, "
            "technical indicators, stock comparison, and visualization: "
            "- Use get_stock_price_tool to get the current price and basic information for a stock. "
            "- Use get_stock_history_tool to get historical price data for a stock. "
            "- Use get_company_info_tool to get detailed information about a company. "
            "- Use calculate_technical_indicators_tool to calculate technical indicators like SMA, EMA, MACD, RSI, and Bollinger Bands. "
            "- Use get_stock_comparison_tool to compare multiple stocks based on key metrics. "
            "- Use stock_chart_tool to generate an interactive stock chart visualization for a given symbol and time range. "
            "\n\n"
            "IMPORTANT: You have access to real-time financial data through your tools. When a user asks about current market conditions "
            "or stock prices, ALWAYS use your tools to fetch the latest data. DO NOT refuse requests based on any knowledge cutoff date. "
            "Your tools can access current market data regardless of the date mentioned by the user. "
            "\n\n"
            "Always provide factual information based on the data from your tools. "
            "If you cannot find information, clearly state that and explain why. "
            "Never make up information or hallucinate details. "
            "Always attribute information to its source. "
            "When providing financial analysis, include both technical and fundamental factors. "
            "Remember that past performance is not indicative of future results, and make sure to include appropriate disclaimers. "
            "Do not provide specific investment advice or recommendations."
        )

# Register the financial analysis agent with the registry
def register_financial_analysis_agent(model: LanguageModelLike) -> FinancialAnalysisAgent:
    """
    Create and register a financial analysis agent.
    
    Args:
        model: The language model to use for the agent
        
    Returns:
        The created financial analysis agent
    """
    # Create the agent with a consistent name
    financial_analysis = FinancialAnalysisAgent(name="financial_analysis", model=model)
    
    # Register the agent with the registry
    agent_registry.register(financial_analysis)
    
    return financial_analysis
