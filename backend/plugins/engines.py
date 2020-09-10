import requests
import time


def send(file, URL, SECRET_KEY):
	name = file.name.split(".")[0]
	timestamp = time.time()
	requestId = f'{file.content_type.split("/")[0]}_{timestamp}'

	message = {
		"requestId": requestId,
		"version": "V2",
		"images": [{
			"name": name,
			"format": file.content_type.split("/")[1]
		}],
		"timestamp": str(timestamp)
	}

    payload = {"message": str(message)}

    headers = {"Content-Type": "multipart/form-data", "X-OCR-SECRET": SECRET_KEY}

    response = requests.request("POST", URL, headers=headers, data=payload, files=[file])

    image = response.json().get("image")
    if image:
        return image.values[0].get("fields")
    return None
