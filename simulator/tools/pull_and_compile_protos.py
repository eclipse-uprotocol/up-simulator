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

import os
import re
import shutil
import subprocess

import git
from git import Repo

from simulator.utils.constant import PROTO_OUTPUT_DIR, REPO_URL, PROTO_REPO_DIR


def clone_or_pull(repo_url, PROTO_REPO_DIR):
    try:
        Repo.clone_from(repo_url, PROTO_REPO_DIR)
        print(f"Repository cloned successfully from {repo_url} to {PROTO_REPO_DIR}")
    except git.exc.GitCommandError as clone_error:
        print(f"Error during cloning: {clone_error}")
        try:
            git_pull_command = ["git", "pull"]
            subprocess.run(git_pull_command, cwd=PROTO_REPO_DIR, check=True)
            print("Git pull successful after clone failure.")
        except subprocess.CalledProcessError as pull_error:
            print(f"Error during Git pull: {pull_error}")


def execute_maven_command(project_dir, command):
    try:
        with subprocess.Popen(command, cwd=os.path.join(os.getcwd(), project_dir), shell=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, text=True) as process:
            stdout, stderr = process.communicate()
            print(stdout)

            if process.returncode != 0:
                print(f"Error: {stderr}")
            else:
                print("Maven command executed successfully.")
                src_directory = os.path.join(os.getcwd(), project_dir, "target", "generated-sources", "protobuf",
                                             "python")

                shutil.copytree(src_directory, PROTO_OUTPUT_DIR, dirs_exist_ok=True)
                process_python_protofiles(PROTO_OUTPUT_DIR)
    except Exception as e:
        print(f"Error executing Maven command: {e}")


def replace_in_file(file_path, search_pattern, replace_pattern):
    with open(file_path, 'r') as file:
        file_content = file.read()

    updated_content = re.sub(search_pattern, replace_pattern, file_content)

    with open(file_path, 'w') as file:
        file.write(updated_content)


def process_python_protofiles(directory):
    for root, dirs, files in os.walk(directory):
        create_init_py(root)
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                replace_in_file(file_path, r'from vehicle', 'from target.protofiles.vehicle')
                replace_in_file(file_path, r'from example', 'from target.protofiles.example')
                replace_in_file(file_path, r'from common', 'from target.protofiles.common')
                replace_in_file(file_path, r'import uservices_options_pb2', 'import target.protofiles.uservices_options_pb2')
                replace_in_file(file_path, r'import units_pb2', 'import target.protofiles.units_pb2')
                replace_in_file(file_path, r'import uprotocol_options_pb2', 'import target.protofiles.uprotocol_options_pb2')


def create_init_py(directory):
    init_file_path = os.path.join(directory, "__init__.py")

    # Check if the file already exists
    if not os.path.exists(init_file_path):
        # Create an empty __init__.py file
        with open(init_file_path, "w"):
            pass
        print(f"Added __init__.py file to {directory}")


if __name__ == "__main__":
    # if os.path.exists(PROTO_OUTPUT_DIR):
    #     print(f"Deleting existing protofiles in {PROTO_OUTPUT_DIR}")
    #     shutil.rmtree(PROTO_OUTPUT_DIR)
    # os.makedirs(PROTO_OUTPUT_DIR)

    clone_or_pull(REPO_URL, PROTO_REPO_DIR)
    shutil.copy('uprotocol_options.proto', os.path.join(PROTO_REPO_DIR, 'src', 'main', 'proto'))

    # Execute mvn compile-python
    maven_command = ['mvn', "protobuf:compile-python"]
    execute_maven_command(PROTO_REPO_DIR, maven_command)
