######################################################################
# Copyright 2016, 2021 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Promotion Steps

Steps file for Promotion.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from behave import given
from compare import expect


@given('the following promotions')
def step_impl(context):
    """ Delete all Promotions and load new ones """
    # List all of the promotions and delete them one by one
    rest_endpoint = f"{context.BASE_URL}/api/promotions"
    context.resp = requests.get(rest_endpoint)
    expect(context.resp.status_code).to_equal(200)
    for promotion in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{promotion['id']}",
                                       headers={'X-Api-Key': "133b94898f9b6c07ede6296e0ec197f7"})
        expect(context.resp.status_code).to_equal(204)

    # load the database with new promotions
    for row in context.table:
        payload = {
            "name": row['name'],
            "category": row['category'],
            "available": row['available'] in ['True', 'true', '1'],
            "promotype": row['promotype']
        }
        context.resp = requests.post(rest_endpoint, json=payload, headers={'X-Api-Key': "133b94898f9b6c07ede6296e0ec197f7"})
        expect(context.resp.status_code).to_equal(201)
