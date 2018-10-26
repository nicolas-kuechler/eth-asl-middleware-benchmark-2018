import os, json, logging
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
import middleware_vm, server_vm, client_vm
from configs import config

log = logging.getLogger('asl')

def start(n_client, n_middleware, n_server):
    """Starts and initializes the specified number of vm's
    (if they are already running, they are left unchanged)
    """
    log.info(f"Requesting {n_client} clients, {n_middleware} middlewares and {n_server} servers")

    # create the list of vm names (e.g. ['Client1', 'Server1', 'Server2'])
    client_names = [f"Client{i+1}" for i in range(n_client)]
    middleware_names = [f"Middleware{i+1}" for i in range(n_middleware)]
    server_names = [f"Server{i+1}" for i in range(n_server)]
    vm_names = client_names + middleware_names + server_names

    # start the vm's if they are not already running
    started_vm_names = _start(vm_names=vm_names)

    # initialize all newly started vm's (e.g. pull from git)
    for started_vm_name in started_vm_names:
        id, c = _vm_config_by_name(vm_name)
        host = c['host']
        if started_vm_name.startswith("Client"):
            client_vm.init(client_id=id, host=host)
        elif started_vm_name.startswith("Middleware"):
            middleware_vm.init(mw_id=id, host=host)
        elif started_vm_name.startswith("Server"):
            server_vm.init(server_id=id, host=host)

def list_vm_status(compute_client=None):
    """List all VM's in group asl
        with their current status
    """

    if compute_client is None:
        compute_client = _get_compute_client()

    for vm in compute_client.virtual_machines.list("asl"):
        vm_status = get_power_state("asl", vm.name)
        log.info(f"{vm.name}: \t{vm_status}")


def _start(vm_names, compute_client=None):
    """Start the vm's given in vm_names
        if they are not already running
    """

    if compute_client is None:
        compute_client = _get_compute_client()

    async_vm_starts = []
    started_vm_names = []

    for vm_name in vm_names:
        vm_status = get_power_state("asl", vm_name)

        if vm_status == 'PowerState/deallocated': # only start the deallocated vm's
            log.info(f"Starting {vm_name}...")
            async_vm_start = compute_client.virtual_machines.start("asl", vm_name)
            started_vm_names.append(vm_name)
            async_vm_starts.append(async_vm_start)
        else:
            log.debug(f"Not starting {vm_name} becauce it is currently in {vm_status}")

    for vm_name, async_vm_start in zip(started_vm_names, async_vm_starts):
        async_vm_start.wait()
        log.info(f"Finished Starting {vm_name}")

    return started_vm_names

def deallocate_all(compute_client=None):
    """Deallocating all vm's in resource group asl
    """

    if compute_client is None:
        compute_client = _get_compute_client()

    async_vm_stops = []
    vm_names = []
    log.info("Deallocating all VM's...")

    for vm in compute_client.virtual_machines.list("asl"):
        async_vm_stop = compute_client.virtual_machines.deallocate("asl", vm.name)
        async_vm_stops.append(async_vm_stop)
        vm_names.append(vm.name)
        log.info(f"  Deallocating {vm.name}...")

    for vm_name, async_vm_stop in zip(vm_names, async_vm_stops):
        async_vm_stop.wait()
        log.info(f"  Finished Deallocating {vm_name}")

    log.info("Finished Deallocating all VM's")

def _get_compute_client():
    """Get a computing client to connect to azure
    """
    with open(config.AZURE_CREDENTIALS_FILE) as f:
        cred = json.load(f)

    subscription_id = cred['subscription_id']
    credentials = ServicePrincipalCredentials(
        client_id=cred['application_id'],
        secret=cred['key'],
        tenant=cred['tenant']
    )

    compute_client = ComputeManagementClient(credentials, subscription_id)

    return compute_client

def _vm_config_by_name(vm_name):
    """Given the name of the vm (e.g. Client1)
    returns the index and the config
    """

    if vm_name.startswith("Client"):
        lst = config.VM_CLIENT
    elif vm_name.startswith("Middleware"):
        lst =  config.VM_MIDDLEWARE
    elif vm_name.startswith("Server"):
        lst =  config.VM_SERVER
    else:
        raise ValueError(f"Cannot find config by name, unknown vm_name: {vm_name}")

    for id, c in enumerate(lst):
        if c['name'] == vm_name:
            return id, c

    raise ValueError(f"Cannot find config by name: {vm_name}")
