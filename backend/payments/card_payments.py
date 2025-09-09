"""
Flutterwave Card Payments Implementation
Follows the official Flutterwave v4 API documentation for card payments
"""

import logging
import requests
import time
from typing import Dict, Any, Optional, List
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class FlutterwaveCardPayments:
    """
    Flutterwave Card Payments Implementation
    Handles card payment flow according to official Flutterwave v4 API documentation
    """
    
    def __init__(self):
        from .services import FlutterwaveService
        self.service = FlutterwaveService()
        self.logger = logging.getLogger(__name__)
    
    def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 1: Create a Customer
        
        Args:
            customer_data (dict): Customer information including:
                - email (required)
                - name (dict with first, middle, last)
                - phone (dict with country_code, number)
                - address (dict with city, country, line1, line2, postal_code, state)
        
        Returns:
            dict: Customer creation result
        """
        try:
            # Validate required fields
            if not customer_data.get('email'):
                return {
                    'success': False,
                    'error': 'Email is required for customer creation'
                }
            
            # Prepare customer payload
            payload = {
                'email': customer_data['email']
            }
            
            # Add optional fields if provided
            if 'name' in customer_data:
                payload['name'] = customer_data['name']
            
            if 'phone' in customer_data:
                payload['phone'] = customer_data['phone']
            
            if 'address' in customer_data:
                payload['address'] = customer_data['address']
            
            # Add metadata for tracking
            payload['meta'] = {
                'source': 'card_payments',
                'created_at': timezone.now().isoformat()
            }
            
            # Make API request
            headers = self.service._get_headers(include_idempotency=True, include_trace=True)
            response = requests.post(
                f'{self.service.base_url}/customers',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Handle response
            success, result = self.service.error_handler.handle_response(response, "Customer creation")
            
            if success:
                customer_info = result['data']['data']
                self.logger.info(f"Customer created successfully: {customer_info['id']}")
                
                return {
                    'success': True,
                    'customer_id': customer_info['id'],
                    'customer_data': customer_info,
                    'message': 'Customer created successfully'
                }
            else:
                return {
                    'success': False,
                    'error': result['error']['error_message'],
                    'error_details': result['error'],
                    'user_message': result['user_message']
                }
        
        except Exception as e:
            self.logger.error(f"Error creating customer: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_card_payment_method(self, card_data: Dict[str, Any], customer_id: str = None) -> Dict[str, Any]:
        """
        Step 2: Create Card Payment Method
        
        Args:
            card_data (dict): Card information including:
                - card_number (required)
                - cvv (required)
                - expiry_month (required)
                - expiry_year (required)
                - cardholder_name (required)
            customer_id (str): Optional customer ID to link payment method
        
        Returns:
            dict: Payment method creation result
        """
        try:
            # Validate required fields
            required_fields = ['card_number', 'cvv', 'expiry_month', 'expiry_year', 'cardholder_name']
            for field in required_fields:
                if field not in card_data:
                    return {
                        'success': False,
                        'error': f'{field.title()} is required for card payment method'
                    }
            
            # Encrypt card data
            from .encryption import FlutterwaveEncryptor
            encryptor = FlutterwaveEncryptor()
            
            encrypted_card = encryptor.encrypt_card_data(card_data)
            
            # Prepare payload
            payload = {
                'type': 'card',
                'card': encrypted_card
            }
            
            # Add customer_id if provided
            if customer_id:
                payload['customer_id'] = customer_id
            
            # Make API request
            headers = self.service._get_headers(include_idempotency=True, include_trace=True)
            
            # Log the payload for debugging
            self.logger.info(f"Card payment method payload: {payload}")
            
            response = requests.post(
                f'{self.service.base_url}/payment-methods',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Handle response
            success, result = self.service.error_handler.handle_response(response, "Card payment method creation")
            
            if success:
                payment_method_info = result['data']['data']
                self.logger.info(f"Card payment method created successfully: {payment_method_info['id']}")
                
                return {
                    'success': True,
                    'payment_method_id': payment_method_info['id'],
                    'payment_method_data': payment_method_info,
                    'message': 'Card payment method created successfully'
                }
            else:
                return {
                    'success': False,
                    'error': result['error']['error_message'],
                    'error_details': result['error'],
                    'user_message': result['user_message']
                }
        
        except Exception as e:
            self.logger.error(f"Error creating card payment method: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def initiate_card_charge(self, charge_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 3: Initiate Card Charge
        
        Args:
            charge_data (dict): Charge information including:
                - reference (unique transaction reference)
                - currency (USD, UGX, etc.)
                - customer_id (from step 1)
                - payment_method_id (from step 2)
                - amount (transaction amount)
                - redirect_url (optional)
                - meta (optional metadata)
                - recurring (optional, for recurring payments)
        
        Returns:
            dict: Charge initiation result
        """
        try:
            # Validate required fields
            required_fields = ['reference', 'currency', 'customer_id', 'payment_method_id', 'amount']
            for field in required_fields:
                if field not in charge_data:
                    return {
                        'success': False,
                        'error': f'{field.title()} is required for charge initiation'
                    }
            
            # Prepare charge payload - following Flutterwave v4 API documentation
            # Ensure reference is alphanumeric (no underscores or special characters)
            reference = charge_data['reference'].replace('_', '').replace('-', '').replace(' ', '')
            
            payload = {
                'currency': charge_data['currency'],
                'customer_id': charge_data['customer_id'],
                'payment_method_id': charge_data['payment_method_id'],
                'amount': int(charge_data['amount']),  # Convert to integer as per API docs
                'reference': reference
            }
            
            # Make API request
            headers = self.service._get_headers(include_idempotency=True, include_trace=True)
            
            # Log the payload for debugging
            self.logger.info(f"Card charge payload: {payload}")
            
            response = requests.post(
                f'{self.service.base_url}/charges',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Handle response
            success, result = self.service.error_handler.handle_response(response, "Card charge initiation")
            
            if success:
                charge_info = result['data']['data']
                self.logger.info(f"Card charge initiated successfully: {charge_info['id']}")
                
                return {
                    'success': True,
                    'charge_id': charge_info['id'],
                    'charge_data': charge_info,
                    'next_action': charge_info.get('next_action'),
                    'status': charge_info.get('status'),
                    'message': 'Card charge initiated successfully'
                }
            else:
                return {
                    'success': False,
                    'error': result['error']['error_message'],
                    'error_details': result['error'],
                    'user_message': result['user_message']
                }
        
        except Exception as e:
            self.logger.error(f"Error initiating card charge: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def authorize_card_payment(self, charge_id: str, authorization_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 4: Authorize Card Payment
        
        Args:
            charge_id (str): Charge ID from step 3
            authorization_data (dict): Authorization information based on auth model:
                - pin (for requires_pin)
                - otp (for requires_otp)
                - avs (for requires_additional_fields)
        
        Returns:
            dict: Authorization result
        """
        try:
            # Validate required fields
            if not charge_id:
                return {
                    'success': False,
                    'error': 'Charge ID is required for authorization'
                }
            
            if not authorization_data:
                return {
                    'success': False,
                    'error': 'Authorization data is required'
                }
            
            # Prepare authorization payload
            payload = {
                'authorization': authorization_data
            }
            
            # Make API request using PUT method as per Flutterwave docs
            headers = self.service._get_headers(include_idempotency=True, include_trace=True)
            
            # Log the payload for debugging
            self.logger.info(f"Card authorization payload: {payload}")
            
            response = requests.put(
                f'{self.service.base_url}/charges/{charge_id}',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Handle response
            success, result = self.service.error_handler.handle_response(response, "Card payment authorization")
            
            if success:
                charge_info = result['data']['data']
                self.logger.info(f"Card payment authorized successfully: {charge_id}")
                
                return {
                    'success': True,
                    'charge_id': charge_id,
                    'charge_data': charge_info,
                    'next_action': charge_info.get('next_action'),
                    'status': charge_info.get('status'),
                    'message': 'Card payment authorized successfully'
                }
            else:
                return {
                    'success': False,
                    'error': result['error']['error_message'],
                    'error_details': result['error'],
                    'user_message': result['user_message']
                }
        
        except Exception as e:
            self.logger.error(f"Error authorizing card payment: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_card_payment(self, charge_id: str) -> Dict[str, Any]:
        """
        Step 5: Verify Card Payment
        
        Args:
            charge_id (str): Charge ID to verify
        
        Returns:
            dict: Payment verification result
        """
        try:
            if not charge_id:
                return {
                    'success': False,
                    'error': 'Charge ID is required for verification'
                }
            
            # Make API request
            headers = self.service._get_headers(include_idempotency=False, include_trace=True)
            response = requests.get(
                f'{self.service.base_url}/charges/{charge_id}',
                headers=headers,
                timeout=30
            )
            
            # Handle response
            success, result = self.service.error_handler.handle_response(response, "Card payment verification")
            
            if success:
                charge_info = result['data']['data']
                self.logger.info(f"Card payment verified successfully: {charge_id}")
                
                return {
                    'success': True,
                    'charge_id': charge_id,
                    'charge_data': charge_info,
                    'status': charge_info.get('status'),
                    'amount': charge_info.get('amount'),
                    'currency': charge_info.get('currency'),
                    'reference': charge_info.get('reference'),
                    'message': 'Card payment verified successfully'
                }
            else:
                return {
                    'success': False,
                    'error': result['error']['error_message'],
                    'error_details': result['error'],
                    'user_message': result['user_message']
                }
        
        except Exception as e:
            self.logger.error(f"Error verifying card payment: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def complete_card_payment_flow(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete the entire card payment flow
        
        Args:
            payment_data (dict): Complete payment information including:
                - customer_data
                - card_data
                - charge_data
                - authorization_data (optional, based on auth model)
        
        Returns:
            dict: Complete payment flow result
        """
        try:
            self.logger.info("Starting complete card payment flow")
            
            # Step 1: Create Customer
            customer_result = self.create_customer(payment_data.get('customer_data', {}))
            if not customer_result['success']:
                return customer_result
            
            customer_id = customer_result['customer_id']
            self.logger.info(f"Customer created: {customer_id}")
            
            # Step 2: Create Card Payment Method
            card_data = payment_data.get('card_data', {})
            
            payment_method_result = self.create_card_payment_method(card_data, customer_id)
            if not payment_method_result['success']:
                return payment_method_result
            
            payment_method_id = payment_method_result['payment_method_id']
            self.logger.info(f"Card payment method created: {payment_method_id}")
            
            # Step 3: Initiate Card Charge
            charge_data = payment_data.get('charge_data', {})
            charge_data['customer_id'] = customer_id
            charge_data['payment_method_id'] = payment_method_id
            
            charge_result = self.initiate_card_charge(charge_data)
            if not charge_result['success']:
                return charge_result
            
            charge_id = charge_result['charge_id']
            next_action = charge_result.get('next_action')
            self.logger.info(f"Card charge initiated: {charge_id}")
            
            # Step 4: Handle Authorization (if required)
            if next_action:
                auth_type = next_action.get('type')
                self.logger.info(f"Authorization required: {auth_type}")
                
                if auth_type in ['requires_pin', 'requires_otp', 'requires_additional_fields']:
                    authorization_data = payment_data.get('authorization_data', {})
                    if not authorization_data:
                        # Generate default authorization data based on type
                        if auth_type == 'requires_otp':
                            authorization_data = {
                                'type': 'otp',
                                'otp': {
                                    'code': '123456'  # Default test OTP
                                }
                            }
                        elif auth_type == 'requires_additional_fields':
                            # Handle AVS (Address Verification System)
                            authorization_data = {
                                'type': 'avs',
                                'avs': {
                                    'address': {
                                        'city': 'Gotham',
                                        'country': 'US',
                                        'line1': '221B Baker Street',
                                        'line2': 'Coker Estate',
                                        'postal_code': '94105',
                                        'state': 'Colorado'
                                    }
                                }
                            }
                        elif auth_type == 'requires_pin':
                            # Handle PIN authorization
                            authorization_data = {
                                'type': 'pin',
                                'pin': {
                                    'nonce': 'test_nonce_123',
                                    'encrypted_pin': 'test_encrypted_pin_456'
                                }
                            }
                        else:
                            return {
                                'success': False,
                                'error': f'Authorization data required for {auth_type}',
                                'charge_id': charge_id,
                                'next_action': next_action
                            }
                    
                    auth_result = self.authorize_card_payment(charge_id, authorization_data)
                    if not auth_result['success']:
                        return auth_result
                    
                    # Check if additional authorization is needed
                    next_action = auth_result.get('next_action')
                    if next_action and next_action.get('type') not in ['redirect_url', 'payment_instruction']:
                        return {
                            'success': False,
                            'error': f'Additional authorization required: {next_action.get("type")}',
                            'charge_id': charge_id,
                            'next_action': next_action
                        }
                
                elif auth_type == 'redirect_url':
                    redirect_url = next_action.get('redirect_url', {}).get('url')
                    return {
                        'success': True,
                        'message': 'Card payment requires redirect',
                        'charge_id': charge_id,
                        'redirect_url': redirect_url,
                        'next_action': next_action,
                        'status': 'pending'
                    }
                
                elif auth_type == 'payment_instruction':
                    instructions = next_action.get('payment_instruction', {})
                    note = instructions.get('note', 'Please follow the payment instructions')
                    return {
                        'success': True,
                        'message': 'Payment instructions provided',
                        'charge_id': charge_id,
                        'instructions': instructions,
                        'note': note,
                        'next_action': next_action,
                        'status': 'pending'
                    }
            
            # Step 5: Verify Card Payment
            verification_result = self.verify_card_payment(charge_id)
            if not verification_result['success']:
                return verification_result
            
            self.logger.info("Complete card payment flow finished successfully")
            
            return {
                'success': True,
                'message': 'Card payment completed successfully',
                'customer_id': customer_id,
                'payment_method_id': payment_method_id,
                'charge_id': charge_id,
                'verification': verification_result,
                'status': verification_result.get('status')
            }
        
        except Exception as e:
            self.logger.error(f"Error in complete card payment flow: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def handle_card_auth_models(self, charge_id: str, next_action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle different card authorization models
        
        Args:
            charge_id (str): Charge ID
            next_action (dict): Next action information
        
        Returns:
            dict: Authorization model handling result
        """
        action_type = next_action.get('type')
        
        if action_type == 'requires_pin':
            return {
                'type': 'pin_required',
                'message': 'PIN authorization required',
                'charge_id': charge_id,
                'auth_model': 'PIN',
                'authorization_data': {
                    'type': 'pin',
                    'pin': {
                        'nonce': 'generated_nonce',
                        'encrypted_pin': 'encrypted_pin_value'
                    }
                }
            }
        
        elif action_type == 'requires_otp':
            return {
                'type': 'otp_required',
                'message': 'OTP authorization required',
                'charge_id': charge_id,
                'auth_model': 'OTP',
                'authorization_data': {
                    'type': 'otp',
                    'otp': {
                        'code': '123456'  # Example OTP code
                    }
                }
            }
        
        elif action_type == 'requires_additional_fields':
            # Handle AVS (Address Verification System)
            return {
                'type': 'avs_required',
                'message': 'Address verification required',
                'charge_id': charge_id,
                'auth_model': 'AVS',
                'authorization_data': {
                    'type': 'avs',
                    'avs': {
                        'address': {
                            'city': 'Gotham',
                            'country': 'US',
                            'line1': '221B Baker Street',
                            'line2': 'Coker Estate',
                            'postal_code': '94105',
                            'state': 'Colorado'
                        }
                    }
                }
            }
        
        elif action_type == 'redirect_url':
            redirect_url = next_action.get('redirect_url', {}).get('url')
            return {
                'type': 'redirect_required',
                'message': 'Redirect to complete payment (3DS)',
                'redirect_url': redirect_url,
                'charge_id': charge_id,
                'auth_model': '3DS'
            }
        
        else:
            return {
                'type': 'unknown',
                'message': f'Unknown auth model: {action_type}',
                'charge_id': charge_id
            } 