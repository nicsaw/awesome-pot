import zipfile
import glob
import requests

EXTENSIONS = ["**/*.json", "**/*.json.*", "**/*.log", "**/*.log.*", "**/*.csv", ]
ZIP_FILENAME = "data.zip"
UPLOAD_URL = "https://file.io"

def zip_files():
    files_to_zip = []

    for ext in EXTENSIONS:
        files_to_zip.extend(glob.glob(ext, recursive=True))

    with zipfile.ZipFile(ZIP_FILENAME, 'w') as zipf:
        for file in files_to_zip:
            zipf.write(file)
    print(f"Zipped files into {ZIP_FILENAME}")

def upload_file():
    with open(ZIP_FILENAME, "rb") as file:
        response = requests.post(UPLOAD_URL, files={"file": file})

    if response.status_code == 200:
        response_json = response.json()
        print(response_json)
        print(f"Link: {response_json.get("link")}")
    else:
        print(f"Failed to upload file {ZIP_FILENAME}")
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

if __name__ == "__main__":
    try:
        zip_files()
        upload_file()
    except Exception as e:
        print(e)