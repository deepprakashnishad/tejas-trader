seeddata = [
    {
        "classname": "Technical",
        "keys": [
                "name"
            ],
        "data": [
            {
                "name": "RSI",
                "description": "Relative Strength Index",
                "tech_args": {
                    "high": "80",
                    "low": "20",
                    "period": "14",
                    "field": "close",
                }
            },
            {
                "name": "PreviousHigh",
                "description": "Previous High",
                "tech_args": {
                    "period": "1"
                }
            },
            {
                "name": "PreviousLow",
                "description": "Previous Low",
                "tech_args": {
                    "period": "1"
                }
            },
            {
                "name": "ClosePrice",
                "description": "Close Price",
                "tech_args": {}
            },
            {
                "name": "DayFirstCandle",
                "description": "Day First Candle",
                "tech_args": {
                    "field": "high"
                }
            },
            {
                "name": "Range",
                "description": "Difference between high and low",
                "tech_args": {}
            },
            {
                "name": "Target",
                "description": "Target",
                "tech_args": {
                    "value": "2",
                    "type": "percent" #value, percent, price
                }
            },
            {
                "name": "Stoploss",
                "description": "Stoploss",
                "tech_args": {
                    "value": "0.5",
                    "type": "percent" #value, percent, price
                }
            },
            {
                "name": "InsideCandle",
                "description": "Inside Candle",
                "tech_args": {
                    "previous_candle_count": "1",
                    "till_first_candle": "true"
                }
            },
            {
                "name": "PiercingCandle",
                "description": "Piercing Candle",
                "tech_args": {
                    "field": "high"
                }
            },
            {
                "name": "Candle",
                "description": "Single Candle",
                "tech_args": {
                    "field": "high",
                    "candle_choice": "day_first_candle"
                }
            }    
        ]
    }
]