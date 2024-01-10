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

import git
from git import Repo

# Constants
REPO_URL = "https://github.com/COVESA/uservices.git"
REPO_DIR = "protos"
OUTPUT_DIR = "../protofiles"


def clone_or_pull(repo_url, repo_dir):
    try:
        Repo.clone_from(repo_url, repo_dir)
        print(f"Repository cloned successfully from {repo_url} to {repo_dir}")
    except git.exc.GitCommandError as clone_error:
        print(f"Error during cloning: {clone_error}")
        try:
            git_pull_command = ["git", "pull"]
            subprocess.run(git_pull_command, cwd=repo_dir, check=True)
            print("Git pull successful after clone failure.")
        except subprocess.CalledProcessError as pull_error:
            print(f"Error during Git pull: {pull_error}")


def generate_protobuf(repo_dir, output_dir):
    print(f"Generating protobuf files in {repo_dir} to {output_dir}")
    proto_files, root_dirs = find_proto_files(repo_dir)
    import_options_str = ' '.join(['-I {}'.format(root_dir + os.sep) for root_dir in root_dirs])
    import_options_list = import_options_str.split()
    protoc_command = ['protoc', *import_options_list, f'--python_out={output_dir}', *proto_files]

    try:
        subprocess.run(protoc_command)
    except subprocess.CalledProcessError as protoc_error:
        print(f"Error during protoc execution: {protoc_error}")


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
                shutil.copytree(src_directory, OUTPUT_DIR, dirs_exist_ok=True)
    except Exception as e:
        print(f"Error executing Maven command: {e}")


def find_proto_files(directory):
    proto_files = []
    root_dirs = set()
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".proto"):
                proto_files.append(os.path.join(root, file))
                root_dirs.add(root)
    return proto_files, root_dirs


def delete_protos_folder(repo_dir):
    print(f"Deleting entire protofiles folder: {repo_dir}")
    shutil.rmtree(repo_dir, ignore_errors=True)


if __name__ == "__main__":
    if os.path.exists(OUTPUT_DIR):
        print(f"Deleting existing protofiles in {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    clone_or_pull(REPO_URL, REPO_DIR)
    # Execute mvn compile-python
    maven_command = ['mvn', "protobuf:compile-python"]
    execute_maven_command(REPO_DIR, maven_command)
