from base64 import b64decode
import logging
import os
import base58
import requests

def validate_token_metrics(metrics):
    """Perform authenticity checks on token metrics."""
    errors = []
    # Logical checks
    if metrics["circulatingSupply"] > 0:
        expected_market_cap = metrics["price"] * metrics["circulatingSupply"]
        if abs(expected_market_cap - metrics["marketCap"]) > 0.05 * expected_market_cap:
            errors.append("Market Cap doesn't match price * circulating supply.")
    
    if metrics["circulatingSupply"] == 0 and metrics["marketCap"] > 0:
        errors.append("Market cap is nonzero but circulating supply is zero.")
    
    if metrics["volatility24h"] > 100:
        errors.append("Volatility is unrealistically high (>100%).")
    
    print(f"print the error", errors)

    return 0.0 if errors else 1.0

def calculate_quality_score(unique_tokens_count):
    """Calculate quality score based on provided token details."""
    logging.info(f"length is {unique_tokens_count} ")

    if 12 <= unique_tokens_count <= 20:
        return 1
    elif 6 <= unique_tokens_count <= 11:
        return unique_tokens_count
    elif 1 <= unique_tokens_count <= 5:
        return 0.1
    else:
        return 0

def calculate_token_metrics(unique_tokens):
    results = []
    valid_chains = {
        "ethereum", "optimistic-ethereum", "cronos", "binance-smart-chain", "xdai", 
        "polygon-pos", "manta-pacific", "x-layer", "opbnb", "fantom", 
        "kucoin-community-chain", "zksync", "merlin-chain", "mantle", "base", 
        "arbitrum-one", "avalanche", "linea", "blast", "bitlayer", 
        "scroll", "zklink-nova", "tron", "vana", "solana"
    }
    
    valid_attributes = {
        "momentum-surge", "high-liquidity", "utility-driven", "backed-by-major-investors",
        "community-powered", "verified-contracts", "disruptive-tech", "major-integrations",
        "limited-supply"
    }
    
    valid_categories = {
        "MemeCoins", "Web3Gaming", "BlueChipDeFi", "AIAgent", "Layer1", "Layer2Layer3", 
        "RWA", "DecentralizedAI", "DecentralizedFinance", "DePIN", "LiquidStakingRestaking", 
        "BlockchainServiceInfra"
    }
    
    for token in unique_tokens:
        token_metadata = token.get("token_metadata", {})
        data_chain = token_metadata.get("chain", "").lower()
        data_contract = token_metadata.get("contract", "")
        metrics = token_metadata.get("metrics", {})
        
        if data_chain not in valid_chains:
            print(f"Skipping token {data_contract}: Invalid chain {data_chain}")
            continue
        
        token_category = token.get("tokenCategory", "")
        if token_category not in valid_categories:
            print(f"Skipping token {data_contract}: Invalid category {token_category}")
            continue
        
        suggestion_attributes = set(token.get("suggestionAttributes", []))
        recommendation_attributes = set(token.get("recommendationAttributes", []))
        has_valid_attributes = bool(suggestion_attributes & valid_attributes or recommendation_attributes & valid_attributes)
        
        individual_authenticity = validate_token_metrics(metrics) if has_valid_attributes else 0
        print(f"individual authenticity is ", individual_authenticity)
        
        data_reason = token.get("reason_recommend", "")
        data_suggestion = token.get("suggestion", "")
        
        individual_quality = 0.5 * (len(data_reason) > 10) + 0.5 * (len(data_suggestion) > 10)
        individual_quality *= individual_authenticity  # Ensure quality is zero if authenticity is zero
        
        results.append({
            "token": data_contract,
            "authenticity": individual_authenticity,
            "quality": individual_quality
        })
    
    return results

def final_scores(unique_tokens):
    """Calculate the average authenticity and quality scores."""
    results = calculate_token_metrics(unique_tokens)
    unique_token_count = len(unique_tokens)
    
    if not results:
        return 0, 0

    quality_avg = calculate_quality_score(unique_token_count)
    authenticity_avg = sum(result["authenticity"] for result in results) / len(results)
    logging.info(f"authenticity_avg: {authenticity_avg}, quality_avg: {quality_avg}, results, {results[0]}")
    return authenticity_avg, quality_avg

