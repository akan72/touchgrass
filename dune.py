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
def execute_query(query_id: str) -> Dict:
    """
    Execute a query

    @param query_id: query id
    @return: response to execution {'execution_id': 'string', 'state': 'ENUM'}
    """
    url = f'https://api.dune.com/api/v1/query/{query_id}/execute'
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

    # put results in a dataframe
    df = pd.DataFrame(response['result']['rows'])
    df.columns = response['result']['metadata']['column_names']
    return df

def get_query_results(query_id: str, sleep: int = 2) -> pd.DataFrame:
    """
    Get the results of a query

    @param query_id: query id
    @param sleep: time to sleep between checking execution status
    @return: execution results
    """

    # submit query & get execution id
    execution_response = execute_query(query_id)
    execution_id = execution_response['execution_id']

    # get execution status
    execution_status = get_execution_status(execution_id)

    # wait for execution to complete
    while execution_status['state'] != 'QUERY_STATE_COMPLETED':
        print(execution_status)
        time.sleep(sleep)
        execution_status = get_execution_status(execution_id)

    # get execution results
    df = get_execution_results(execution_id)
    return df

# ***** lens-profiles *****
def get_lens_handles() -> List[str]:
    query_id = '1527541'
    df = get_query_results(query_id)

    # convert vars col from string to dict
    df['vars'] = df['vars'].apply(lambda x: eval(x))
    handles = df["vars"].apply(lambda x: x['handle']).tolist()
    return handles

handles = get_lens_handles()
print(handles)
