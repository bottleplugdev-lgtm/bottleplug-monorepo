"""
Flutterwave General Flow Implementation
Implements the 5-step payment flow: Customer → Payment Method → Charge → Authorize → Verify
"""

import logging
import requests
import time
from typing import Dict, Any, Optional, List, Tuple
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class FlutterwaveGeneralFlow:
    """
    Flutterwave General Flow Implementation
    Handles the complete 5-step payment process
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
                'source': 'general_flow',
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
    
    def create_payment_method(self, payment_method_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 2: Create a Payment Method
        
        Args:
            payment_method_data (dict): Payment method information including:
                - type (card, mobile_money, etc.)
                - card (for card payments) or mobile_money (for mobile money)
        
        Returns:
            dict: Payment method creation result
        """
        try:
            # Validate required fields
            if not payment_method_data.get('type'):
                return {
                    'success': False,
                    'error': 'Payment method type is required'
                }
            
            payment_type = payment_method_data['type']
            
            # Prepare payload based on payment type
            payload = {
                'type': payment_type
            }
            
            # Add customer_id if provided
            if 'customer_id' in payment_method_data:
                payload['customer_id'] = payment_method_data['customer_id']
            
            if payment_type == 'card':
                if 'card' not in payment_method_data:
                    return {
                        'success': False,
                        'error': 'Card details are required for card payment method'
                    }
                
                # Encrypt card data
                from .encryption import FlutterwaveEncryptor
                encryptor = FlutterwaveEncryptor()
                
                card_data = payment_method_data['card']
                encrypted_card = encryptor.encrypt_card_data(card_data)
                
                payload['card'] = encrypted_card
            
            elif payment_type == 'mobile_money':
                if 'mobile_money' not in payment_method_data:
                    return {
                        'success': False,
                        'error': 'Mobile money details are required'
                    }
                
                payload['mobile_money'] = payment_method_data['mobile_money']
            
            # Make API request
            headers = self.service._get_headers(include_idempotency=True, include_trace=True)
            
            # Log the payload for debugging
            self.logger.info(f"Payment method payload: {payload}")
            
            response = requests.post(
                f'{self.service.base_url}/payment-methods',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Handle response
            success, result = self.service.error_handler.handle_response(response, "Payment method creation")
            
            if success:
                payment_method_info = result['data']['data']
                self.logger.info(f"Payment method created successfully: {payment_method_info['id']}")
                
                return {
                    'success': True,
                    'payment_method_id': payment_method_info['id'],
                    'payment_method_data': payment_method_info,
                    'message': 'Payment method created successfully'
                }
            else:
                return {
                    'success': False,
                    'error': result['error']['error_message'],
                    'error_details': result['error'],
                    'user_message': result['user_message']
                }
        
        except Exception as e:
            self.logger.error(f"Error creating payment method: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def initiate_charge(self, charge_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 3: Initiate a Charge
        
        Args:
            charge_data (dict): Charge information including:
                - reference (unique transaction reference)
                - currency (USD, UGX, etc.)
                - customer_id (from step 1)
                - payment_method_id (from step 2)
                - amount (transaction amount)
                - redirect_url (optional)
                - meta (optional metadata)
        
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
            self.logger.info(f"Charge payload: {payload}")
            
            response = requests.post(
                f'{self.service.base_url}/charges',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Handle response
            success, result = self.service.error_handler.handle_response(response, "Charge initiation")
            
            if success:
                charge_info = result['data']['data']
                self.logger.info(f"Charge initiated successfully: {charge_info['id']}")
                
                return {
                    'success': True,
                    'charge_id': charge_info['id'],
                    'charge_data': charge_info,
                    'next_action': charge_info.get('next_action'),
                    'status': charge_info.get('status'),
                    'message': 'Charge initiated successfully'
                }
            else:
                return {
                    'success': False,
                    'error': result['error']['error_message'],
                    'error_details': result['error'],
                    'user_message': result['user_message']
                }
        
        except Exception as e:
            self.logger.error(f"Error initiating charge: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def authorize_charge(self, charge_id: str, authorization_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 4: Authorize a Charge
        
        Args:
            charge_id (str): Charge ID from step 3
            authorization_data (dict): Authorization information based on next_action type:
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
            response = requests.put(
                f'{self.service.base_url}/charges/{charge_id}',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Handle response
            success, result = self.service.error_handler.handle_response(response, "Charge authorization")
            
            if success:
                charge_info = result['data']['data']
                self.logger.info(f"Charge authorized successfully: {charge_id}")
                
                return {
                    'success': True,
                    'charge_id': charge_id,
                    'charge_data': charge_info,
                    'next_action': charge_info.get('next_action'),
                    'status': charge_info.get('status'),
                    'message': 'Charge authorized successfully'
                }
            else:
                return {
                    'success': False,
                    'error': result['error']['error_message'],
                    'error_details': result['error'],
                    'user_message': result['user_message']
                }
        
        except Exception as e:
            self.logger.error(f"Error authorizing charge: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment(self, charge_id: str) -> Dict[str, Any]:
        """
        Step 5: Verify Payment Status
        
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
            success, result = self.service.error_handler.handle_response(response, "Payment verification")
            
            if success:
                charge_info = result['data']['data']
                self.logger.info(f"Payment verified successfully: {charge_id}")
                
                return {
                    'success': True,
                    'charge_id': charge_id,
                    'charge_data': charge_info,
                    'status': charge_info.get('status'),
                    'amount': charge_info.get('amount'),
                    'currency': charge_info.get('currency'),
                    'reference': charge_info.get('reference'),
                    'message': 'Payment verified successfully'
                }
            else:
                return {
                    'success': False,
                    'error': result['error']['error_message'],
                    'error_details': result['error'],
                    'user_message': result['user_message']
                }
        
        except Exception as e:
            self.logger.error(f"Error verifying payment: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def complete_payment_flow(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete the entire 5-step payment flow
        
        Args:
            payment_data (dict): Complete payment information including:
                - customer_data
                - payment_method_data
                - charge_data
                - authorization_data (optional, based on next_action)
        
        Returns:
            dict: Complete payment flow result
        """
        try:
            self.logger.info("Starting complete payment flow")
            
            # Step 1: Create Customer
            customer_result = self.create_customer(payment_data.get('customer_data', {}))
            if not customer_result['success']:
                return customer_result
            
            customer_id = customer_result['customer_id']
            self.logger.info(f"Customer created: {customer_id}")
            
            # Step 2: Create Payment Method
            payment_method_data = payment_data.get('payment_method_data', {})
            payment_method_data['customer_id'] = customer_id  # Link to customer
            
            self.logger.info(f"Creating payment method for customer: {customer_id}")
            payment_method_result = self.create_payment_method(payment_method_data)
            if not payment_method_result['success']:
                return payment_method_result
            
            payment_method_id = payment_method_result['payment_method_id']
            self.logger.info(f"Payment method created: {payment_method_id}")
            
            # Step 3: Initiate Charge
            charge_data = payment_data.get('charge_data', {})
            charge_data['customer_id'] = customer_id
            charge_data['payment_method_id'] = payment_method_id
            
            charge_result = self.initiate_charge(charge_data)
            if not charge_result['success']:
                return charge_result
            
            charge_id = charge_result['charge_id']
            next_action = charge_result.get('next_action')
            self.logger.info(f"Charge initiated: {charge_id}")
            
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
                    
                    auth_result = self.authorize_charge(charge_id, authorization_data)
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
                        'message': 'Payment requires redirect',
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
            
            # Step 5: Verify Payment
            verification_result = self.verify_payment(charge_id)
            if not verification_result['success']:
                return verification_result
            
            self.logger.info("Complete payment flow finished successfully")
            
            return {
                'success': True,
                'message': 'Payment completed successfully',
                'customer_id': customer_id,
                'payment_method_id': payment_method_id,
                'charge_id': charge_id,
                'verification': verification_result,
                'status': verification_result.get('status')
            }
        
        except Exception as e:
            self.logger.error(f"Error in complete payment flow: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def handle_next_action(self, charge_id: str, next_action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle different types of next_action responses
        
        Args:
            charge_id (str): Charge ID
            next_action (dict): Next action information
        
        Returns:
            dict: Next action handling result
        """
        action_type = next_action.get('type')
        
        if action_type == 'requires_pin':
            return {
                'type': 'pin_required',
                'message': 'PIN authorization required',
                'charge_id': charge_id,
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
                'authorization_data': {
                    'type': 'otp',
                    'otp': {
                        'code': '123456'  # Example OTP code
                    }
                }
            }
        
        elif action_type == 'requires_additional_fields':
            # Handle AVS (Address Verification System)
            avs_data = next_action.get('avs', {})
            return {
                'type': 'additional_fields_required',
                'message': 'Address verification required',
                'charge_id': charge_id,
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
                'message': 'Redirect to complete payment',
                'redirect_url': redirect_url,
                'charge_id': charge_id
            }
        
        elif action_type == 'payment_instruction':
            instructions = next_action.get('payment_instruction', {})
            return {
                'type': 'instructions_provided',
                'message': 'Payment instructions available',
                'instructions': instructions,
                'charge_id': charge_id,
                'note': instructions.get('note', 'Please follow the payment instructions')
            }
        
        else:
            return {
                'type': 'unknown',
                'message': f'Unknown action type: {action_type}',
                'charge_id': charge_id
            } 