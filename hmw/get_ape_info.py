from web3 import Web3
from web3.contract import Contract
from web3.providers.rpc import HTTPProvider
import requests
import json
import time

bayc_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
contract_address = Web3.toChecksumAddress(bayc_address)

#You will need the ABI to connect to the contract
#The file 'abi.json' has the ABI for the bored ape contract
#In general, you can get contract ABIs from etherscan
#https://api.etherscan.io/api?module=contract&action=getabi&address=0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D
with open('/home/codio/workspace/abi.json', 'r') as f:
	abi = json.load(f) 

############################
#Connect to an Ethereum node
# api_url = #YOU WILL NEED TO TO PROVIDE THE URL OF AN ETHEREUM NODE
api_url = f"https://eth-mainnet.g.alchemy.com/v2/kBQFL6fReQL7Rafl6CSLVbtB9nCRfszA"
provider = HTTPProvider(api_url)
web3 = Web3(provider)

def get_ape_info(apeID):
    assert isinstance(apeID, int), f"{apeID} is not an int"
    assert 1 <= apeID, f"{apeID} must be at least 1"

    data = {'owner': "", 'image': "", 'eyes': ""}

    # YOUR CODE HERE
    url = f'https://gateway.pinata.cloud/ipfs/QmeSjSinHpPnmXmspMjwiXyN6zS4E9zccariGR3jxcaWtq/{apeID}'
    r = requests.get(url)
    response = json.loads(r.text)
    data['image'] = response['image']
    for attribute in response['attributes']:
        if attribute['trait_type'] == 'Eyes':
            data['eyes'] = attribute['value']
    
    contract = web3.eth.contract(address=contract_address,abi=abi)
    supply = contract.functions.totalSupply().call()
    print( f"Supply = {supply}" )

    owner_address = contract.functions.owner().call()
    token_uri = contract.functions.tokenURI(1).call()

    print('Current owner:', owner_address)
    print('Token URI:', token_uri)
    data['owner'] = owner_address
    assert isinstance(data, dict), f'get_ape_info{apeID} should return a dict'
    assert all([a in data.keys() for a in
                ['owner', 'image', 'eyes']]), f"return value should include the keys 'owner','image' and 'eyes'"
    return data
