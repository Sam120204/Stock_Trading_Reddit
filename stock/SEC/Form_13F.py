from sec_api import QueryApi

# Initialize the API with your API key
queryApi = QueryApi(api_key="key")

# Define the query to get recent 13F filings
query = {
    "query": "formType:\"13F-HR\"",
    "from": "0",
    "size": "10",
    "sort": [{"filedAt": {"order": "desc"}}]
}

# Fetch the filings
filings = queryApi.get_filings(query)

# Process each filing to extract holdings
for filing in filings['filings']:
    print(f"Filing Date: {filing['filedAt']}")
    print(f"Institution: {filing['companyName']} (CIK: {filing['cik']})")
    print("Holdings:")
    for holding in filing.get('holdings', []):
        name_of_issuer = holding['nameOfIssuer']
        cusip = holding['cusip']
        shares = holding['shrsOrPrnAmt']['sshPrnamt']
        value = holding['value']  # Value is in thousands
        print(f"  - {name_of_issuer} (CUSIP: {cusip})")
        print(f"    Shares: {shares}")
        print(f"    Value (in thousands): ${value}")
    print("----")
