import gql
import json
import pandas as pd
import streamlit as st

from string import Template
from typing import List

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport, log as requests_logger

import logging
logging.basicConfig(level=logging.INFO)
requests_logger.setLevel(logging.WARNING)

url = "https://api.lens.dev"

@st.cache(ttl=60*10, max_entries=10)
def get_profiles_owned_by(addresses: List[str]):
    transport = AIOHTTPTransport(url=url)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    query = gql(Template(
        """
        query Profiles {
          profiles(request: { ownedBy: ${addresses}, limit: 10 }) {
            items {
              id
              name
              bio
              attributes {
                displayType
                traitType
                key
                value
              }
              followNftAddress
              metadata
              isDefault
              picture {
                ... on NftImage {
                  contractAddress
                  tokenId
                  uri
                  verified
                }
                ... on MediaSet {
                  original {
                    url
                    mimeType
                  }
                }
                __typename
              }
              handle
              coverPicture {
                ... on NftImage {
                  contractAddress
                  tokenId
                  uri
                  verified
                }
                ... on MediaSet {
                  original {
                    url
                    mimeType
                  }
                }
                __typename
              }
              ownedBy
              dispatcher {
                address
                canUseRelay
              }
              stats {
                totalFollowers
                totalFollowing
                totalPosts
                totalComments
                totalMirrors
                totalPublications
                totalCollects
              }
              followModule {
                ... on FeeFollowModuleSettings {
                  type
                  amount {
                    asset {
                      symbol
                      name
                      decimals
                      address
                    }
                    value
                  }
                  recipient
                }
                ... on ProfileFollowModuleSettings {
                 type
                }
                ... on RevertFollowModuleSettings {
                 type
                }
              }
            }
            pageInfo {
              prev
              next
              totalCount
            }
          }
        }
        """).substitute(addresses=json.dumps(addresses))
    )
    result = client.execute(query)
    return result

def profiles_to_df(profiles: List[str]) -> pd.DataFrame:
    profiles = get_profiles_owned_by(profiles)
    profiles = pd.DataFrame(profiles["profiles"]["items"])
    profiles = pd.concat([
            profiles.drop('stats', axis=1),
            profiles['stats'].apply(pd.Series),
            pd.json_normalize(profiles['picture'], sep='_'),
            #pd.json_normalize(profiles['coverPicture'], record_prefix='cover_', sep='_'),
        ],
     axis=1
    )
    profiles = profiles.drop(
        [
            'attributes',
            'picture',
            'coverPicture',
            'dispatcher',
            'followModule',
            '__typename',
            'original_mimeType'
        ],
        axis=1
    )

    return profiles

