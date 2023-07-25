import os
import json

from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkfunctiongraph.v2.region.functiongraph_region import FunctionGraphRegion
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkfunctiongraph.v2 import *


class HW:
    def __init__(self):
        ak = os.environ.get('ak')
        sk = os.environ.get('sk')
        credentials = BasicCredentials(ak, sk)
        self.client = FunctionGraphClient.new_builder() \
            .with_credentials(credentials) \
            .with_region(FunctionGraphRegion.value_of("cn-north-4")) \
            .build()

    def get_user_data(self):
        try:
            request = ShowFunctionConfigRequest()
            request.function_urn = "urn:fss:cn-north-4:05586f9fc00025fb2f37c01e91c8b6fe:function:default:sfc_automations:latest"
            response = self.client.show_function_config(request)
            user_data = json.loads(response.to_json_object()['user_data'])
            return user_data
        except exceptions.ClientRequestException as e:
            print(e.status_code)
            print(e.request_id)
            print(e.error_code)
            print(e.error_msg)

    def update_user_data(self, key, value):
        user_data = self.get_user_data()
        user_data[key] = value
        try:
            request = UpdateFunctionConfigRequest()
            request.function_urn = "urn:fss:cn-north-4:05586f9fc00025fb2f37c01e91c8b6fe:function:default:sfc_automations:latest"
            request.body = UpdateFunctionConfigRequestBody(
                user_data=json.dumps(user_data),
                memory_size=128,
                handler="index.handler",
                timeout=30,
                runtime="Python3.6",
                func_name="sfc_automations"
            )
            response = self.client.update_function_config(request)
        except exceptions.ClientRequestException as e:
            print(e.status_code)
            print(e.request_id)
            print(e.error_code)
            print(e.error_msg)
