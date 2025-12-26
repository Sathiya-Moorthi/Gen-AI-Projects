"""
conversion_logic.py

This module defines the ConversionLogic class, which encapsulates all
stateless unit conversion functions required by the application.
It is designed to be independent, container-ready, and highly reliable.

All methods include strict input validation and use a hard-coded exchange rate
for currency conversion to ensure reproducibility and security, as per
application constraints.
"""
from typing import Union

# Type alias for clarity in type hinting
Numeric = Union[int, float]

class ConversionLogic:
    """
    A stateless class containing static methods for various unit conversions.
    The methods handle input validation and raise ValueError on non-numeric input.
    """

    # --- Configuration Constants ---
    # CRITICAL SECURITY ENFORCEMENT: Hard-coded exchange rate to avoid
    # external API dependency and ensure reproducible results.
    USD_TO_INR_RATE: float = 83.00
    
    # Standard conversion factors
    CM_PER_INCH: float = 2.54
    KG_PER_POUND: float = 0.453592

    @staticmethod
    def _validate_input(value: Numeric) -> None:
        """Helper method to validate that the input is a numeric type."""
        if not isinstance(value, (int, float)):
            raise ValueError(f"Invalid input type: Expected numeric (int or float), got {type(value).__name__}.")

    # ----------------------------------------------------------------------
    # Currency Conversions (INR <-> USD)
    # ----------------------------------------------------------------------

    @staticmethod
    def usd_to_inr(usd_amount: Numeric) -> float:
        """
        Converts a USD amount to INR using a fixed, hard-coded exchange rate.

        :param usd_amount: The amount in US Dollars.
        :raises ValueError: If the input is not numeric.
        :return: The converted amount in Indian Rupees.
        """
        ConversionLogic._validate_input(usd_amount)
        # Apply the fixed, hard-coded rate
        inr_amount = usd_amount * ConversionLogic.USD_TO_INR_RATE
        return float(inr_amount)

    @staticmethod
    def inr_to_usd(inr_amount: Numeric) -> float:
        """
        Converts an INR amount to USD using a fixed, hard-coded exchange rate.

        :param inr_amount: The amount in Indian Rupees.
        :raises ValueError: If the input is not numeric.
        :return: The converted amount in US Dollars.
        """
        ConversionLogic._validate_input(inr_amount)
        # Apply the fixed, hard-coded rate
        usd_amount = inr_amount / ConversionLogic.USD_TO_INR_RATE
        return float(usd_amount)

    # ----------------------------------------------------------------------
    # Temperature Conversions (Celsius <-> Fahrenheit)
    # ----------------------------------------------------------------------

    @staticmethod
    def celsius_to_fahrenheit(celsius: Numeric) -> float:
        """
        Converts temperature from Celsius (°C) to Fahrenheit (°F).

        Formula: F = C * (9/5) + 32

        :param celsius: The temperature in Celsius.
        :raises ValueError: If the input is not numeric.
        :return: The converted temperature in Fahrenheit.
        """
        ConversionLogic._validate_input(celsius)
        fahrenheit = (celsius * 9/5) + 32
        return float(fahrenheit)

    @staticmethod
    def fahrenheit_to_celsius(fahrenheit: Numeric) -> float:
        """
        Converts temperature from Fahrenheit (°F) to Celsius (°C).

        Formula: C = (F - 32) * (5/9)

        :param fahrenheit: The temperature in Fahrenheit.
        :raises ValueError: If the input is not numeric.
        :return: The converted temperature in Celsius.
        """
        ConversionLogic._validate_input(fahrenheit)
        celsius = (fahrenheit - 32) * 5/9
        return float(celsius)

    # ----------------------------------------------------------------------
    # Length Conversions (Centimeter <-> Inch)
    # ----------------------------------------------------------------------

    @staticmethod
    def cm_to_inch(cm: Numeric) -> float:
        """
        Converts length from Centimeters (cm) to Inches (inch).

        :param cm: The length in Centimeters.
        :raises ValueError: If the input is not numeric.
        :return: The converted length in Inches.
        """
        ConversionLogic._validate_input(cm)
        inch = cm / ConversionLogic.CM_PER_INCH
        return float(inch)

    @staticmethod
    def inch_to_cm(inch: Numeric) -> float:
        """
        Converts length from Inches (inch) to Centimeters (cm).

        :param inch: The length in Inches.
        :raises ValueError: If the input is not numeric.
        :return: The converted length in Centimeters.
        """
        ConversionLogic._validate_input(inch)
        cm = inch * ConversionLogic.CM_PER_INCH
        return float(cm)

    # ----------------------------------------------------------------------
    # Weight Conversions (Kilogram <-> Pound)
    # ----------------------------------------------------------------------

    @staticmethod
    def kg_to_lb(kg: Numeric) -> float:
        """
        Converts weight from Kilograms (kg) to Pounds (lb).

        :param kg: The weight in Kilograms.
        :raises ValueError: If the input is not numeric.
        :return: The converted weight in Pounds.
        """
        ConversionLogic._validate_input(kg)
        # 1 kg is approximately 2.20462 pounds.
        lb = kg / ConversionLogic.KG_PER_POUND
        return float(lb)

    @staticmethod
    def lb_to_kg(lb: Numeric) -> float:
        """
        Converts weight from Pounds (lb) to Kilograms (kg).

        :param lb: The weight in Pounds.
        :raises ValueError: If the input is not numeric.
        :return: The converted weight in Kilograms.
        """
        ConversionLogic._validate_input(lb)
        # 1 lb is approximately 0.453592 kilograms.
        kg = lb * ConversionLogic.KG_PER_POUND
        return float(kg)