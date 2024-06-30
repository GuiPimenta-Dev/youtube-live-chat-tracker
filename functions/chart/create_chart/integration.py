import pytest
import requests
from lambda_forge.constants import BASE_URL


@pytest.mark.integration(method="POST", endpoint="/chart")
def test_create_chart_status_code_is_200():

    response = requests.post(url=f"{BASE_URL}/chart")

    assert response.status_code == 200