# Example of how this would be executed
if __name__ == "__main__":
    # Assuming we have some example unique tokens
    unique_tokens =   [
        {
            "token_metadata": {
                "contract": "0x2170ed0880ac9a755fd29b2688956bd959f933f8",
                "chain": "binance-smart-chain",
                "metrics": {
                    "name": "Binance-Peg WETH",
                    "symbol": "weth",
                    "price": 2123.79,
                    "marketCap": 1290454998,
                    "priceChange24h": -8.5807,
                    "volume24h": 61943274,
                    "circulatingSupply": 604999.999959841,
                    "volatility24h": 12.12,
                    "riskScore": 5,
                    "securityStatus": "Low Risk"
                }
            },
            "reason_recommend": "dwadawdwa",
            "recommendationAttributes": [
                "momentum-surge",
                "backed-by-major-investors",
                "disruptive-tech"
            ],
            "recommendation_time": "2025-02-28T05:11:33.718Z",
            "suggestion": "wdaawdawd",
            "suggestionAttributes": [
                "momentum-surge",
                "backed-by-major-investors",
                "disruptive-tech"
            ],
            "on_chain_analysis": "The token analysis reveals a comprehensive picture of Binance-Peg WETH (WETH), currently priced at $2,123.79 with a market cap of approximately $1.29 billion, placing it at rank 72 within the cryptocurrency market. However, this token has faced significant downward pressure, experiencing an 8.58% decline in the last 24 hours and a 22.75% decrease over the past week. The two-week and two-month signals suggest a persistent downtrend, with the current price standing at 51.82% of its all-time high (ATH) of $4,098.26 reached in December 2024, which indicates a potential concern for investors regarding price recovery. The trading volume of $61.94 million reflects a robust liquidity aspect, emphasizing a solid market cap to volume ratio of 20.83. Although the liquidity situation appears moderate with a sizeable number of trading exchanges (100) facilitating transactions, the lack of Total Value Locked (TVL) data is a drawback.\n\nIn terms of supply dynamics, the token boasts a circulating supply equal to its total supply of about 605,000 WETH, implying a complete circulation. The fully diluted valuation matches the market cap, yielding a market cap to FDV ratio of 1, suggesting no inflation risk under the current supply condition. Social sentiment can be gauged from its robust following on Twitter, with 3.77 million followers, signifying a potentially strong community support; however, detailed metrics from platforms like Reddit and Telegram are absent, making it difficult to accurately assess social engagement levels. Developer activity metrics are also elusive, lacking critical insights from GitHub, which could raise questions regarding the project’s innovation trajectory and support.\n\nThe risk assessment indicates moderate price and liquidity volatility, while the supply concentration risk remains very low, which is a positive sign. However, the high developer activity risk suggests uncertainty in the project’s ongoing development and technical support. Overall, Binance-Peg WETH appears to hold potential due to its established presence in the Binance Smart Chain ecosystem, yet significant concerns over recent price trends and limited developer insights mean that it earns a moderate risk score of 5 out of 10. This suggests that while there are opportunities for growth, there is a clear need for cautious optimism given the current market conditions.",
            "tokenCategory": "MemeCoins"
        },
        {
            "token_metadata": {
                "contract": "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c",
                "chain": "binance-smart-chain",
                "metrics": {
                    "name": "Wrapped BNB",
                    "symbol": "wbnb",
                    "price": 573.38,
                    "marketCap": 698210570,
                    "priceChange24h": -6.3817,
                    "volume24h": 205400439,
                    "circulatingSupply": 1218750.96285504,
                    "volatility24h": 8.64,
                    "riskScore": 2,
                    "securityStatus": "High Risk"
                }
            },
            "reason_recommend": "r3wr3rwr3",
            "recommendationAttributes": [
                "momentum-surge",
                "backed-by-major-investors",
                "disruptive-tech"
            ],
            "recommendation_time": "2025-02-28T05:11:33.718Z",
            "suggestion": "rw3r3wr",
            "suggestionAttributes": [
                "momentum-surge",
                "disruptive-tech",
                "backed-by-major-investors"
            ],
            "on_chain_analysis": "Wrapped BNB (WBNB) is currently priced at $573.38, with a market capitalization of approximately $698.21 million, positioning it at rank 107 in the cryptocurrency market. Over the past 24 hours, the trading volume reached around $205.4 million, reflecting a notable 6.38% decline in price within the same timeframe. The token has faced a downward trend recently, evident from its 30-day price change of -15.24%, although it has gained 44.11% over the past year. The all-time high (ATH) was recorded at $789.32 in December 2024, marking a current price that is 72.64% of that peak, while the all-time low (ATL) of $23.60 affirms an impressive 2329.58% increase from its lowest point. \n\nIn terms of liquidity, WBNB enjoys a robust trading environment, with a volume-to-market cap ratio of 29.42, indicating ample trading activity, and a tight average bid-ask spread of 0.6%. Despite the absence of Total Value Locked (TVL) data, the circulating supply of 1,218,750.96 fully matches its total supply, resulting in a fully diluted valuation equal to its market cap. \n\nSocial engagement data is lacking, and the community metrics on platforms like Twitter and Reddit are unavailable, suggesting potential weaknesses in social sentiment and community interaction. Additionally, developer activity seems to lack transparency, as pertinent metrics from platforms like GitHub are not reported, raising concerns about project sustainability and innovation.\n\nIn terms of risk assessment, WBNB has a low price volatility and liquidity risk but exhibits very high developer activity risk, signaling uncertainty about ongoing development and long-term viability. Combined with a market maturity that remains largely unknown, the overall risk score is assessed at 2 out of 10, indicating moderate risk primarily tied to developer engagement. The unique position of WBNB as a crypto-backed token within the Binance Smart Chain ecosystem presents opportunities, yet its diminished recent price action alongside insufficient developer metrics raises critical concerns worth monitoring closely.",
            "tokenCategory": "MemeCoins"
        },
        {
            "token_metadata": {
                "contract": "0xce7de646e7208a4ef112cb6ed5038fa6cc6b12e3",
                "chain": "binance-smart-chain",
                "metrics": {
                    "name": "TRON (BSC)",
                    "symbol": "trx",
                    "price": 0.217812,
                    "marketCap": 0,
                    "priceChange24h": -4.34506,
                    "volume24h": 297993,
                    "circulatingSupply": 0,
                    "volatility24h": 6.43,
                    "riskScore": 5,
                    "securityStatus": "Low Risk"
                }
            },
            "reason_recommend": "dawdawdw",
            "recommendationAttributes": [
                "backed-by-major-investors",
                "momentum-surge",
                "disruptive-tech"
            ],
            "recommendation_time": "2025-02-28T05:11:33.718Z",
            "suggestion": "dawdwad",
            "suggestionAttributes": [
                "momentum-surge",
                "backed-by-major-investors",
                "disruptive-tech"
            ],
            "on_chain_analysis": "The TRON (BSC) token, symbolized as TRX, is currently priced at $0.217812, reflecting a notable decline of 4.35% over the last 24 hours and a significant drop of 12.66% over the past week. The token exhibits a 24-hour trading volume of $297,993, but lacks available market cap data and a corresponding market cap to volume ratio. Historically, TRX has reached an all-time high of $0.446892 on December 3, 2024, positioning its current price at 48.74% of this peak, while the token has appreciated 380.77% from its all-time low of $0.04530479 on November 14, 2022. Despite demonstrating a 70.28% increase over 200 days and a 51.33% rise annually, recent trends indicate a strong downtrend, with 14-day and 60-day changes both negative. \n\nOn the liquidity front, while specific metrics such as total value locked and the market cap to TVL ratio are unavailable, TRX benefits from a diverse trading ecosystem with 20 exchanges and an average bid-ask spread of 1.11%. The total supply is capped at approximately 295.59 million tokens, with a fully diluted valuation reaching $64.45 million. Social dynamics appear modest, with 3,720 Twitter followers and a Telegram community of 1,073 users, though concrete sentiment metrics are missing. \n\nDeveloper engagement is relatively robust, characterized by 3,530 GitHub stars, a high issue resolution ratio of 98.13%, and consistent activity reflected in 19 commits over the past four weeks, indicating a dedicated development team. The token operates on the Binance Smart Chain, enhancing its appeal within the BNB Chain Ecosystem. However, it faces moderate developer activity risk amidst potential uncertainties in liquidity, supply concentration, and market maturity, culminating in an overall risk score of 5 out of 10. In summary, while TRX shows strengths in historical returns and developer engagement, its current downtrend, liquidity uncertainties, and social engagement need careful monitoring.",
            "tokenCategory": "MemeCoins"
        },
        {
            "token_metadata": {
                "contract": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN",
                "chain": "solana",
                "metrics": {
                    "name": "Official Trump",
                    "symbol": "trump",
                    "price": 11.35,
                    "marketCap": 2274228414,
                    "priceChange24h": -14.3411,
                    "volume24h": 1067934633,
                    "circulatingSupply": 199999978.036,
                    "volatility24h": 20.41,
                    "riskScore": 6,
                    "securityStatus": "Low Risk"
                }
            },
            "reason_recommend": "dwadwad",
            "recommendationAttributes": [
                "momentum-surge",
                "backed-by-major-investors",
                "disruptive-tech"
            ],
            "recommendation_time": "2025-02-28T05:11:33.718Z",
            "suggestion": "dwadwad",
            "suggestionAttributes": [
                "backed-by-major-investors",
                "disruptive-tech",
                "momentum-surge"
            ],
            "on_chain_analysis": "The token \"Official Trump\" (symbol: TRUMP), operating on the Solana blockchain, is currently priced at $11.35, with a market capitalization of approximately $2.27 billion, ranking 50th in the market. Its recent performance has been troubling, with a significant 24-hour trading volume of $1.07 billion reflecting a market cap to volume ratio of 2.13, indicating moderately healthy liquidity, although the asset experienced a sharp decline of over 14% in 24 hours and a staggering 31.63% drop over the past week. The token’s historical performance reveals an all-time high of $73.43 reached on January 19, 2025, translating to only 15.46% of its ATH at the current price, while the all-time low of $4.29 shows a significant price recovery of 164.57%. However, the overall trend appears to be downward, highlighting recent bearish market sentiment. While the liquidity is bolstered by a high volume to market cap ratio of 46.96 and an average bid-ask spread of just 0.39%, it’s essential to note the circulating supply accounts for only 20% of its total and max supply of 1 billion TRUMP tokens, with a fully diluted valuation of about $11.37 billion, indicating a market cap to FDV ratio of only 0.2, suggesting possible future dilution concerns. Social sentiment is skewed negatively, with 71.88% negative sentiment reported against 28.13% positive, underscoring investor apprehension. Developer activity metrics remain unclear, with no available data, raising a red flag regarding ongoing support and innovation for this token. Overall, considering the heightened price volatility, the very low liquidity risk, but extremely high risks related to supply concentration and developer activity, the overall risk score stands at a concerning 6 out of 10. Despite its considerable community presence, particularly on Twitter with over 101 million followers, the underlying fundamentals and recent performance suggest caution for potential investors.",
            "tokenCategory": "MemeCoins"
        },
        {
            "token_metadata": {
                "contract": "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
                "chain": "solana",
                "metrics": {
                    "name": "Jupiter",
                    "symbol": "jup",
                    "price": 0.678095,
                    "marketCap": 1792437982,
                    "priceChange24h": -8.14853,
                    "volume24h": 167936354,
                    "circulatingSupply": 2637438888.88,
                    "volatility24h": 11.15,
                    "riskScore": 5,
                    "securityStatus": "Low Risk"
                }
            },
            "reason_recommend": "dawdwad",
            "recommendationAttributes": [
                "momentum-surge",
                "backed-by-major-investors",
                "disruptive-tech"
            ],
            "recommendation_time": "2025-02-28T05:11:33.718Z",
            "suggestion": "dwadwa",
            "suggestionAttributes": [
                "momentum-surge",
                "disruptive-tech",
                "backed-by-major-investors"
            ],
            "on_chain_analysis": "The token Jupiter (JUP) operates on the Solana blockchain, currently priced at $0.678095, giving it a market capitalization of approximately $1.79 billion and ranking 62nd in the market. Despite having strong trading activity with a 24-hour trading volume of around $167.94 million, the token has disclosed a concerning trend, exhibiting a -8.15% change over the last 24 hours and -13.11% over the past week, indicating a significant downturn amidst a more extended decline of nearly 39.79% in the last month. The current price remains 33.9% below its all-time high (ATH) of $2 reached in late January 2024, while the price has recovered approximately 48.23% from its all-time low (ATL) of $0.457464 in February 2024. Volatility sits at a notable 11.15% as the market grapples with these price declines. \n\nOn the liquidity side, the volume-to-market cap ratio is robust at 9.37, suggesting healthy trading dynamics. However, with a substantial market cap to total value locked (TVL) ratio of 0.89, it implies considerable funds are not circulating effectively within liquidity pools, despite a low FDV to TVL ratio of 2.36. The circulating supply stands at approximately 2.64 billion with a maximum supply of 10 billion; thus, the circulating ratio of 37.68% contributes to a fully diluted valuation of about $4.76 billion, with a market cap to FDV ratio of 0.38, indicating potentially significant upside or downside risk.\n\nSocial sentiment shows promising metrics with a 75.68% positive sentiment from its 566,640 Twitter followers, yet developer activity remains untracked, suggesting potential vulnerabilities in ongoing project sustainability. Given the heightened supply concentration risk and very high developer activity risk (due to a lack of available metrics), the overall risk assessment is moderate, rated at 5 out of 10, highlighting a market that is both promising and precarious. The current state of Jupiter necessitates careful observation as bearish trends persist, yet positive social sentiment may underpin a rebound if market conditions stabilize.",
            "tokenCategory": "MemeCoins"
        }
    ]
    
    # networks = {
    #     "eth": "https://mainnet.infura.io/v3/0822174983b6479ca10ad18f6a5a518c",
    #     "base": "https://base-mainnet.infura.io/v3/0822174983b6479ca10ad18f6a5a518c",
    #     "vana": "https://rpc.vana.org",
    #     "solana": "https://alien-side-emerald.solana-mainnet.quiknode.pro/a9c0f414bbd654569d77f8cfec805701a08b5f03",
    # }

    results = calculate_token_metrics( unique_tokens )
    authenticity, quality = final_scores(unique_tokens)
    print(f"authenticity, quality", authenticity, quality)

    # Output the results
    for result in results:
        # print(f"Token: {result['token']}")
        print(f"Individual authenticity: {result['authenticity']}, Individual quality: {result['quality']} , Result: {result}")
