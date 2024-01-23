import re

from jinja2 import Template

copyright_value = """
# -------------------------------------------------------------------------
#
# Copyright (c) 2023 General Motors GTO LLC
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# SPDX-FileType: SOURCE
# SPDX-FileCopyrightText: 2023 General Motors GTO LLC
# SPDX-License-Identifier: Apache-2.0
#
# -------------------------------------------------------------------------
"""


def extract_service_class_name(proto_file_content):
    service_name = None
    service_pattern = r'service\s+([\w]+)\s*{'
    # Extract service name
    service_match = re.search(service_pattern, proto_file_content)
    if service_match:
        service_name = service_match.group(1)
        print("Service Name:", service_name)
    return service_name + "Service"


def extract_package(proto_file_content):
    package_name = None
    package_pattern = r'package\s+([\w.]+);'
    # Extract package name
    package_match = re.search(package_pattern, proto_file_content)
    if package_match:
        package_name = package_match.group(1)
        print("Package Name:", package_name)
    return package_name


def extract_entity(proto_file_content):
    entity_name = re.search(r'option\s+\(uprotocol\.name\)\s*=\s*"([^"]+)"', proto_file_content)
    return entity_name.group(1) if entity_name else None



def extract_import_stat(proto_file_content):
    imports_stat = []
    import_pattern = r'import\s+"([^"]+\.proto)"'
    imports_match = re.findall(import_pattern, proto_file_content)

    for imp in imports_match:
        imports_stat.append(imp)
        print(imp)

    return imports_stat


def extract_rpcs(proto_file_content):
    rpcs = []
    inputtype_currentproto = []

    rpc_pattern = r'rpc\s+(\w+)\s*\(([^)]+)\)\s*returns\s*\(([^)]+)\)'

    # Extract RPCs, including their names, input types, and return types
    rpc_matches = re.finditer(rpc_pattern, proto_file_content)
    for rpc_match in rpc_matches:
        rpc_name = rpc_match.group(1)
        input_type = rpc_match.group(2)
        return_type = rpc_match.group(3)
        rpcs.append({
            'rpc': rpc_name,
            'input_type': input_type,
            'output_type': return_type
        })
        # Regex pattern to search for the message
        pattern_inputtype_in_proto = r'message\s' + input_type + '\s*{'

        # Search for the pattern in the input string
        matches = re.findall(pattern_inputtype_in_proto, proto_file_content)
        if matches:
            inputtype_currentproto.append(input_type)
        else:
            # search in other files, to do
            pass

    return (rpcs, inputtype_currentproto)


def generate_code(protodata, filename):
    rpc_inp_out = {}
    # rpc_outputs = []
    rpc_names = []

    rpcs, inputtype_currentproto = extract_rpcs(protodata)
    for rpc in rpcs:
        # rpc_inputs.append(rpc["input_type"])
        rpc_names.append(rpc["rpc"])
        # rpc_outputs.append(rpc["output_type"])
        rpc_inp_out[rpc["input_type"]] = rpc["output_type"]
    class_name = extract_service_class_name(protodata)
    generated_code = copyright_value + template_imports(inputtype_currentproto, protodata,
                                                        filename) + template_class_code(protodata,class_name) + template_rpc_code(
        rpc_names) + template_handlereq_code(rpc_inp_out, rpc_names) + template_main_code(protodata)

    return generated_code, class_name


def template_imports(inputtype_currentproto, protodata, filename):
    template_str_imports = """

from simulator.core.abstract_service import CovesaService
from simulator.core.exceptions import ValidationError
{%if inputtype_currentproto|length >0 %}
from target.protofiles.{{package}}.{{filename}} import ({% for inputtype in inputtype_currentproto %}
    {{inputtype}},{% endfor %}
){% endif %}
     """
    template = create_template(template_str_imports)
    return template.render(inputtype_currentproto=inputtype_currentproto, package=extract_package(protodata),
                           filename=filename + "_pb2")


def template_class_code(protodata,class_name):
    template_str = '''

class {{class_name}}(CovesaService):

    def __init__(self, portal_callback=None):
        """
        {{class_name}} constructor
        """
        super().__init__('{{entity_name}}', portal_callback)
        self.init_state()

    def init_state(self):
        """
        Initializes internal data structures for keeping track of the current state of the {{class_name}}
        """
        self.state = {}
     '''
    template = create_template(template_str)
    return template.render(class_name=class_name,
                           entity_name=extract_entity(protodata))


def template_rpc_code(rpc_names):
    template_Str = """
    # RPC Request Listeners for each RPC method{% for rpc in rpc_names %}
    @CovesaService.RequestListener
    def {{ rpc }}(self, request, response):
        return self.handle_request(request, response)
    {% endfor %}
    """
    template = create_template(template_Str)
    return template.render(rpc_names=rpc_names)


def enumerate_dict(dict_obj):
    return [{'index': idx, 'key': key, 'value': value} for idx, (key, value) in enumerate(dict_obj.items())]


def template_handlereq_code(rpc_inp_out, rpc_names):
    template_str = """def handle_request(self, request, response):        
        {% for rpc in rpc_inp_out %}
        # handle {{rpc_names[rpc['index']]}} request       
        if type(request) == {{rpc['input']}}:
           # todo return {{rpc['output']}} response, Implement your logic here
           pass
        {% endfor %}
        return response
    """
    template = create_template(template_str)
    processed_data = [{'index': idx, 'input': key, 'output': value} for idx, (key, value) in
                      enumerate(rpc_inp_out.items())]

    return template.render(rpc_inp_out=processed_data, rpc_names=rpc_names)


def template_main_code(protodata):
    template_str = """
if __name__ == "__main__":
    service = {{class_name}}()
    service.start()
    
    """
    template = create_template(template_str)
    return template.render(class_name=extract_service_class_name(protodata))


def create_template(template_str):
    # Create a Jinja2 template object
    return Template(template_str)

