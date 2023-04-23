#!/usr/bin/python3

from algosdk.v2client import algod
from algosdk import mnemonic
from algosdk import transaction
from algosdk import account

#Connect to Algorand node maintained by PureStake
algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "B3SU4KcVKi94Jap2VXkK83xx38bsv95K5UZm2lab"
#algod_token = 'IwMysN3FSZ8zGVaQnoUIJ9RXolbQ5nRY62JRqF2H'
headers = {
   "X-API-Key": algod_token,
}

acl = algod.AlgodClient(algod_token, algod_address, headers)
min_balance = 100000 #https://developer.algorand.org/docs/features/accounts/#minimum-balance

def send_tokens( receiver_pk, tx_amount ):
    print(f"send_tokens1")
    params = acl.suggested_params()
    gen_hash = params.gh
    first_valid_round = params.first
    tx_fee = params.min_fee
    last_valid_round = params.last

    # sk: 2eZvFiNAuR9tf8xfqGDzjGr3ePTWQjSdt8icGdFKKEdBo19nzTajtFYIjoJnVNCLocabcK+W4yaX+Kk5l5fuTg==  
    # pk:  IGRV6Z6NG2R3IVQIR2BGOVGQROQ4NG3QV6LOGJUX7CUTTF4X5ZHC37C66M

    #Your code here
    # sk, sender_pk = account.generate_account()

    sk = '2eZvFiNAuR9tf8xfqGDzjGr3ePTWQjSdt8icGdFKKEdBo19nzTajtFYIjoJnVNCLocabcK+W4yaX+Kk5l5fuTg=='
    sender_pk = 'IGRV6Z6NG2R3IVQIR2BGOVGQROQ4NG3QV6LOGJUX7CUTTF4X5ZHC37C66M'


    sign = transaction.PaymentTxn(sender_pk, tx_fee, first_valid_round, last_valid_round, gen_hash, receiver_pk, tx_amount)
    signed_sign = sign.sign(sk)
    txid = sign.get_txid()
    acl.send_transaction(signed_sign)

    print(f"sender_pk: {sender_pk}; txid: {txid}")

    return sender_pk, txid

# Function from Algorand Inc.
def wait_for_confirmation(client, txid):

    print(f"wait_for_confirmation txid: {txid}")
    """
    Utility function to wait until the transaction is
    confirmed before proceeding.
    """
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print("Waiting for confirmation")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')))
    return txinfo

