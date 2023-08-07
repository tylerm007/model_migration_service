
from sqlalchemy import create_engine, inspect, MetaData
import requests
from dotmap import DotMap
import json
import models

host = "localhost"
port = "5656"
api = "api"

def login(user:str = 'sam'):
    post_uri = f'http://{host}:{port}/api/auth/login'
    post_data = {"username": user, "password": "password"}
    r = requests.post(url=post_uri, json = post_data)
    response_text = r.text
    status_code = r.status_code
    if status_code > 300:
        raise requests.HTTPError(f'POST login failed with {r.text}')
    result_data = json.loads(response_text)
    result_map = DotMap(result_data)
    token = result_map.access_token

        # https://stackoverflow.com/questions/19069701/python-requests-library-how-to-pass-authorization-header-with-single-token
    return {'Authorization': f'Bearer {token}'}
    
def getData(table_name):
    get_uri = f'http://{host}:{port}/{api}/{table_name}?page%5Boffset%5D=0&page%5Blimit%5D=1"' #0&filter%5BId%5D=10248
    try:
        r = requests.get(url=get_uri, headers= login())
        return json.loads(r.text)
    except Exception as ex:
        return {}
    
def genPayload(table_name: str):
    data = getData(table_name)
    key = data["data"][0]["id"] if "data" in data and len(data["data"]) > 0 else 0
    print('\t "data": {')
    if key == 0:
        print('\t\t"attributes": {')
        print('\t\t"field1": "value1"')
        print('\t\t},')
    else:
        print('\t\t"attributes":')
        print(f'\t\t{data["data"][0]["attributes"]},')
   
    print(f'\t\t"type": "{table_name}",')
    print(f'\t\t"id": {key}')
    print('\t}}')
    return key

def print_meta(meta):
    #print("\n\nmeta.sorted_tables (meta = models.metadata.sorted_tables)\n")
    tableList = getData("listOfClasses")
    for each_table in tableList:
        print(f'\n{each_table.key}')
        for each_column in each_table.columns:
            print(f'\t{each_column.name}')

def print_steps(table_name:str, method_name:str):
        """
        
        @given('Sample Database')
        def step_impl(context):
            assert True

        @when('Transactions are submitted')
        def step_impl(context):
            assert True is not False

        @then('Enforce business policies with Logic (rules + code)')
        def step_impl(context):
            scenario = "Transaction Processing"
            test_utils.prt(f'Rules Report', scenario)
            assert True
        """
        print("")
        print(f"@given('{method_name} {table_name} endpoint')")
        print("def step_impl(context):")
        print("\tassert True")
        
        print("")
        if method_name == 'GET':
            print(f"@when('{method_name} {table_name} API')")
            print("def step_impl(context):")
            print(f"\tcontext.response_text = getAPI('{table_name}')")
        elif method_name == 'PATCH':
            print(f"@when('{method_name} {table_name} submitted')")
            print("def step_impl(context):")
            print("\tpayload = {")
            key = genPayload(table_name)
            print(f"\tcontext.response_text = patchAPI('{table_name}', payload, {key})")
        
        print("")
        if method_name == 'GET':
            print(f"@then('{table_name} retrieved')")
            print("def step_impl(context):")
            print('\tresponse_text = context.response_text')
            print("\tassert len(response_text.data) > 0")
        else: 
            print(f"@then('Enforce {table_name} business Logic')")
            print("def step_impl(context):")
            print('\tresponse_text = context.response_text')
            print("\tassert 'errors' not in response_text, f'Error - in response:{response_text}'")
    
def print_scenario(table_name:str, method_name:str):
    print(f"  Scenario: {method_name} {table_name} Endpoint")
    print(f"    Given {method_name} {table_name} endpoint")
    if method_name not in {'GET'}:
        print(f"    When {method_name} {table_name} submitted")
        print(f"    Then Enforce {table_name} business Logic")
    else:
        print(f"    When GET {table_name} API")
        print(f"    Then {table_name} retrieved")
    print("")


def gen_api_feature(method_name:str):
    """create feature and py file for behave testing

    Feature: API Testing

        Scenario: {table_name} Endpoint 
        Given {table_name}
        When Transactions are submitted
        Then Enforce business policies with Logic (rules + code)
    """
    print("#this is the api_test.feature")
    print("Feature: API GET Testing")
    print("")
    table_list =getData("listOfClasses")
    for tbl in table_list:
        print_scenario(tbl, method_name)
        

def gen_behave_steps(method_name:str):
    table_list = getData("listOfClasses")
    print_import()
    for tbl in table_list:
        print_steps(tbl, method_name)
        
def print_import():
    print("# this is the api_test.py")
    print("from behave import *")
    print("import requests, pdb")
    print("import json")
    print("from dotmap import DotMap")
    print("")
    print('host = "localhost"')
    print('port = "5656"')
    print("")
    print("def getAPI(table_name:str):")
    print("\tget_uri = f'http://{host}:{port}/api/{table_name}/?'\\")
    print('\t"page%5Boffset%5D=0&page%5Blimit%5D=1"') #0&filter%5BId%5D=10248
    print("\tr = requests.get(url=get_uri, headers= login())")
    print("\tresult_data = json.loads(r.text)")
    print("\treturn DotMap(result_data)")
    print("")
    print("def patchAPI(table_name:str, payload:dict, key:any):")
    print("\tget_uri = f'http://{host}:{port}/api/{table_name}/{key}'")
    print("\tr = requests.patch(url=get_uri, json=payload, headers= login())")
    print("\treturn json.loads(r.text)")
    print("")

def main():
    
    #gen_api_feature("GET")
    #gen_behave_steps("GET")
    
    gen_api_feature("PATCH")
    gen_behave_steps("PATCH")


if __name__ == "__main__":
    main()