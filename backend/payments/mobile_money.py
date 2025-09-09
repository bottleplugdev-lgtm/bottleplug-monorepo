"""
Flutterwave Mobile Money Payments Implementation
Follows the official Flutterwave v4 API documentation for mobile money payments
"""

import logging
import requests
import time
from typing import Dict, Any, Optional, List
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class FlutterwaveMobileMoney:
    """
    Flutterwave Mobile Money Payments Implementation
    Handles mobile money payment flow according to official Flutterwave v4 API documentation
    """
    
    # Supported countries and their mobile money networks
    SUPPORTED_COUNTRIES = {
        '226': {  # Burkina Faso
            'currency': 'XOF',
            'networks': ['mobicash', 'orange'],
            'region': 'West Africa'
        },
        '237': {  # Cameroon
            'currency': 'XAF',
            'networks': ['mtn', 'orange'],
            'region': 'Central Africa'
        },
        '225': {  # Côte d'Ivoire
            'currency': 'XOF',
            'networks': ['moov', 'mtn', 'orange', 'wave'],
            'region': 'West Africa'
        },
        '233': {  # Ghana
            'currency': 'GHS',
            'networks': ['airteltigo', 'mtn', 'vodafone'],
            'region': 'West Africa'
        },
        '254': {  # Kenya
            'currency': 'KES',
            'networks': ['airtel', 'mpesa'],
            'region': 'East Africa'
        },
        '265': {  # Malawi
            'currency': 'MWK',
            'networks': ['airtel'],
            'region': 'East Africa'
        },
        '250': {  # Rwanda
            'currency': 'RWF',
            'networks': ['airtel', 'mtn'],
            'region': 'East Africa'
        },
        '221': {  # Senegal
            'currency': 'XOF',
            'networks': ['emoney', 'freemoney', 'orange'],
            'region': 'West Africa'
        },
        '255': {  # Tanzania
            'currency': 'TZS',
            'networks': ['airtel', 'tigo', 'halopesa', 'vodafone'],
            'region': 'East Africa'
        },
        '256': {  # Uganda
            'currency': 'UGX',
            'networks': ['airtel', 'mtn'],
            'region': 'East Africa'
        }
    }
    
    def __init__(self):
        from .services import FlutterwaveService
        self.service = FlutterwaveService()
        self.logger = logging.getLogger(__name__)
    
    def validate_country_network(self, country_code: str, network: str) -> Dict[str, Any]:
        """
        Validate country code and network combination
        
        Args:
            country_code (str): Country code (e.g., 'GH', 'KE')
            network (str): Mobile money network (e.g., 'mtn', 'airtel')
        
        Returns:
            dict: Validation result
        """
        if country_code not in self.SUPPORTED_COUNTRIES:
            return {
                'valid': False,
                'error': f'Country {country_code} is not supported for mobile money payments'
            }
        
        country_info = self.SUPPORTED_COUNTRIES[country_code]
        if network.lower() not in [n.lower() for n in country_info['networks']]:
            return {
                'valid': False,
                'error': f'Network {network} is not supported in {country_code}. Supported networks: {country_info["networks"]}'
            }
        
        return {
            'valid': True,
            'country_info': country_info,
            'currency': country_info['currency'],
            'region': country_info['region']
        }
    
    def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 1: Create a Customer or retrieve existing customer
        
        Args:
            customer_data (dict): Customer information including:
                - email (required)
                - name (dict with first, middle, last)
                - phone (dict with country_code, number)
                - address (dict with city, country, line1, line2, postal_code, state)
        
        Returns:
            dict: Customer creation/retrieval result
        """
        try:
            # Validate required fields
            if not customer_data.get('email'):
                return {
                    'success': False,
                    'error': 'Email is required for customer creation'
                }
            
            email = customer_data['email']
            
            # First, try to retrieve existing customer by email
            self.logger.info(f"Checking if customer exists with email: {email}")
            existing_customer = self._get_customer_by_email(email)
            
            if existing_customer:
                self.logger.info(f"Customer already exists: {existing_customer['id']}")
                return {
                    'success': True,
                    'customer_id': existing_customer['id'],
                    'customer_data': existing_customer,
                    'message': 'Customer retrieved successfully',
                    'existing': True
                }
            
            # Customer doesn't exist, create new one
            self.logger.info(f"Creating new customer with email: {email}")
            
            # Prepare customer payload
            payload = {
                'email': email
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
                'source': 'mobile_money',
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
                    'message': 'Customer created successfully',
                    'existing': False
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
    
    def _get_customer_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve customer by email address
        
        Args:
            email (str): Customer email address
        
        Returns:
            dict: Customer data if found, None otherwise
        """
        try:
            headers = self.service._get_headers(include_idempotency=False, include_trace=True)
            response = requests.get(
                f'{self.service.base_url}/customers?email={email}',
                headers=headers,
                timeout=30
            )
            
            success, result = self.service.error_handler.handle_response(response, "Customer retrieval")
            
            if success and result['data']['data']:
                # Return the first customer found with this email
                return result['data']['data'][0]
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error retrieving customer by email: {e}")
            return None
    
    def create_mobile_money_payment_method(self, mobile_money_data: Dict[str, Any], customer_id: str = None) -> Dict[str, Any]:
        """
        Step 2: Create Mobile Money Payment Method
        
        Args:
            mobile_money_data (dict): Mobile money information including:
                - country_code (required)
                - network (required)
                - phone_number (required)
            customer_id (str): Optional customer ID to link payment method
        
        Returns:
            dict: Payment method creation result
        """
        try:
            # Validate required fields
            required_fields = ['country_code', 'network', 'phone_number']
            for field in required_fields:
                if field not in mobile_money_data:
                    return {
                        'success': False,
                        'error': f'{field.title()} is required for mobile money payment method'
                    }
            
            # Validate country and network
            validation = self.validate_country_network(
                mobile_money_data['country_code'],
                mobile_money_data['network']
            )
            
            if not validation['valid']:
                return {
                    'success': False,
                    'error': validation['error']
                }
            
            # Get currency for the country
            country_info = self.SUPPORTED_COUNTRIES.get(mobile_money_data['country_code'], {})
            currency = country_info.get('currency', 'GHS')
            
            # Prepare payload
            payload = {
                'type': 'mobile_money',
                'mobile_money': {
                    'country_code': mobile_money_data['country_code'],
                    'network': mobile_money_data['network'],
                    'phone_number': mobile_money_data['phone_number']
                },
                'currency': currency  # Add currency to payment method
            }
            
            # Add customer_id if provided
            if customer_id:
                payload['customer_id'] = customer_id
            
            # Make API request
            headers = self.service._get_headers(include_idempotency=True, include_trace=True)
            
            # Log the payload for debugging
            self.logger.info(f"Mobile money payment method payload: {payload}")
            
            response = requests.post(
                f'{self.service.base_url}/payment-methods',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Handle response
            success, result = self.service.error_handler.handle_response(response, "Mobile money payment method creation")
            
            if success:
                payment_method_info = result['data']['data']
                self.logger.info(f"Mobile money payment method created successfully: {payment_method_info['id']}")
                
                return {
                    'success': True,
                    'payment_method_id': payment_method_info['id'],
                    'payment_method_data': payment_method_info,
                    'message': 'Mobile money payment method created successfully'
                }
            else:
                return {
                    'success': False,
                    'error': result['error']['error_message'],
                    'error_details': result['error'],
                    'user_message': result['user_message']
                }
        
        except Exception as e:
            self.logger.error(f"Error creating mobile money payment method: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def initiate_mobile_money_charge(self, charge_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 3: Initiate Mobile Money Charge
        
        Args:
            charge_data (dict): Charge information including:
                - reference (unique transaction reference)
                - currency (must match country currency)
                - customer_id (from step 1)
                - payment_method_id (from step 2)
                - amount (transaction amount)
                - redirect_url (optional)
                - meta (optional metadata)
                - scenario (optional, for testing)
        
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
            
            # Add scenario key if provided (for testing)
            if 'scenario' in charge_data:
                headers['X-Scenario-Key'] = charge_data['scenario']
            
            # Log the payload for debugging
            self.logger.info(f"Mobile money charge payload: {payload}")
            
            response = requests.post(
                f'{self.service.base_url}/charges',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Handle response
            success, result = self.service.error_handler.handle_response(response, "Mobile money charge initiation")
            
            if success:
                charge_info = result['data']['data']
                self.logger.info(f"Mobile money charge initiated successfully: {charge_info['id']}")
                
                return {
                    'success': True,
                    'charge_id': charge_info['id'],
                    'charge_data': charge_info,
                    'next_action': charge_info.get('next_action'),
                    'status': charge_info.get('status'),
                    'message': 'Mobile money charge initiated successfully'
                }
            else:
                return {
                    'success': False,
                    'error': result['error']['error_message'],
                    'error_details': result['error'],
                    'user_message': result['user_message']
                }
        
        except Exception as e:
            self.logger.error(f"Error initiating mobile money charge: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_mobile_money_payment(self, charge_id: str) -> Dict[str, Any]:
        """
        Step 4: Verify Mobile Money Payment
        
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
            success, result = self.service.error_handler.handle_response(response, "Mobile money payment verification")
            
            if success:
                charge_info = result['data']['data']
                self.logger.info(f"Mobile money payment verified successfully: {charge_id}")
                
                return {
                    'success': True,
                    'charge_id': charge_id,
                    'charge_data': charge_info,
                    'status': charge_info.get('status'),
                    'amount': charge_info.get('amount'),
                    'currency': charge_info.get('currency'),
                    'reference': charge_info.get('reference'),
                    'message': 'Mobile money payment verified successfully'
                }
            else:
                return {
                    'success': False,
                    'error': result['error']['error_message'],
                    'error_details': result['error'],
                    'user_message': result['user_message']
                }
        
        except Exception as e:
            self.logger.error(f"Error verifying mobile money payment: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def complete_mobile_money_flow(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete the entire mobile money payment flow
        
        Args:
            payment_data (dict): Complete payment information including:
                - customer_data
                - mobile_money_data
                - charge_data
                - scenario (optional, for testing)
        
        Returns:
            dict: Complete payment flow result
        """
        try:
            self.logger.info("Starting complete mobile money payment flow")
            
            # Step 1: Create Customer
            customer_result = self.create_customer(payment_data.get('customer_data', {}))
            if not customer_result['success']:
                return customer_result
            
            customer_id = customer_result['customer_id']
            self.logger.info(f"Customer created: {customer_id}")
            
            # Step 2: Create Mobile Money Payment Method
            mobile_money_data = payment_data.get('mobile_money_data', {})
            
            payment_method_result = self.create_mobile_money_payment_method(mobile_money_data, customer_id)
            if not payment_method_result['success']:
                return payment_method_result
            
            payment_method_id = payment_method_result['payment_method_id']
            self.logger.info(f"Mobile money payment method created: {payment_method_id}")
            
            # Step 3: Initiate Mobile Money Charge
            charge_data = payment_data.get('charge_data', {})
            charge_data['customer_id'] = customer_id
            charge_data['payment_method_id'] = payment_method_id
            
            # Add scenario if provided
            if 'scenario' in payment_data:
                charge_data['scenario'] = payment_data['scenario']
            
            charge_result = self.initiate_mobile_money_charge(charge_data)
            if not charge_result['success']:
                return charge_result
            
            charge_id = charge_result['charge_id']
            next_action = charge_result.get('next_action')
            self.logger.info(f"Mobile money charge initiated: {charge_id}")
            
            # Step 4: Handle Next Action
            if next_action:
                action_type = next_action.get('type')
                self.logger.info(f"Next action required: {action_type}")
                
                if action_type == 'payment_instruction':
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
                
                elif action_type == 'redirect_url':
                    redirect_url = next_action.get('redirect_url', {}).get('url')
                    return {
                        'success': True,
                        'message': 'Mobile money payment requires redirect',
                        'charge_id': charge_id,
                        'redirect_url': redirect_url,
                        'next_action': next_action,
                        'status': 'pending'
                    }
            
            # Step 5: Verify Mobile Money Payment
            verification_result = self.verify_mobile_money_payment(charge_id)
            if not verification_result['success']:
                return verification_result
            
            self.logger.info("Complete mobile money payment flow finished successfully")
            
            return {
                'success': True,
                'message': 'Mobile money payment completed successfully',
                'customer_id': customer_id,
                'payment_method_id': payment_method_id,
                'charge_id': charge_id,
                'verification': verification_result,
                'status': verification_result.get('status')
            }
        
        except Exception as e:
            self.logger.error(f"Error in complete mobile money payment flow: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_supported_countries(self) -> Dict[str, Any]:
        """
        Get list of supported countries and their mobile money networks
        
        Returns:
            dict: Supported countries information
        """
        return {
            'success': True,
            'supported_countries': self.SUPPORTED_COUNTRIES,
            'total_countries': len(self.SUPPORTED_COUNTRIES),
            'regions': {
                'West Africa': ['BF', 'CI', 'GH', 'SN'],
                'Central Africa': ['CM'],
                'East Africa': ['KE', 'MW', 'RW', 'TZ', 'UG']
            }
        }
    
    def handle_mobile_money_next_action(self, charge_id: str, next_action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle different mobile money next_action responses
        
        Args:
            charge_id (str): Charge ID
            next_action (dict): Next action information
        
        Returns:
            dict: Next action handling result
        """
        action_type = next_action.get('type')
        
        if action_type == 'payment_instruction':
            instructions = next_action.get('payment_instruction', {})
            note = instructions.get('note', 'Please follow the payment instructions')
            return {
                'type': 'payment_instruction',
                'message': 'Payment instructions provided',
                'charge_id': charge_id,
                'instructions': instructions,
                'note': note,
                'flow_type': 'push_notification'
            }
        
        elif action_type == 'redirect_url':
            redirect_url = next_action.get('redirect_url', {}).get('url')
            return {
                'type': 'redirect_required',
                'message': 'Redirect to complete payment',
                'redirect_url': redirect_url,
                'charge_id': charge_id,
                'flow_type': 'redirect'
            }
        
        else:
            return {
                'type': 'unknown',
                'message': f'Unknown action type: {action_type}',
                'charge_id': charge_id
            } 