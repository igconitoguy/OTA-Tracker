import json
import time
import logging
from utils.crypto import Crypto
from utils.data import Data

class Request:
    def __init__(
        self,
        req_version=1,
        model=None,
        ota_version=None,
        nv_identifier=None,
        rui_version=None,
        region=None,
        device_id=None,
        imei0=None,
        imei1=None,
        beta=False,
        language=None,
        resp_key=None,
    ):
        self.req_version = req_version
        self.model = model
        self.ota_version = ota_version
        self.nv_identifier = nv_identifier
        self.rui_version = rui_version
        self.region = region
        self.device_id = device_id
        self.imei0 = imei0
        self.imei1 = imei1
        self.beta = beta
        self.language = language
        self.resp_key = resp_key
        
        # Initialize properties dictionary
        self.properties = {
            "model": model,
            "productName": model,
            "nvCarrier": nv_identifier,
            "otaVersion": ota_version,
            "uRegion": region,
            "rui_version": rui_version,
            "region": region,
            "deviceId": device_id,
            "imei": imei0,
            "imei1": imei1,
        }
        
        # Add otaPrefix if otaVersion is available
        if ota_version:
            parts = ota_version.split('_')
            if len(parts) >= 2:
                ota_prefix = '_'.join(parts[:2])
                self.properties["otaPrefix"] = ota_prefix
                self.properties["romVersion"] = ota_prefix
        
        # Set deviceId with sha256 hash
        if device_id:
            self.properties["deviceId"] = Crypto.sha256(device_id)
        elif imei0:
            self.properties["deviceId"] = Crypto.sha256(imei0)
        else:
            self.properties["deviceId"] = Crypto.sha256(Data.default_headers["deviceId"])
        
        # Handle RUI version specific settings
        if rui_version == 1:
            self.properties["version"] = "2"
        
        # Set language
        if language:
            self.properties["language"] = language
        
        self.key = None
        self.body = None
        self.headers = {}
        self.url = ""

    def encrypt(self, buf):
        if self.properties["rui_version"] == 1:
            return (Crypto.encrypt_ecb(buf), None, None)
        elif self.req_version == 2:
            return Crypto.encrypt_ctr_v2(buf)
        else:
            return (Crypto.encrypt_ctr(buf), None, None)

    def decrypt(self, buf):
        if self.properties["rui_version"] == 1:
            return Crypto.decrypt_ecb(buf)
        elif self.req_version == 2:
            body_object = json.loads(buf)
            return Crypto.decrypt_ctr_v2(
                body_object["cipher"],
                self.key,
                body_object["iv"]
            )
        else:
            return Crypto.decrypt_ctr(buf)

    def set_vars(self):
        region = self.properties.get("region")
        rui_version = self.properties.get("rui_version")
        model = self.properties.get("model")
        
        # Set trackRegion
        self.properties["trackRegion"] = region
        
        # Set uRegion
        self.properties["uRegion"] = region
        
        # Set language for CN region
        if region == "CN" and not self.properties.get("language"):
            self.properties["language"] = "zh-CN"
            self.properties["deviceId"] = "0"
        
        # Set Android version based on RUI version
        if rui_version:
            android_version = 10 + rui_version - 1
            self.properties["androidVersion"] = f"Android{android_version}.0"
        
            # Set ColorOS version
            if rui_version == 1:
                self.properties["colorOSVersion"] = "ColorOS7"
            else:
                color_version = 11 + rui_version - 2
                self.properties["colorOSVersion"] = f"ColorOS{color_version}"
        
        # Set isRealme flag
        if model and "RMX" in model:
            self.properties["isRealme"] = "1"
        else:
            self.properties["isRealme"] = "0"
        
        # Set current timestamp
        self.properties["time"] = str(int(time.time() * 1000))
        
        # Set URL based on model and RUI version
        if model == "OnePlus":
            self.url = "https://otag.h2os.com/post/Query_Update"
        elif rui_version and rui_version >= 2 and self.req_version == 2:
            if region in Data.server_params:
                self.url = Data.server_params[region].server_url
            else:
                self.url = "https://default-server-url.com"
        else:
            rui_index = min(rui_version or 2, 2)
            if region in Data.urls.get(rui_index, {}):
                self.url = Data.urls[rui_index][region]
            else:
                self.url = "https://default-server-url.com"

    def set_body_headers(self):
        new_body = {}
        
        # Populate new_body from properties or default_body
        for key in Data.default_body:
            if key in self.properties and self.properties[key] is not None:
                new_body[key] = self.properties[key]
            else:
                new_body[key] = Data.default_body[key]
        
        # Handle beta mode
        if self.beta:
            new_body["mode"] = "1"
        
        # Populate headers
        for key in Data.default_headers:
            if key in self.properties and self.properties[key] is not None:
                self.headers[key] = str(self.properties[key])
            else:
                self.headers[key] = Data.default_headers[key]
        
        # Set response key based on RUI version
        self.resp_key = "resps" if self.rui_version == 1 else "body"
        
        # Handle request versioning and encryption
        if self.req_version == 2:
            logging.debug(f"Request body: {new_body}")
            self.headers["version"] = "2"
            
            # Encrypt the body
            cipher, new_key, iv = self.encrypt(json.dumps(new_body))
            self.key = new_key
            
            # Create the JSON body
            params = {
                "cipher": cipher,
                "iv": iv
            }
            self.body = json.dumps({"params": json.dumps(params)})
            
            # Generate protected key
            if new_key and self.region in Data.server_params:
                protected_key = Crypto.generate_protected_key(
                    new_key, 
                    Data.server_params[self.region].pub_key
                )
                
                # Create the protected key header
                version = str(int(time.time() * 1000))
                protected_key_obj = {
                    "SCENE_1": {
                        "protectedKey": protected_key,
                        "version": version,
                        "negotiationVersion": Data.server_params[self.region].negotiation_version
                    }
                }
                self.headers["protectedKey"] = json.dumps(protected_key_obj)
        else:
            logging.debug(f"Request body: {new_body}")
            cipher = self.encrypt(json.dumps(new_body))[0]
            
            # Create the JSON body
            params = {
                "cipher": cipher,
                "iv": "2bG0KwLBIkPynC8mOdgVKA=="
            }
            self.body = json.dumps({"params": json.dumps(params)})
        
        return self.body, self.headers, new_body

    def validate_content(self, content):
        if "checkFailReason" in content and content["checkFailReason"] is not None:
            raise RuntimeError(f"Response contents mismatch, expected 'resps' got '{content['checkFailReason']}'!")

    def validate_response(self, response_code, response_body):
        # Check if status code is not 200
        if response_code != 200:
            raise RuntimeError(f"Response status mismatch, expected '200' got '{response_code}'!")
        
        print("Status Valid")
        
        # Parse the response body as JSON
        json_response = json.loads(response_body)
        
        # Check if 'responseCode' is present and not equal to 200
        if "responseCode" in json_response and json_response["responseCode"] != 200:
            err_msg = json_response.get("errMsg", "No error message provided")
            raise RuntimeError(f"Response status mismatch, expected '200' got '{json_response['responseCode']}' ({err_msg})!")

    def parse_log(self, log):
        # Use a regular expression to extract the JSON part
        import re
        regex = r"\{.*\}"
        match = re.search(regex, log)
        if not match:
            return -1
        
        json_string = match.group(0)
        json_object = json.loads(json_string)
        body = json_object["body"]
        response_code = json_object["responseCode"]
        return response_code