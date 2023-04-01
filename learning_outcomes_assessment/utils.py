import json
import os
import uuid
import requests
from django.urls import reverse
from django.conf import settings
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.transports import Transport


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


def post_request(url: str, params: dict = {}, headers: dict = {}, verify: bool = True, timeout = None):
    """Post request to auth URL

    Args:
        auth_url (str): URL
        params (dict, optional): Request parameters. Defaults to {}.
        headers (dict, optional): Request headers. Defaults to {}.
        verify (bool, optional): Verify SSL Certificate. Defaults to True.
        timeout (float, optional): Request timeout. Defaults to None.

    Returns:
        Response | None: Returns response if success, else, returns None
    """

    try:
        response = requests.post(url, params=params, headers=headers, verify=verify, timeout=timeout)
    except requests.exceptions.SSLError:
        if settings.DEBUG: 
            print("SSL Error")
        response = post_request(url, params=params, headers=headers, verify=False)
    except requests.exceptions.MissingSchema:
        if settings.DEBUG:
            print('URL POST has not been set')
        raise
    except requests.exceptions.Timeout:
        if settings.DEBUG:
            print('Timeout')
        raise

    return response


def request_data_to_neosia(auth_url: str, params: dict = {}, headers: dict = {}):
    """Request data to neosia

    Args:
        auth_url (str): URL
        params (dict, optional): Request parameters. Defaults to {}.
        headers (dict, optional): Request headers. Defaults to {}.

    Returns:
        dict | None: Returns JSON Response if success, else, returns None
    """
    
    headers['token'] = os.environ.get('NEOSIA_API_TOKEN')
    
    response = post_request(auth_url, params=params, headers=headers)

    if response.status_code == 200:
        json_response = response.json()
        
        if len(json_response) == 0: 
            if settings.DEBUG: print('JSON is empty. {}'.format(response.url))
            return None

        return json_response
    else:
        if settings.DEBUG: print(response.raw)
        return None


def get_reverse_url(viewname: str, kwargs):
    """Get reverse URL

    Args:
        viewname (str): View name that registered in urls

    Returns:
        str: Reverse URL for viewname
    """
    
    return reverse(viewname, kwargs=kwargs)


def nilai_excel_upload_handler(instance, filename):
    _, extension = os.path.splitext(filename)
    new_filename = '{}{}'.format(uuid.uuid1(), extension)
    
    file_path = os.path.join(settings.MEDIA_ROOT, 'mk-semester', 'nilai', new_filename)
    return file_path 

def _iter_cols(self, min_col=None, max_col=None, min_row=None,
               max_row=None, values_only=False):
    """Iter cols for load workbook with read_only=True
    """
    yield from zip(*self.iter_rows(
        min_row=min_row, max_row=max_row,
        min_col=min_col, max_col=max_col, values_only=values_only))


def request_nusoap(search_text: str) -> dict:
    """Request dosen search by NuSoap

    Args:
        search_text (str): Search name

    Returns:
        dict: Formatted JSON Response
            json_response = {
                'results':[
                    {
                        'id': nip,
                        'text', nama_dosen
                    }
                ]
            }
    """
    
    session = Session()
    session.auth = HTTPBasicAuth(
        os.environ.get('NUSOAP_USERNAME', ''), 
        os.environ.get('NUSOAP_PASSWORD', '')
    )
    client = Client('http://apps.unhas.ac.id/nusoap/serviceApps.php?wsdl', transport=Transport(session=session))
    results = json.loads(client.service['getUser'](search_text))

    json_response = {'results': []}

    for result in results['data']:
        json_response['results'].append({
            'id': result['pegNip'],
            'text': result['pegNamaGelar'],
        })

    return json_response


def clone_object(obj, attrs={}):
    """
    Clone object utility from https://stackoverflow.com/a/61729857/11889798
    """
    
    # we start by building a "flat" clone
    clone = obj._meta.model.objects.get(pk=obj.pk)
    clone.pk = None

    # if caller specified some attributes to be overridden, 
    # use them
    for key, value in attrs.items():
        setattr(clone, key, value)
    
    # Remove lock object first
    if hasattr(clone, 'lock'):
        clone.lock = None
    
    # save the partial clone to have a valid ID assigned
    clone.save()

    # Scan field to further investigate relations
    fields = clone._meta.get_fields()
    for field in fields:

        # Manage M2M fields by replicating all related records 
        # found on parent "obj" into "clone"
        if not field.auto_created and field.many_to_many:
            for row in getattr(obj, field.name).all():
                getattr(clone, field.name).add(row)

        # Manage 1-N and 1-1 relations by cloning child objects
        if field.auto_created and field.is_relation:
            if field.many_to_many:
                # do nothing
                pass
            else:
                # provide "clone" object to replace "obj" 
                # on remote field
                attrs = {
                    field.remote_field.name: clone
                }
                children = field.related_model.objects.filter(**{field.remote_field.name: obj})
                for child in children:
                    clone_object(child, attrs)

    return clone
