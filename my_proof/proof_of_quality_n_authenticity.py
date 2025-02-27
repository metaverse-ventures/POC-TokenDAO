from base64 import b64decode
import logging
import os
import base58
import requests

def validate_token_metrics(metrics):
    """Validate token metrics against authenticity rules."""
    required_keys = [
        "price", "marketCap", "volume24h", "circulatingSupply", "volatility24h", "riskScore"
    ]

    if not all(key in metrics for key in required_keys):
        return 0  # Missing required fields

    return int(
        metrics["price"] > 0 and
        metrics["marketCap"] > 0 and
        metrics["volume24h"] > 0 and
        metrics["circulatingSupply"] > 0 and
        (0 <= metrics["volatility24h"] <= 100) and
        (1 <= metrics["riskScore"] <= 10)
    )

def calculate_quality_score(unique_tokens_provided):
    """Calculate quality score based on provided token details."""
    unique_tokens_provided = len(unique_tokens_provided)  # Count non-empty fields
    logging.info(f"length is {unique_tokens_provided} ")

    if 12 <= unique_tokens_provided <= 20:
        return 1
    elif 6 <= unique_tokens_provided <= 11:
        return unique_tokens_provided
    elif 1 <= unique_tokens_provided <= 5:
        return 0.1
    else:
        return 0

def calculate_token_metrics(unique_tokens):
    results = []

    for token in unique_tokens:
        data_chain = token.get("chain", "").lower()
        data_contract = token.get("contract", "")
        data_reason = token.get("reason", "")
        data_suggestion = token.get("suggestion", "")
        metrics = token.get("metrics", {})

        print(f"Processing token {data_contract} on {data_chain} with reason: {data_reason}")

        # Authenticity Check
        individual_authenticity = validate_token_metrics(metrics)

        # Additional check for suggestionAttributes or recommendationAttributes
        valid_attributes = {
            "momentum-surge",
            "high-liquidity",
            "utility-driven",
            "backed-by-major-investors",
            "community-powered",
            "verified-contracts",
            "disruptive-tech",
            "major-integrations",
            "limited-supply",
        }

        suggestion_attributes = token.get("suggestionAttributes", [])
        recommendation_attributes = token.get("recommendationAttributes", [])

        has_valid_attributes = (
            any(attr in valid_attributes for attr in suggestion_attributes) or
            any(attr in valid_attributes for attr in recommendation_attributes)
        )

        if not has_valid_attributes:
            individual_authenticity = 0

        # Quality Score Calculation
        individual_quality = 0

        if individual_authenticity and len(data_reason) > 10:
            individual_quality += 0.5

        if individual_authenticity and len(data_suggestion) > 10:
            individual_quality += 0.5

        individual_quality = min(individual_quality, 1.0)  # Ensure the quality score does not exceed 1.0

        results.append({
            "token": data_contract,
            "authenticity": individual_authenticity,
            "quality": individual_quality
        })

    return results

def final_scores(unique_tokens):
    """Calculate the average authenticity and quality scores."""
    results = calculate_token_metrics(unique_tokens)
    
    if not results:
        return 0, 0

    authenticity_avg = sum(result["authenticity"] for result in results) / len(results)
    quality_avg = sum(result["quality"] for result in results) / len(results)
    logging.info(f"authenticity_avg: {authenticity_avg}, quality_avg: {quality_avg}, results, {results[0]}")
    return authenticity_avg, quality_avg

