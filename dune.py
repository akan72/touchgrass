import streamlit as st
import requests
import time
import pandas as pd
from typing import Dict, List
import os

# setup auth
api_key = os.environ['DUNE_API_KEY'] # get api key from environment
HEADERS = {
    'x-dune-api-key': api_key
}

# ***** Dune Utilities *****
def execute_query(query_id: str, data: Dict=None) -> Dict:
    """
    Execute a query

    @param query_id: query id
    @param data: data to pass to query {parameter: value}
    @return: response to execution {'execution_id': 'string', 'state': 'ENUM'}
    """
    url = f'https://api.dune.com/api/v1/query/{query_id}/execute'

    if data:
        payload = {"query_parameters": data}
        response = requests.post(url, json=payload, headers=HEADERS).json()
    else:
        response = requests.post(url, headers=HEADERS).json()

    return response

def get_execution_status(execution_id: str) -> Dict:
    """
    Get the status of a query execution

    Possible states:
        QUERY_STATE_PENDING   : query execution is waiting for execution slot
        QUERY_STATE_EXECUTING : query is executing
        QUERY_STATE_FAILED    : execution failed
        QUERY_STATE_COMPLETED : execution completed successfully
        QUERY_STATE_CANCELLED : execution cancelled by user
        QUERY_STATE_EXPIRED   : query execution expired, result no longer available

    @param execution_id: execution id
    @return: execution status
    """
    url = f'https://api.dune.com/api/v1/execution/{execution_id}/status'
    response = requests.get(url, headers=HEADERS).json()
    return response

def get_execution_results(execution_id: str) -> pd.DataFrame:
    """
    Get the results of a query execution

    @param execution_id: execution id
    @return: execution results
    """
    url = f'https://api.dune.com/api/v1/execution/{execution_id}/results'
    response = requests.get(url, headers=HEADERS).json()

    if "result" not in response:
        print(response)

    # unpack results
    rows = response['result']['rows']
    cols = response['result']['metadata']['column_names']

    # create DataFrame
    df = pd.DataFrame(rows, columns=cols)
    return df

def get_query_results(query_id: str, data: Dict=None, sleep: int = 2) -> pd.DataFrame:
    """
    Get the results of a query

    @param query_id: query id
    @param sleep: time to sleep between checking execution status
    @return: execution results
    """

    # submit query & get execution id
    execution_response = execute_query(query_id, data)
    if "execution_id" not in execution_response:
        print(execution_response)
        return pd.DataFrame()
    execution_id = execution_response['execution_id']

    # get execution status
    execution_status = get_execution_status(execution_id)

    # wait for execution to complete
    while execution_status['state'] == 'QUERY_STATE_EXECUTING':
        print(execution_status)
        time.sleep(sleep)
        execution_status = get_execution_status(execution_id)

    # get execution results
    df = get_execution_results(execution_id)
    return df

# ***** lens-profiles *****
@st.cache(allow_output_mutation=True)
def get_lens_handles() -> List[str]:
    query_id = '1527541'
    df = get_query_results(query_id)

    # convert vars col from string to dict
    df['vars'] = df['vars'].apply(lambda x: eval(x))
    handles = df["vars"].apply(lambda x: x['handle']).tolist()
    return handles

# ***** Wallet Labeling *****
@st.cache(allow_output_mutation=True)
def get_address_labels(address: str) -> pd.DataFrame:
    """
    Get the labels for an address

    @param address: address, assuming this is an EVM address
    @return: labels
    """
    query_id = 1531914
    address = address.lower()

    data = {
        "address": address
    }

    df = get_query_results(query_id, data=data)
    return df

if __name__ == "__main__":
    lens_handles = get_lens_handles()
    print(lens_handles)

    address = "0xBE5F037E9bDfeA1E5c3c815Eb4aDeB1D9AB0137B"
    df = get_address_labels(address)
    print(df)
