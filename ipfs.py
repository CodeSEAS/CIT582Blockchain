import requests
import json


def pin_to_ipfs(data):
    assert isinstance(data, dict), f"Error pin_to_ipfs expects a dictionary"
    # YOUR CODE HERE
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    JWT = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiJhMGIyOTYzOS00NWVkLTQwMGQtYTZmMS1hNmEyNGI2YzJmOTMiLCJlbWFpbCI6Im1hbmp1bkBzZWFzLnVwZW5uLmVkdSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJwaW5fcG9saWN5Ijp7InJlZ2lvbnMiOlt7ImlkIjoiRlJBMSIsImRlc2lyZWRSZXBsaWNhdGlvbkNvdW50IjoxfSx7ImlkIjoiTllDMSIsImRlc2lyZWRSZXBsaWNhdGlvbkNvdW50IjoxfV0sInZlcnNpb24iOjF9LCJtZmFfZW5hYmxlZCI6ZmFsc2UsInN0YXR1cyI6IkFDVElWRSJ9LCJhdXRoZW50aWNhdGlvblR5cGUiOiJzY29wZWRLZXkiLCJzY29wZWRLZXlLZXkiOiJiMTgzNTAwMDNiMmNkNWQ5Y2E0MiIsInNjb3BlZEtleVNlY3JldCI6ImE0YTk4MTYzODA0NTMyY2FhMTk0MGI2ZjY4OGE2ZWRlMjAzYWI3MWQ0YzBmZTViMmY4MzQyZGM5MWE2NTAxOTQiLCJpYXQiOjE2NzU2Mzk5NzJ9.GLz401LFSkjASb_iCsJTWTd4sQKmAJ178YyngJv_DCk"
    payload = json.dumps({
        "pinataContent": data
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': JWT
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    dict = json.loads(response.text)
    cid = dict['IpfsHash']
    return cid


# QmYojF4ieWzxjpwKYFHYpGgGvM16D2kvK2ZccwD7FJVtw2

def get_from_ipfs(cid, content_type="json"):
    assert isinstance(cid, str), f"get_from_ipfs accepts a cid in the form of a string"
    # YOUR CODE HERE
    url = f'https://gateway.pinata.cloud/ipfs/{cid}'
    response = json.loads(requests.request("GET", url).text)
    assert isinstance(response, dict), f"get_from_ipfs should return a dict"
    return response


if __name__ == '__main__':
    response = get_from_ipfs('QmYojF4ieWzxjpwKYFHYpGgGvM16D2kvK2ZccwD7FJVtw2')
    print(response)

# API Key: b18350003b2cd5d9ca42
#  API Secret: a4a98163804532caa1940b6f688a6ede203ab71d4c0fe5b2f8342dc91a650194

# JWT: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiJhMGIyOTYzOS00NWVkLTQwMGQtYTZmMS1hNmEyNGI2YzJmOTMiLCJlbWFpbCI6Im1hbmp1bkBzZWFzLnVwZW5uLmVkdSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJwaW5fcG9saWN5Ijp7InJlZ2lvbnMiOlt7ImlkIjoiRlJBMSIsImRlc2lyZWRSZXBsaWNhdGlvbkNvdW50IjoxfSx7ImlkIjoiTllDMSIsImRlc2lyZWRSZXBsaWNhdGlvbkNvdW50IjoxfV0sInZlcnNpb24iOjF9LCJtZmFfZW5hYmxlZCI6ZmFsc2UsInN0YXR1cyI6IkFDVElWRSJ9LCJhdXRoZW50aWNhdGlvblR5cGUiOiJzY29wZWRLZXkiLCJzY29wZWRLZXlLZXkiOiJiMTgzNTAwMDNiMmNkNWQ5Y2E0MiIsInNjb3BlZEtleVNlY3JldCI6ImE0YTk4MTYzODA0NTMyY2FhMTk0MGI2ZjY4OGE2ZWRlMjAzYWI3MWQ0YzBmZTViMmY4MzQyZGM5MWE2NTAxOTQiLCJpYXQiOjE2NzU2Mzk5NzJ9.GLz401LFSkjASb_iCsJTWTd4sQKmAJ178YyngJv_DCk
