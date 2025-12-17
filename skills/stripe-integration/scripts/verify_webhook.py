#!/usr/bin/env python3
"""Verify Stripe webhook signature (for testing)."""
import hmac
import hashlib
import sys
import time

def verify_signature(payload, signature, secret):
    """
    Verify Stripe webhook signature.

    Args:
        payload: Raw request body
        signature: stripe-signature header value
        secret: Webhook secret (whsec_...)

    Returns:
        bool: True if signature is valid
    """
    # Parse signature header
    sig_parts = {}
    for part in signature.split(','):
        key, value = part.split('=')
        sig_parts[key] = value

    timestamp = sig_parts.get('t')
    sig_hash = sig_parts.get('v1')

    if not timestamp or not sig_hash:
        print("❌ Invalid signature format")
        return False

    # Check timestamp (prevent replay attacks)
    current_time = int(time.time())
    if abs(current_time - int(timestamp)) > 300:  # 5 minutes tolerance
        print("❌ Timestamp too old (replay attack?)")
        return False

    # Compute expected signature
    signed_payload = f"{timestamp}.{payload}"
    expected_sig = hmac.new(
        secret.encode('utf-8'),
        signed_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # Compare signatures
    if hmac.compare_digest(expected_sig, sig_hash):
        print("✅ Signature is valid")
        return True
    else:
        print("❌ Signature verification failed")
        print(f"Expected: {expected_sig}")
        print(f"Got: {sig_hash}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: verify_webhook.py <payload> <signature> <secret>")
        print("")
        print("Example:")
        print('  verify_webhook.py \'{"type":"test"}\' \'t=123,v1=abc\' whsec_...')
        sys.exit(1)

    payload = sys.argv[1]
    signature = sys.argv[2]
    secret = sys.argv[3]

    valid = verify_signature(payload, signature, secret)
    sys.exit(0 if valid else 1)
