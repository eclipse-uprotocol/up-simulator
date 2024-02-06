import time

from simulator.tools import pull_and_compile_protos


def execute_pre_scripts():
    pull_and_compile_protos.execute()
    time.sleep(1)
    from simulator.tools import generate_resource_catalog
    generate_resource_catalog.execute()
    time.sleep(1)
    from simulator.tools import create_services_json_for_ui
    create_services_json_for_ui.execute()
    time.sleep(1)



if __name__ == "__main__":
    execute_pre_scripts()
