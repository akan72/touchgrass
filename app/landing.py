import streamlit as st
from queries import (
    profiles_to_df,
    get_follower_set,
)

st.title("🌱 touchgrass 🌿")

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
image_url = selected_profile['original_url'].values[0]

# get data from profile
name = selected_profile['name'].values[0]
bio = selected_profile['bio'].values[0]
totalFollowers = selected_profile['totalFollowers'].values[0]
totalFollowing = selected_profile['totalFollowing'].values[0]
totalPosts = selected_profile['totalPosts'].values[0]
totalComments = selected_profile['totalComments'].values[0]
totalMirrors = selected_profile['totalMirrors'].values[0]
totalPublications = selected_profile['totalPublications'].values[0]
totalCollects = selected_profile['totalCollects'].values[0]


# ***** APP Visuals *****
col1, col2 = st.columns(2)

# profile image, default to empty
image_holder = col1.empty()
image_holder.image('https://via.placeholder.com/150')

# Check for profile image
if image_url is not None:
    if 'ipfs' in image_url and 'https' not in image_url:
        ipfs_object = image_url.split('/')[-1]
        image_url = f'https://lens.infura-ipfs.io/ipfs/{ipfs_object}'
    image_holder.image(image_url)

# profile info
col2.write(f'**{name}**: {bio}')
col2.write(f'Followers: {totalFollowers} Following: {totalFollowing}')
col2.write(f'Posts: {totalPosts} Comments: {totalComments}')
col2.write(f'Mirrors: {totalMirrors} Publications: {totalPublications} Collects: {totalCollects}')

# profile followers
st.write("Follower set")
selected_profile_id = selected_profile['id'].values[0]

follower_set = get_follower_set(selected_profile_id)
st.dataframe(follower_set)
