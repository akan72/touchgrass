import streamlit as st
from queries import (
    profiles_to_df,
    get_follower_set,
)

st.title("touchgrass")

alex_address = "0xBE5F037E9bDfeA1E5c3c815Eb4aDeB1D9AB0137B"
stani_address = "0x7241DDDec3A6aF367882eAF9651b87E1C7549Dff"

profiles = profiles_to_df([alex_address, stani_address])
handles = profiles['handle']

handle = st.selectbox(
    label="Select Lens handle",
    options=handles,
)

selected_profile = profiles.loc[profiles['handle'] == handle]

# TODO: pretty print all of this

st.write(selected_profile)

image_url = selected_profile['original_url'].values[0]

if image_url is not None:
    if 'ipfs' in image_url and 'https' not in image_url:
        ipfs_object = image_url.split('/')[-1]
        image_url = f'https://lens.infura-ipfs.io/ipfs/{ipfs_object}'

    st.image(image_url)

for col in [
    'totalFollowers',
    'totalFollowing',
    'totalPosts',
    'totalComments',
    'totalMirrors',
    'totalPublications',
    'totalCollects',
]:
    st.write(f"{col}: {selected_profile[col].values[0]}")

st.write("Follower set")
selected_profile_id = selected_profile['id'].values[0]

follower_set = get_follower_set(selected_profile_id)
st.dataframe(follower_set)

