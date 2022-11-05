import streamlit as st
from queries import profiles_to_df

st.title("touchgrass")

stani_address = "0x7241DDDec3A6aF367882eAF9651b87E1C7549Dff"
alex_address = "0xBE5F037E9bDfeA1E5c3c815Eb4aDeB1D9AB0137B"

profiles = profiles_to_df([alex_address, stani_address])
handles = profiles['handle']
st.dataframe(profiles)

handle = st.selectbox(
    label="Select lens handle",
    options=handles,
)

selected_profile = profiles.loc[profiles['handle'] == handle]
st.write(selected_profile)

image_url = selected_profile['original_url'].values[0]

if image_url is not None:
    if 'ipfs' in image_url and 'https' not in image_url:
        ipfs_object = image_url.split('/')[-1]
        image_url = f'https://lens.infura-ipfs.io/ipfs/{ipfs_object}'

    st.image(image_url)
