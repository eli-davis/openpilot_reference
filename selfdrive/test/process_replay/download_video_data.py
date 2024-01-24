# B"H

import requests
from tqdm import tqdm


def download_video_data(bool_main_cam, route_id, segment_i): #, total_segments=11):

    #base_url = f"https://commadataci.blob.core.windows.net/openpilotci/{route_id}"
    BASE_URL = "https://commadataci.blob.core.windows.net/openpilotci/"



    if bool_main_cam == True:
        camera_name = "fcamera"
        file_prefix = "main_cam"

    else:
        camera_name = "ecamera"
        file_prefix = "wide_cam"


    ### Loop over each segment
    ##for i in tqdm(range(total_segments)):

    if True:
        # Construct the URL for the current segment
        ##segment_url = f"{base_url}/{segment_i}/{camera_name}.hevc"
        segment_url = BASE_URL + f"{route_id.replace('|', '/')}/{segment_i}/{camera_name}.hevc"

        # Send a GET request to the URL
        response = requests.get(segment_url)

        # Check if the request was successful
        if response.status_code == 200:
            # Write the content of the response to a file
            with open(f"{file_prefix}_segment_{segment_i}.hevc", "wb") as f:
                f.write(response.content)
        else:
            print(f"Failed to download segment {segment_i}. Status code: {response.status_code}")



def _download():

    source_segment = "54827bf84c38b14f|2023-01-26--21-59-07--4" # FORD.BRONCO_SPORT_MK1
    route_id, segment_i = source_segment.rsplit("--", 1)


    download_video_data(bool_main_cam=True, route_id=route_id, segment_i=segment_i)
    download_video_data(bool_main_cam=False, route_id=route_id, segment_i=segment_i)

if __name__ == "__main__":
    _download()
