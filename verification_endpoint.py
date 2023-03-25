from flask import Flask, request, jsonify
from flask_restful import Api
import json
import eth_account
import algosdk

app = Flask(__name__)
api = Api(app)
app.url_map.strict_slashes = False

@app.route('/verify', methods=['GET','POST'])
def verify():
    content = request.get_json(silent=True)
# {'sig': '0x3718eb506f445ecd1d6921532c30af84e89f2faefb17fc8117b75c4570134b4967a0ae85772a8d7e73217a32306016845625927835818d395f0f65d25716356c1c', 
#  'payload': {
#     'message': 'Ethereum test message', 
#     'pk': '0x9d012d5a7168851Dc995cAC0dd810f201E1Ca8AF', 
#     'platform': 'Ethereum'
#   }
# }
    request_payload = content['payload']
    request_sig = content['sig']

    payload_message = json.dumps(request_payload)
    payload_platform = request_payload['platform']
    payload_pk = request_payload['pk']

    #Check if signature is valid
    result = True #Should only be true if signature validates

    if payload_platform == 'Ethereum':
        # The signature should be on the entire payload dictionary not just the single “message” field.
        eth_encoded_msg = eth_account.messages.encode_defunct(text = payload_message)
        eth_pk = eth_account.Account.recover_message(eth_encoded_msg, signature = request_sig)

        if payload_pk == eth_pk:
            result = True
        else: 
            result = False
    
    elif payload_platform == 'Algorand':
        if algosdk.util.verify_bytes(payload_message.encode('utf-8'), request_sig, payload_pk):
            result = True
        else: 
            result = False
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(port='5002')