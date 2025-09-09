"""
Flutterwave v4 API Testing Scenarios
Comprehensive testing framework for different payment scenarios
"""

# Card Testing Scenarios
CARD_SCENARIOS = {
    # Authentication flows
    'auth_pin': 'Mock PIN authentication',
    'auth_pin_3ds': 'Mock failover from PIN to 3DS',
    'auth_3ds': 'Mock 3DS authentication',
    'auth_avs': 'Mock noauth (AVS) flow',
}

# Card Issuer Responses
CARD_ISSUER_RESPONSES = {
    # Success responses
    'approved': 'Transaction approved',
    'partial_approval': 'Partial approval',
    'no_reason_to_decline': 'No reason to decline',
    
    # PIN-related failures
    'incorrect_pin': 'Incorrect PIN entered',
    'cannot_verify_pin': 'Cannot verify PIN',
    'pin_data_required': 'PIN data required',
    'pin_entry_tries_exceeded': 'PIN entry tries exceeded',
    
    # Card-related failures
    'expired_card': 'Card has expired',
    'lost_card_pick_up': 'Lost card - pick up',
    'stolen_card_pick_up': 'Stolen card - pick up',
    'pick_up_card_fraud': 'Pick up card - fraud',
    'pick_up_card_no_fraud': 'Pick up card - no fraud',
    
    # Account-related failures
    'insufficient_funds': 'Insufficient funds',
    'no_checking_account': 'No checking account',
    'no_savings_account': 'No savings account',
    'invalid_account_number': 'Invalid account number',
    
    # Transaction-related failures
    'do_not_honor': 'Do not honor',
    'exceeds_approval_amount_limit': 'Exceeds approval amount limit',
    'exceeds_withdrawal_limit': 'Exceeds withdrawal limit',
    'invalid_amount': 'Invalid amount',
    'invalid_cvv': 'Invalid CVV',
    'invalid_transaction': 'Invalid transaction',
    'transaction_not_permitted_card': 'Transaction not permitted for card',
    'transaction_not_permitted_terminal': 'Transaction not permitted for terminal',
    
    # Security-related failures
    'security_violation': 'Security violation',
    'suspected_fraud': 'Suspected fraud',
    'negative_cvv_result': 'Negative CVV result',
    'blocked_first_use': 'Blocked first use',
    
    # System-related failures
    'error': 'System error',
    'issuer_unavailable': 'Issuer unavailable',
    'system_error': 'System error',
    'file_temporarily_not_available': 'File temporarily not available',
    'unable_to_locate_record_in_file': 'Unable to locate record in file',
    'unable_to_route_transaction': 'Unable to route transaction',
    
    # Other failures
    'cannot_complete_violation_of_law': 'Cannot complete - violation of law',
    'invalid_merchant': 'Invalid merchant',
    'invalid_restricted_service_code': 'Invalid restricted service code',
    'no_action_taken': 'No action taken',
    'no_such_issuer': 'No such issuer',
    'refer_to_issuer': 'Refer to issuer',
    'refer_to_issuer_special_condition': 'Refer to issuer - special condition',
    'reenter_transaction': 'Reenter transaction',
    'transaction_does_not_fulfill_aml_req': 'Transaction does not fulfill AML requirements',
    'unsolicited_reversal': 'Unsolicited reversal',
    'already_reversed': 'Already reversed',
}

# Mobile Money Scenarios
MOBILE_MONEY_SCENARIOS = {
    'default': 'Default flow (notification on mobile device)',
    'auth_redirect': 'Redirect flow (authorization page)',
}

# Transfer Scenarios
TRANSFER_SCENARIOS = {
    # Success scenarios
    'successful': 'Successful transfer',
    
    # Account-related failures
    'account_resolved_failed': 'Account resolution failed',
    'no_account_found': 'No account found',
    
    # Amount-related failures
    'amount_below_limit_error': 'Amount below limit',
    'amount_exceed_limit_error': 'Amount exceeds limit',
    'currency_amount_below_limit': 'Currency amount below limit',
    'currency_amount_exceed_limit': 'Currency amount exceeds limit',
    'invalid_amount': 'Invalid amount',
    'invalid_amount_validation': 'Invalid amount validation',
    
    # Limit-related failures
    'day_limit_error': 'Daily limit error',
    'day_transfer_limit_exceeded': 'Daily transfer limit exceeded',
    'month_limit_error': 'Monthly limit error',
    'month_transfer_limit_exceeded': 'Monthly transfer limit exceeded',
    
    # Balance-related failures
    'insufficient_balance': 'Insufficient balance',
    
    # Currency-related failures
    'invalid_currency': 'Invalid currency',
    'invalid_wallet_currency': 'Invalid wallet currency',
    
    # Reference-related failures
    'duplicate_reference': 'Duplicate reference',
    'invalid_reference': 'Invalid reference',
    'invalid_reference_length': 'Invalid reference length',
    
    # Data-related failures
    'invalid_bulk_data': 'Invalid bulk data',
    'invalid_payouts': 'Invalid payouts',
    'file_too_large': 'File too large',
    
    # Transfer-specific failures
    'blocked_bank': 'Blocked bank',
    'disabled_transfer': 'Disabled transfer',
    'payout_creation_error': 'Payout creation error',
    'unavailable_transfer_option': 'Unavailable transfer option',
}


