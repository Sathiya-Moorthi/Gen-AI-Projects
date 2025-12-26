class CurrencyService:
    """
    Service layer to handle currency logic.
    Base Currency for calculation: USD
    """
    # Static rates relative to USD (1.0)
    RATES = {
        "USD": 1.0,
        "INR": 83.50,
        "EUR": 0.92,
        "GBP": 0.79
    }

    @classmethod
    def get_currencies(cls):
        return list(cls.RATES.keys())

    @classmethod
    def convert(cls, from_currency, to_currency, amount):
        if from_currency not in cls.RATES or to_currency not in cls.RATES:
            raise ValueError("Invalid currency code provided.")
        
        # Conversion formula: (Amount / From_Rate) * To_Rate
        # We convert 'from' to USD, then USD to 'to'
        base_amount = amount / cls.RATES[from_currency]
        converted_amount = base_amount * cls.RATES[to_currency]
        
        return round(converted_amount, 2)