# Example of how this would be executed
if __name__ == "__main__":
    # Assuming we have some example unique tokens
    unique_tokens =  [
        {
            "chain": "ethereum",
            "contract": "0xdac17f958d2ee523a2206206994597c13d831ec7",
            "reason": "This is a very good token",
            "suggestion": "This is awesome",
            "recommendationAttributes": [
                "momentum-surge",
                "utility-driven",
                "community-powered"
            ],
            "suggestionAttributes": [
                "momentum-surge",
                "utility-driven",
                "community-powered"
            ],
            "analysis": "The provided token data for Tether (USDT) reveals a stable market presence with a current price of approximately $0.999, reflecting a market cap of $141.96 billion, positioned at rank 3 in the crypto market. Daily trading volume stands at $89.08 billion, showcasing significant liquidity, although the token has experienced minor fluctuations, reflected in the 24-hour change of 0.02% and volatility of 0.09%. Historically, USDT has an all-time high (ATH) of $1.32 reached in July 2018, making the current price 75.68% below its ATH, yet it is 74.49% above its all-time low (ATL) of $0.5725 from March 2015, indicating resilience. The circulating supply is fully in circulation at approximately 142.1 billion tokens, which suggests effective supply management, with a market cap to fully diluted valuation (FDV) ratio of 1 indicating that there\u00e2\u20ac\u2122s no further supply dilution expected. Despite a successful trading volume to market cap ratio of 62.75, the token lacks specific liquidity metrics such as total value locked (TVL). Socially, Tether has a robust Twitter following of nearly 525,000, with a positive sentiment ratio of 1.44, hinting at favorable community perception despite high developer activity risk. Overall, while USDT reflects stability and liquidity, developer activity remains a notable concern and should be monitored for potential future impacts on its market maturity and overall usability in an evolving crypto landscape.",
            "metrics": {
                "name": "Tether",
                "symbol": "usdt",
                "price": 0.998984,
                "marketCap": 141964371788,
                "priceChange24h": 0.02083,
                "volume24h": 89078197306,
                "circulatingSupply": 142104224084.4939,
                "volatility24h": 0.09,
                "riskScore": 2,
                "securityStatus": "High Risk"
            }
        },
        {
            "chain": "ethereum",
            "contract": "0xb8c77482e45f1f44de1745f52c74426c631bdd52",
            "reason": "dwadw",
            "suggestion": "dwadwa",
            "recommendationAttributes": [
                "disruptive-tech",
                "community-powered",
                "utility-driven"
            ],
            "suggestionAttributes": [
                "momentum-surge",
                "utility-driven",
                "community-powered"
            ],
            "analysis": "The market data for the BNB token indicates a current price of $609.23 with a market cap of approximately $89.26 billion, positioning it as the 5th largest cryptocurrency by market cap. However, the recent price movements display a concerning downward trend, with declines of 0.57%, 6.92%, and 7.90% over the last 24 hours, 7 days, and 30 days respectively, despite a commendable 24-hour trading volume of $1.04 billion and a market cap to volume ratio of 86. Historical analysis reveals an all-time high (ATH) of $788.84, indicating a price correction of 22.77% since then, contrasting sharply with its all-time low (ATL) of $0.0398, highlighting substantial long-term growth capabilities of over 1.5 million percent. The liquidity analysis shows solid trading volume relative to market cap with a volume to market cap ratio of 1.16, reflecting adequate liquidity through its presence on 100 trading exchanges, though Total Value Locked (TVL) data is unavailable. On the supply side, the circulating supply matches the total supply, achieving a circulation ratio of 100%, with a fully diluted valuation equal to the market cap, emphasizing the token's mature supply. Social sentiment is moderately positive, with a sentiment ratio of 1.36, which may stimulate community engagement given a substantial Twitter following of over 14 million. Developer activity, while robust with 4,125 GitHub stars indicating interest, lacks quantifiable current contributions, leading to a high risk rating for developer activity. Overall, the token shows a mixed but generally stable picture, characterized by low price volatility, moderate liquidity risk, and high market maturity but continues to be hindered by recent price depreciations, fluctuating developer engagement, and the absence of critical TVL metrics.",
            "metrics": {
                "name": "BNB",
                "symbol": "bnb",
                "price": 609.23,
                "marketCap": 89257633624,
                "priceChange24h": -0.57218,
                "volume24h": 1037919564,
                "circulatingSupply": 145887575.79,
                "volatility24h": 3.98,
                "riskScore": 4,
                "securityStatus": "Moderate Risk"
            }
        },
        {
            "chain": "ethereum",
            "contract": "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",
            "reason": "dawdw",
            "suggestion": "wadwa",
            "recommendationAttributes": [
                "momentum-surge",
                "utility-driven",
                "community-powered"
            ],
            "suggestionAttributes": [
                "momentum-surge",
                "utility-driven",
                "community-powered"
            ],
            "analysis": "The market data for Wrapped Bitcoin (WBTC) reveals a current price of $86,058, with a market cap of approximately $11.15 billion, placing it at rank 12 in the market. A 24-hour volume of $573.29 million indicates decent trading activity, but a daily change of -1.05% and a -10.37% decline over the past week suggest a strong downtrend. Historical analysis shows that the asset is currently at 79.41% of its all-time high (ATH) of $108,368, reflecting resilience since it\u00e2\u20ac\u2122s also up 2,641.43% from its all-time low (ATL). Liquidity appears reasonable with a volume-to-market cap ratio of 5.14 and a market cap to TVL ratio of 0.98, but total value locked data is absent, preventing a full understanding. Token supply analysis shows that WBTC has a fully circulating supply, indicating no future inflationary risk. Positive sentiment also stands out, with a 100% favorable view, despite limited engagement on platforms like Reddit and Telegram. Developer activity remains concerning due to the lack of detailed metrics and only modest engagement metrics on GitHub, leading to a high-risk rating in development. Overall, WBTC demonstrates stability and liquidity but is vulnerable to market sentiment shifts and developer activity risks, which detracts from perceived maturity.",
            "metrics": {
                "name": "Wrapped Bitcoin",
                "symbol": "wbtc",
                "price": 86058,
                "marketCap": 11154208039,
                "priceChange24h": -1.05279,
                "volume24h": 573285619,
                "circulatingSupply": 129138.42002211,
                "volatility24h": 4.34,
                "riskScore": 3,
                "securityStatus": "Moderate Risk"
            }
        },
        {
            "chain": "ethereum",
            "contract": "0x514910771af9ca656af840dff83e8264ecf986ca",
            "reason": "dwadwa",
            "suggestion": "wdadwa",
            "recommendationAttributes": [
                "momentum-surge",
                "utility-driven",
                "disruptive-tech"
            ],
            "suggestionAttributes": [
                "momentum-surge",
                "utility-driven",
                "community-powered"
            ],
            "analysis": "**Market Data Analysis** indicates a current price of $15.15 for the Chainlink token (LINK), reflecting a market capitalization of approximately $9.67 billion, which positions it at a notable 14th in market cap rank. While the 24-hour trading volume of $696.83 million underscores its active trading environment, the recent performance shows a troubling trend with a significant 30-day decline of over 35% and a more tempered 7-day drop of about 15.55%. However, the token's 24-hour volatility at 6.44% suggests reasonable stability in the short term, despite recent struggles. In terms of historical perspective, the token's all-time high (ATH) of $52.70 in May 2021 highlights a substantial decline of nearly 72% from its peak, stressing the ongoing bearish sentiment; conversely, its all-time low (ATL) of $0.148 ensures that the current pricing represents an astronomical 10,123% increase, showcasing long-term growth potential. Liquidity appears fairly robust, with a volume to market cap ratio of 7.21, though the lack of Total Value Locked (TVL) data inhibits a fuller liquidity risk assessment. The average bid-ask spread at 0.23% indicates a narrow spread, suggesting efficient trading conditions. Circulating supply stands at about 638 million, 63.81% of the total supply of 1 billion, and a market cap to fully diluted valuation ratio of 0.64 implies there could be upward valuation preferences. Social sentiment remains largely positive at 81.25% with a significant Twitter following of over 1.28 million, emphasizing community support. Developer activity reflects a healthy engagement with high issue resolution ratios, although the absence of a developer score limits a deeper insight into potential risks. Finally, a risk assessment rating of 1/10 suggests a favorable risk profile against high market maturity, low liquidity, and developer activity risks, despite moderate supply concentration concerns. Overall, Chainlink presents as a promising asset with strengths in community engagement and developer activity but needs to address its existing price volatility and market adaptations to recover from recent downturns.",
            "metrics": {
                "name": "Chainlink",
                "symbol": "link",
                "price": 15.15,
                "marketCap": 9667424557,
                "priceChange24h": 2.54002,
                "volume24h": 696828906,
                "circulatingSupply": 638099970.4505637,
                "volatility24h": 6.44,
                "riskScore": 1,
                "securityStatus": "High Risk"
            }
        },
        {
            "chain": "ethereum",
            "contract": "0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce",
            "reason": "adwdaw",
            "suggestion": "dawd",
            "recommendationAttributes": [
                "momentum-surge",
                "utility-driven",
                "community-powered"
            ],
            "suggestionAttributes": [
                "momentum-surge",
                "community-powered",
                "utility-driven"
            ],
            "analysis": "The token analysis for Shiba Inu (SHIB) presents a mixed picture, highlighting significant strengths and notable concerns. Currently priced at $0.00001406 with a market capitalization of approximately $8.3 billion, its 24-hour trading volume of $234.5 million reflects active market engagement despite a recent 30-day price decline of 23.36%. The token ranked 21st in market capitalization, demonstrating substantial liquidity with a market cap to volume ratio of 35.4 and average volatility of 5.16%. Historically, SHIB has seen drastic price fluctuations, reaching an all-time high (ATH) of $0.00008616 in late 2021 but struggling with a 7-day change of -8.46% and a concerning 60-day decline of over 36%. Social sentiment remains strong, with an impressive 84.93% positive feedback, bolstered by a large following on Twitter (3.9 million). However, the liquidity is marked as moderate due to the sheer volume against market cap, and the lack of developer activity data raises concerns about sustainability. While the supply is nearly fully circulated at 99.96%, high developer activity risk and an overall risk score of 4/10 imply caution despite apparent community support, hinting at the token's speculative nature within the broader crypto market.",
            "metrics": {
                "name": "Shiba Inu",
                "symbol": "shib",
                "price": 1.406e-05,
                "marketCap": 8302739954,
                "priceChange24h": 1.77888,
                "volume24h": 234545625,
                "circulatingSupply": 589253691596721.6,
                "volatility24h": 5.16,
                "riskScore": 4,
                "securityStatus": "Moderate Risk"
            }
        }
    ]
    
    # networks = {
    #     "eth": "https://mainnet.infura.io/v3/0822174983b6479ca10ad18f6a5a518c",
    #     "base": "https://base-mainnet.infura.io/v3/0822174983b6479ca10ad18f6a5a518c",
    #     "vana": "https://rpc.vana.org",
    #     "solana": "https://alien-side-emerald.solana-mainnet.quiknode.pro/a9c0f414bbd654569d77f8cfec805701a08b5f03",
    # }

    results = calculate_token_metrics( unique_tokens )

    # Output the results
    for result in results:
        # print(f"Token: {result['token']}")
        print(f"Authenticity: {result['authenticity']}, Quality: {result['quality']} , Result: {result}")
