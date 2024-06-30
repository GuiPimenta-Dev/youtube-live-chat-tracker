import pytest
import requests
from lambda_forge.constants import BASE_URL

@pytest.mark.integration(method="POST", endpoint="/downloader")
def test_downloader_status_code_is_200():

    response = requests.post(url=f"{BASE_URL}/downloader")

    assert response.status_code == 200 