class FlutterwaveTestScenarios:
    """
    Flutterwave v4 API Testing Scenarios Manager
    """
    
    @staticmethod
    def generate_card_scenario_key(scenario='auth_avs', issuer='approved'):
        """
        Generate scenario key for card testing
        
        Args:
            scenario (str): Authentication scenario (auth_pin, auth_3ds, etc.)
            issuer (str): Issuer response (approved, insufficient_funds, etc.)
        
        Returns:
            str: Formatted scenario key
        """
        if scenario not in CARD_SCENARIOS:
            raise ValueError(f"Invalid card scenario: {scenario}")
        if issuer not in CARD_ISSUER_RESPONSES:
            raise ValueError(f"Invalid issuer response: {issuer}")
        
        return f"scenario:{scenario}&issuer:{issuer}"
    
    @staticmethod
    def generate_mobile_money_scenario_key(scenario='auth_redirect'):
        """
        Generate scenario key for mobile money testing
        
        Args:
            scenario (str): Mobile money scenario (default, auth_redirect)
        
        Returns:
            str: Formatted scenario key
        """
        if scenario not in MOBILE_MONEY_SCENARIOS:
            raise ValueError(f"Invalid mobile money scenario: {scenario}")
        
        return f"scenario:{scenario}"
    
    @staticmethod
    def generate_transfer_scenario_key(scenario='successful'):
        """
        Generate scenario key for transfer testing
        
        Args:
            scenario (str): Transfer scenario (successful, insufficient_balance, etc.)
        
        Returns:
            str: Formatted scenario key
        """
        if scenario not in TRANSFER_SCENARIOS:
            raise ValueError(f"Invalid transfer scenario: {scenario}")
        
        return f"scenario:{scenario}"
    
    @staticmethod
    def get_card_scenarios():
        """Get all available card scenarios"""
        return CARD_SCENARIOS
    
    @staticmethod
    def get_card_issuer_responses():
        """Get all available card issuer responses"""
        return CARD_ISSUER_RESPONSES
    
    @staticmethod
    def get_mobile_money_scenarios():
        """Get all available mobile money scenarios"""
        return MOBILE_MONEY_SCENARIOS
    
    @staticmethod
    def get_transfer_scenarios():
        """Get all available transfer scenarios"""
        return TRANSFER_SCENARIOS
    
    @staticmethod
    def get_successful_scenarios():
        """Get scenarios that result in successful transactions"""
        return {
            'card': {
                'scenario': 'auth_avs',
                'issuer': 'approved',
                'description': 'Successful card payment'
            },
            'mobile_money': {
                'scenario': 'auth_redirect',
                'description': 'Successful mobile money payment'
            },
            'transfer': {
                'scenario': 'successful',
                'description': 'Successful transfer'
            }
        }
    
    @staticmethod
    def get_failure_scenarios():
        """Get common failure scenarios for testing"""
        return {
            'card': [
                {
                    'scenario': 'auth_pin',
                    'issuer': 'incorrect_pin',
                    'description': 'Incorrect PIN'
                },
                {
                    'scenario': 'auth_avs',
                    'issuer': 'insufficient_funds',
                    'description': 'Insufficient funds'
                },
                {
                    'scenario': 'auth_3ds',
                    'issuer': 'expired_card',
                    'description': 'Expired card'
                }
            ],
            'mobile_money': [
                {
                    'scenario': 'auth_redirect',
                    'description': 'Mobile money redirect flow'
                }
            ],
            'transfer': [
                {
                    'scenario': 'insufficient_balance',
                    'description': 'Insufficient balance'
                },
                {
                    'scenario': 'invalid_currency',
                    'description': 'Invalid currency'
                }
            ]
        } 