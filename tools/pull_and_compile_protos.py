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
import shutil
import subprocess

from git import Repo


def clone_or_pull(repo_url, repo_dir):
    try:
        Repo.clone_from(repo_url, repo_dir)
        print(f"Repository cloned successfully from {repo_url} to {repo_dir}")
    except Exception as clone_error:
        print(clone_error.__getattribute__('stderr'))
        # If the clone fails, attempt a Git pull
        try:
            git_pull_command = ["git", "pull"]
            subprocess.run(git_pull_command, cwd=repo_dir, check=True)
            print("Git pull successful after clone failure.")
        except subprocess.CalledProcessError as pull_error:
            print(f"Error during Git pull: {pull_error}")


def generate_protobuf(repo_dir, output_dir):
    print(f"Generating protobuf files in {repo_dir} to {output_dir}")
    # Get a list of all .proto files in the directory and its subdirectories
    proto_files, root_dirs = find_proto_files(repo_dir)
    import_options_str = ' '.join(['-I {}'.format(root_dir + os.sep) for root_dir in root_dirs])
    import_options_list = import_options_str.split()

    # Construct the protoc command as a list of strings
    protoc_command = [
        'protoc',
        *import_options_list,
        f'--python_out={output_dir}',
        *proto_files
    ]

    # Run protoc command to generate Python files for all .proto files
    subprocess.run(protoc_command)


def find_proto_files(directory):
    # Get a list of all .proto files in the directory and its subdirectories
    proto_files = []
    root_dirs = set()
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".proto"):
                proto_files.append(os.path.join(root, file))
                root_dirs.add(root)
    return proto_files, root_dirs


def delete_protos_folder(repo_dir):
    print(f"Deleting entire protos folder: {repo_dir}")
    shutil.rmtree(repo_dir, ignore_errors=True)


if __name__ == "__main__":
    # GitHub repository information
    repo_url = "https://github.com/COVESA/uservices.git"
    repo_dir = "protos"

    # Output directory for protobuf files
    output_dir = "../protos"
    if os.path.exists(output_dir):
        print(f"Deleting existing protofiles in {output_dir}")
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    # Clone repository
    clone_or_pull(repo_url, repo_dir)
    # Generate protobuf files
    generate_protobuf(repo_dir, output_dir)
