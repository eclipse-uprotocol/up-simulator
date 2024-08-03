"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import os
import re
import shutil
import subprocess

import git
from git import Repo

from tdk.utils.constant import (
    PROTO_OUTPUT_DIR,
    PROTO_REPO_DIR,
    REPO_URL,
    TAG_NAME,
)


def clone_or_pull(repo_url, proto_repo_dir):
    try:
        repo = Repo.clone_from(repo_url, proto_repo_dir)
        print(f"Repository cloned successfully from {repo_url} to {proto_repo_dir}")
        # Checkout the specific tag
        repo.git.checkout(TAG_NAME)
    except git.exc.GitCommandError:
        try:
            git_pull_command = ["git", "pull", "origin", TAG_NAME]
            subprocess.run(git_pull_command, cwd=proto_repo_dir, check=True)
            print("Git pull successful after clone failure.")
        except subprocess.CalledProcessError as pull_error:
            print(f"Error during Git pull: {pull_error}")


def execute_maven_command(project_dir, command):
    try:
        with subprocess.Popen(
            command,
            cwd=os.path.join(os.getcwd(), project_dir),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ) as process:
            stdout, stderr = process.communicate()
            print(stdout)

            if process.returncode != 0:
                print(f"Error: {stderr}")
            else:
                print("Maven command executed successfully.")
                src_directory = os.path.join(
                    os.getcwd(),
                    project_dir,
                    "target",
                    "generated-sources",
                    "protobuf",
                    "python",
                )

                shutil.copytree(src_directory, PROTO_OUTPUT_DIR, dirs_exist_ok=True)
                process_python_protofiles(PROTO_OUTPUT_DIR)
    except Exception as e:
        print(f"Error executing Maven command: {e}")


def replace_in_file(file_path, search_pattern, replace_pattern):
    with open(file_path, "r") as file:
        file_content = file.read()

    updated_content = re.sub(search_pattern, replace_pattern, file_content)

    with open(file_path, "w") as file:
        file.write(updated_content)


def process_python_protofiles(directory):
    for root, dirs, files in os.walk(directory):
        create_init_py(root)
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                replace_in_file(
                    file_path,
                    r"from vehicle",
                    "from tdk.target.protofiles.vehicle",
                )
                replace_in_file(
                    file_path,
                    r"from example",
                    "from tdk.target.protofiles.example",
                )
                replace_in_file(
                    file_path,
                    r"from common",
                    "from tdk.target.protofiles.common",
                )
                replace_in_file(
                    file_path,
                    r"import uservices_options_pb2",
                    "import tdk.target.protofiles.uservices_options_pb2",
                )
                replace_in_file(
                    file_path,
                    r"import units_pb2",
                    "import tdk.target.protofiles.units_pb2",
                )
                replace_in_file(
                    file_path,
                    r"import uprotocol_options_pb2",
                    "import uprotocol.proto.uprotocol_options_pb2",
                )


def create_init_py(directory):
    init_file_path = os.path.join(directory, "__init__.py")

    # Check if the file already exists
    if not os.path.exists(init_file_path):
        # Create an empty __init__.py file
        with open(init_file_path, "w"):
            pass


def execute():
    clone_or_pull(REPO_URL, PROTO_REPO_DIR)

    # Execute mvn compile-python
    maven_command = "mvn protobuf:compile-python"
    execute_maven_command(PROTO_REPO_DIR, maven_command)


if __name__ == "__main__":
    execute()
