import os
import requests
from django.conf import settings


def extract_tahun_ajaran(tahun_ajaran: str) -> dict:
    """Extract tahun ajaran string to make it tahun ajaran awal dan akhir
    ```
    in: '2019/2020' 
    out: {
        'tahun_ajaran_awal': 2019,
        'tahun_ajaran_akhir': 2020
    }
    ```

    Args:
        tahun_ajaran (str): Tahun ajaran

    Returns:
        dict: Tahun ajaran awal dan akhir
    """
    
    result = {
        'tahun_ajaran_awal': 0,
        'tahun_ajaran_akhir': 0
    }

    list_split_result = tahun_ajaran.split('/')
    list_integer_split_result = []

    # Convert to integer
    for split_result in list_split_result[:2]:
        try:
            integer_split_result = int(split_result)
        except ValueError:
            if settings.DEBUG: 
                print('Cannot split {} to integer'.split(split_result))
            continue

        list_integer_split_result.append(integer_split_result)

    if len(list_integer_split_result) != 2: return result

    # Sort tahun ajaran
    list_integer_split_result.sort()
    tahun_ajaran_awal = list_integer_split_result[0]
    tahun_ajaran_akhir = list_integer_split_result[1]

    # Validate tahun ajaran
    if tahun_ajaran_akhir - tahun_ajaran_awal == 1:
        result['tahun_ajaran_awal'] = tahun_ajaran_awal
        result['tahun_ajaran_akhir'] = tahun_ajaran_akhir

        return result
    
    # If not valid, print and return
    if settings.DEBUG:
        print('Tahun ajaran difference is too far. Tahun ajaran awal: {}, Tahun ajaran akhir: {}'.format(tahun_ajaran_awal, tahun_ajaran_akhir))

    return result


def request_data_to_neosia(auth_url: str, params: dict = {}, headers: dict = {}):
    headers['token'] = os.environ.get('NEOSIA_API_TOKEN')
    
    try:
        response = requests.post(auth_url, params=params, headers=headers)
    except requests.exceptions.SSLError:
        if settings.DEBUG: print("SSL Error")
        response = requests.post(auth_url, params=params, headers=headers, verify=False)
    except requests.exceptions.ConnectTimeout:
        # TODO: ACTIONS ON CONNECT TIMEOUT
        if settings.DEBUG:
            print('Timeout')
            return None

    if response.status_code == 200:
        json_response = response.json()
        
        if len(json_response) == 0: 
            if settings.DEBUG: print('JSON is empty. {}'.format(response.url))
            return None

        return json_response
    else:
        if settings.DEBUG: print(response.raw)
        return None

