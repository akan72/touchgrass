import random
import streamlit as st
from dune import (
    get_address_labels,
    get_lens_handles,
)
from queries import (
    profiles_to_df,
    followers_to_df,
    get_publications_revenue_by_token,
)

st.title("🌱 touchgrass 🌿")

alex_address = "0xBE5F037E9bDfeA1E5c3c815Eb4aDeB1D9AB0137B"
stani_address = "0x7241DDDec3A6aF367882eAF9651b87E1C7549Dff"
default_addresses = [alex_address, stani_address]

profiles = profiles_to_df(default_addresses, "ownedBy")

if st.button("Get all lens handles"):
    all_handles = get_lens_handles()
    list_sample = random.sample(all_handles, 50)
    profiles = profiles_to_df(list_sample, "handle")

handles = profiles['handle']

handle = st.selectbox(
    label="Choose a lens handle!",
    options=handles,
)

selected_profile = profiles.loc[profiles['handle'] == handle]
eth_address = selected_profile['ownedBy'].values[0]
st.markdown(f"View Address on [Etherscan](https://etherscan.io/address/{eth_address})")
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
if str(image_url) != 'nan':
    if 'ipfs' in image_url and 'https' not in image_url:
        ipfs_object = image_url.split('/')[-1]
        image_url = f'https://lens.infura-ipfs.io/ipfs/{ipfs_object}'
    image_holder.image(image_url)

# Get Dune labels for the address
if st.button(f"Get Dune labels for {handle}"):
    try:
        labels = get_address_labels(eth_address)
        if not labels.empty:
            labels = labels[['name', 'category', 'contributor', 'source']]
            st.write(labels)
        else:
            st.write("No Dune labels found!")
    except Exception as e:
        print(e)
        st.write("No Dune labels found!")

# profile info
col2.markdown(f"""
**{name}**:
\nBio: {bio}
  - Followers: {totalFollowers}, Following: {totalFollowing}
  - Posts: {totalPosts}, Comments: {totalComments}
  - Mirrors: {totalMirrors}, Publications: {totalPublications}, Collects: {totalCollects}
""")

# profile followers
st.markdown("### Follower Set (first 50)")
selected_profile_id = selected_profile['id'].values[0]

follower_set = followers_to_df(selected_profile_id)
follower_set = follower_set.rename(
    columns={
        'defaultProfile_stats_totalFollowers': 'total_followers',
        'defaultProfile_stats_totalFollowing': 'total_following',
        'defaultProfile_stats_totalPosts': 'total_posts',
        'defaultProfile_stats_totalComments': 'total_comments',
        'defaultProfile_stats_totalMirrors': 'total_mirrors',
        'defaultProfile_stats_totalPublications': 'total_publications',
        'defaultProfile_stats_totalCollects': 'total_collects',
    }
)

st.dataframe(follower_set)
st.dataframe(follower_set.describe())

# Follower Metrics
st.markdown("### Publication Revenue")
try:
    revenue_by_token = get_publications_revenue_by_token(selected_profile_id)
    st.dataframe(revenue_by_token)
except Exception as e:
    st.write("No revenue! Oh no!")
