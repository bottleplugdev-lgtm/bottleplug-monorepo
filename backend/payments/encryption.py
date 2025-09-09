"""
Flutterwave Encryption Module
Handles encryption of sensitive card data using AES 256 encryption
"""

import base64
import secrets
import string
import logging
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from django.conf import settings

logger = logging.getLogger(__name__)


class FlutterwaveEncryptor:
    """
    Flutterwave AES 256 Encryption for card data
    """
    
    def __init__(self, encryption_key=None):
        """
        Initialize encryptor with encryption key
        
        Args:
            encryption_key (str): Base64 encoded encryption key from Flutterwave dashboard
        """
        self.encryption_key = encryption_key or getattr(settings, 'FLUTTERWAVE_ENCRYPTION_KEY', '')
        
        if not self.encryption_key:
            logger.warning("Flutterwave encryption key not configured")
            return
        
        try:
            # Decode the base64 encryption key
            self.aes_key = base64.b64decode(self.encryption_key)
            logger.info("Flutterwave encryption initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            self.aes_key = None
    
    @staticmethod
    def generate_nonce(length: int = 12) -> str:
        """
        Generate a random nonce for encryption
        
        Args:
            length (int): Length of the nonce (default: 12)
        
        Returns:
            str: Random nonce string
        """
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    def encrypt(self, plain_text: str, nonce: str) -> str:
        """
        Encrypt plain text using AES GCM
        
        Args:
            plain_text (str): Text to encrypt
            nonce (str): Nonce for encryption
        
        Returns:
            str: Base64 encoded encrypted text
        
        Raises:
            ValueError: If encryption key not configured or invalid parameters
        """
        if not self.aes_key:
            raise ValueError("Encryption key not configured")
        
        if not plain_text or not nonce:
            raise ValueError('Both plain_text and nonce are required for encryption.')
        
        try:
            nonce_bytes = nonce.encode()
            aes_gcm = AESGCM(self.aes_key)
            cipher_text = aes_gcm.encrypt(nonce_bytes, plain_text.encode(), None)
            
            return base64.b64encode(cipher_text).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise ValueError(f"Encryption failed: {e}")
    
    def encrypt_dict(self, data: dict) -> dict:
        """
        Encrypt all values in a dictionary
        
        Args:
            data (dict): Dictionary with values to encrypt
        
        Returns:
            dict: Dictionary with encrypted values and nonce
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary.")
        
        if not self.aes_key:
            logger.warning("Encryption key not configured, returning unencrypted data")
            return data
        
        try:
            nonce = self.generate_nonce()
            encrypted_data = {"nonce": nonce}
            
            for key, value in data.items():
                encrypted_data[key] = self.encrypt(str(value), nonce)
            
            return encrypted_data
        except Exception as e:
            logger.error(f"Dictionary encryption failed: {e}")
            raise ValueError(f"Dictionary encryption failed: {e}")
    
    def encrypt_card_data(self, card_data: dict) -> dict:
        """
        Encrypt card data for Flutterwave API
        
        Args:
            card_data (dict): Card data to encrypt
                {
                    'card_number': '1234567890123456',
                    'cvv': '123',
                    'expiry_month': '12',
                    'expiry_year': '2025'
                }
        
        Returns:
            dict: Encrypted card data for Flutterwave API
        """
        if not self.aes_key:
            logger.warning("Encryption key not configured, card data will not be encrypted")
            return card_data
        
        try:
            # Generate nonce for this encryption
            nonce = self.generate_nonce()
            
            # Encrypt each card field
            encrypted_card = {
                "nonce": nonce,
                "encrypted_card_number": self.encrypt(card_data.get('card_number', ''), nonce),
                "encrypted_cvv": self.encrypt(card_data.get('cvv', ''), nonce),
                "encrypted_expiry_month": self.encrypt(card_data.get('expiry_month', ''), nonce),
                "encrypted_expiry_year": self.encrypt(card_data.get('expiry_year', ''), nonce)
            }
            
            # Add cardholder name if provided (not encrypted)
            if 'cardholder_name' in card_data:
                encrypted_card['cardholder_name'] = card_data['cardholder_name']
            
            logger.info("Card data encrypted successfully")
            return encrypted_card
            
        except Exception as e:
            logger.error(f"Card data encryption failed: {e}")
            raise ValueError(f"Card data encryption failed: {e}")
    
    def is_configured(self) -> bool:
        """
        Check if encryption is properly configured
        
        Returns:
            bool: True if encryption key is configured
        """
        return bool(self.aes_key)
    
    def get_encryption_status(self) -> dict:
        """
        Get encryption configuration status
        
        Returns:
            dict: Encryption status information
        """
        return {
            'configured': self.is_configured(),
            'key_length': len(self.encryption_key) if self.encryption_key else 0,
            'key_preview': self.encryption_key[:10] + '...' if self.encryption_key else None
        }


class CardDataValidator:
    """
    Validate card data before encryption
    """
    
    @staticmethod
    def validate_card_number(card_number: str) -> bool:
        """
        Validate card number using Luhn algorithm
        
        Args:
            card_number (str): Card number to validate
        
        Returns:
            bool: True if valid card number
        """
        if not card_number or not card_number.isdigit():
            return False
        
        # Remove spaces and dashes
        card_number = card_number.replace(' ', '').replace('-', '')
        
        if len(card_number) < 13 or len(card_number) > 19:
            return False
        
        # Luhn algorithm
        digits = [int(d) for d in card_number]
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(divmod(d * 2, 10))
        
        return checksum % 10 == 0
    
    @staticmethod
    def validate_cvv(cvv: str) -> bool:
        """
        Validate CVV
        
        Args:
            cvv (str): CVV to validate
        
        Returns:
            bool: True if valid CVV
        """
        if not cvv or not cvv.isdigit():
            return False
        
        return len(cvv) in [3, 4]  # 3 for Visa/MC, 4 for Amex
    
    @staticmethod
    def validate_expiry_month(month: str) -> bool:
        """
        Validate expiry month
        
        Args:
            month (str): Month to validate
        
        Returns:
            bool: True if valid month
        """
        if not month or not month.isdigit():
            return False
        
        month_int = int(month)
        return 1 <= month_int <= 12
    
    @staticmethod
    def validate_expiry_year(year: str) -> bool:
        """
        Validate expiry year
        
        Args:
            year (str): Year to validate
        
        Returns:
            bool: True if valid year
        """
        if not year or not year.isdigit():
            return False
        
        year_int = int(year)
        current_year = 2024  # You might want to get this dynamically
        return year_int >= current_year and year_int <= current_year + 20
    
    @staticmethod
    def validate_card_data(card_data: dict) -> tuple[bool, list]:
        """
        Validate complete card data
        
        Args:
            card_data (dict): Card data to validate
        
        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []
        
        # Validate card number
        if not CardDataValidator.validate_card_number(card_data.get('card_number', '')):
            errors.append("Invalid card number")
        
        # Validate CVV
        if not CardDataValidator.validate_cvv(card_data.get('cvv', '')):
            errors.append("Invalid CVV (must be 3-4 digits)")
        
        # Validate expiry month
        if not CardDataValidator.validate_expiry_month(card_data.get('expiry_month', '')):
            errors.append("Invalid expiry month (must be 1-12)")
        
        # Validate expiry year
        if not CardDataValidator.validate_expiry_year(card_data.get('expiry_year', '')):
            errors.append("Invalid expiry year")
        
        # Validate cardholder name
        cardholder_name = card_data.get('cardholder_name', '')
        if not cardholder_name or len(cardholder_name.strip()) < 2:
            errors.append("Invalid cardholder name")
        
        return len(errors) == 0, errors 