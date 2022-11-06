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
transport = AIOHTTPTransport(url=url)
client = Client(transport=transport, fetch_schema_from_transport=True)

@st.cache(ttl=60*10, max_entries=10)
def get_profiles(addresses: List[str], query_type: str):
    query = gql(Template(
        """
        query Profiles {
          profiles(request: { ${query_type}: ${addresses}, limit: 10 }) {
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
        """).substitute(addresses=json.dumps(addresses), query_type=query_type)
    )
    result = client.execute(query)
    return result

def profiles_to_df(profiles: List[str], query_type: str) -> pd.DataFrame:
    profiles = get_profiles(profiles, query_type)
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

@st.cache(ttl=60*10, max_entries=10)
def get_follower_set(profile_id: str):
    query = gql(Template(
        """
        query Followers {
          followers(request: {
                        profileId: "${profile_id}",
                      limit: 50
                     }) {
               items {
              wallet {
                address
                defaultProfile {
                  id
                  name
                  bio
                  handle
                  ownedBy
                  stats {
                    totalFollowers
                    totalFollowing
                    totalPosts
                    totalComments
                    totalMirrors
                    totalPublications
                    totalCollects
                  }
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
        """).substitute(profile_id=profile_id)
    )

    result = client.execute(query)
    return result

@st.cache(ttl=60*10, max_entries=10)
def get_publications_revenue(profile_id: str):
    query = gql(Template(
        """
        query Revenue {
          profilePublicationRevenue(request: { profileId: "${profile_id}", limit: 10 }) {
            items {
              revenue {
                total {
                  asset {
                    name
                    symbol
                    decimals
                    address
                  }
                  value
                }
              }
            }
          }
        }
        """).substitute(profile_id=profile_id)
    )

    result = client.execute(query)
    return result

def get_publications_revenue_by_token(profile_id: str):
    publications_revenue = get_publications_revenue(profile_id)
    publications_df = pd.DataFrame(publications_revenue['profilePublicationRevenue']['items'])
    publications_df = pd.concat([
        #pd.json_normalize(publications_df['publication'], sep='_'),
        pd.json_normalize(publications_df['revenue'], sep='_'),
    ],axis=1)
    publications_df['total_value'] = publications_df['total_value'].astype(float)
    return pd.DataFrame(publications_df.groupby('total_asset_symbol').sum('total_value')['total_value'])

def followers_to_df(address: str) -> pd.DataFrame:
    result = get_follower_set(address)
    follower_set = pd.json_normalize(pd.DataFrame(result['followers']['items'])['wallet'], sep='_')
    return follower_set

if __name__ == "__main__":
    alex_address = "0xBE5F037E9bDfeA1E5c3c815Eb4aDeB1D9AB0137B"
    stani_address = "0x7241DDDec3A6aF367882eAF9651b87E1C7549Dff"

    profiles = profiles_to_df([alex_address, stani_address], "ownedBy")
    followers_df = followers_to_df("0x01")
    publications_revnue = get_publications_revenue_by_token("0x01")
