# “Consuming BC SaaS OData 4.0 – Read and Print Data from Python”

# LOAD PYTHON MODULES

import os

from time import sleep
from requests.auth import HTTPBasicAuth
from datetime import date, timedelta, datetime
import calendar
from get_token import get_angora_token
import requests
import pandas as pd
BC_token = get_angora_token()



def basic_reporting_query():
    # SET query to Swyft Home Dynamics 365 Business Central location
    BCapi = "https://api.businesscentral.dynamics.com/v2.0/7b8264b4-3685-4886-ae48-15ef08b9f0ea/Production/ODataV4/Company('Angora%20Manufacturing%202022')/MTORFIDList"

    # GET DATA (BY REQUEST METHOD)
    r = requests.get(BCapi,

                     headers={
                         'OData-MaxVersion': '4.0',
                         'OData-Version': '4.0',
                         'Accept': 'application/json',
                         'Content-Type': 'application/json; charset=utf-8',
                         'Authorization': 'Bearer ' + BC_token
    }
    )
    if r.status_code != 200:
        raise Exception(f'Request failed with status code {r.status_code}')

    # get the response (Json object)
    getData = r.json()

    df = pd.json_normalize(getData['value'])
    try:
        next_page = getData['@odata.nextLink']
        # BC has a page limit; while there is a following page, append the JSON & follow link to the next page
        while next_page:
            r = requests.get(next_page,
                             headers={
                                 'OData-MaxVersion': '4.0',
                                 'OData-Version': '4.0',
                                 'Accept': 'application/json',
                                 'Content-Type': 'application/json; charset=utf-8',
                                 'Authorization': 'Bearer ' + BC_token
                             }
                             )
            getData = r.json()
            try:
                df = pd.concat([df, pd.json_normalize(getData['value'])])
                next_page = getData['@odata.nextLink']
            except:
                break


    except OSError as err:
        print("OS error: {0}".format(err))
    except ValueError:
        print("Could not convert data to an integer.")
    except BaseException as err:
        print(f"Unexpected {err=}, {type(err)=}")

    return df

