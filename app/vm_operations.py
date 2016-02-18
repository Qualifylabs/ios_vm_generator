import time
import shutil
import threading
import os
from sh import vboxmanage, grep, sed, cut
from config import DEFAULT_BOX, BOX_SNAPSHOT


#####################
## Device Listener ##
#####################


def device_status_daemon():
    def procedure():
        t = threading.Timer(5.0, procedure)
        t.start()
        devices = get_list_usb_devices()
        vms = get_vm_list()
        if devices:
            for device_id in devices:
                vm_status = get_vm_status(device_id)
                if device_id in vms and vm_status > 2:
                    try:
                        print("Start vm -> " + device_id)
                        start_vm(device_id)
                        print("Device is up and running -> " + device_id)
                    except Exception as e:
                        print(e)
                elif device_id not in vms:
                    clone_and_start_vm(clone_name=device_id)
                    print("New vm created and started -> " + device_id)
        running_vms = get_running_vm_list()
        for vm in running_vms:
            device_status = not vm in devices
            if vm != DEFAULT_BOX and len(vm) is 40 and get_vm_status(vm) is not 9 and device_status:
                print("Shutdown vm -> " + vm)
                shutdown_vm(vm)

    t = threading.Timer(5.0, procedure)
    t.start()


#######################
## Device Operations ##
#######################


def get_list_usb_devices():
    try:
        result = sed(sed(grep(vboxmanage.list.usbhost(), "SerialNumber"),
                         "-e s/SerialNumber://g"), "-e s/\ //g").strip()
        devices = []
        for udid in result.split('\n'):
            if len(udid) is 40:
                devices.append(udid)
    except:
        return None
    else:
        return devices


def add_usb_filter(udid):
    try:
        vboxmanage.usbfilter.add(
            "0", "--target", udid, "--name", "iOS_Device", "--serialnumber", udid)
    except Exception as e:
        print(e)
        return False
    return True


################################
## Virtual Machine Operations ##
################################


def get_vm_list():
    # TODO: Handle empty space name vms.
    try:
        vms = sed(sed(vboxmanage.list.vms(), '-e s/ .*$//'), 's/"//g').strip()
        vm_list = []
        for vm in vms.split('\n'):
            vm_list.append(str(vm))
        return vm_list
    except Exception as e:
        print(e)
        return []


def get_running_vm_list():
    # TODO: Handle empty space name vms.
    try:
        vms = sed(sed(vboxmanage.list.runningvms(),
                      '-e s/ .*$//'), 's/"//g').strip()
        vm_list = []
        for vm in vms.split('\n'):
            vm_list.append(str(vm))
        return vm_list
    except Exception as e:
        print(e)
        return []


def start_vm(vm_name):
    try:
        vboxmanage.startvm(vm_name, "--type", "headless")
        if get_vm_status(vm_name) is 0:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        remove_vm_clone(vm_name)
        return False


def clone_vm(base_name, clone_name=None):
    try:
        _remove_clone_folder(clone_name)
        vboxmanage.clonevm(base_name, '--snapshot', BOX_SNAPSHOT, '--name',
                           clone_name, '--options', 'link', '--mode', 'machine', '--register')
        return True
    except Exception as e:
        print(e)
        raise


def clone_and_start_vm(base_name=DEFAULT_BOX, clone_name=None):
    try:
        clone_vm(base_name, clone_name)
        add_usb_filter(clone_name)
        start_vm(clone_name)
        return clone_name
    except Exception as e:
        print(e)
        remove_vm_clone(clone_name)
        return None


def is_vm_occupied(vm_name):
    try:
        grep(grep(vboxmanage.showvminfo(vm_name), "-A", "8",
                  'Currently Attached USB Devices:'), 'SerialNumber')
        return True
    except Exception as e:
        return False


def shutdown_vm(vm_name):
    try:
        vboxmanage.controlvm(vm_name, "poweroff")
        if get_vm_status(vm_name) is 9:
            return True
        else:
            return False
    except:
        return False


def get_vm_status(vm_name):
    try:
        state = cut(sed(sed(grep(vboxmanage.showvminfo(
            vm_name), "State"), "-e s/State://g"), "-e s/\ //g"), "-d", "(", "-f1").strip()
        if state == 'running':  # status = 0
            if is_vm_occupied(vm_name):
                status = 1
            else:
                status = 0
        elif state == 'stopping':
            status = 8  # Error State
        elif state == 'saved':
            status = 2
        else:  # poweredoff or aborted
            status = 9
        return status
    except:
        status = -1
        return status


def remove_vm_clone(name):
    try:
        shutdown_vm(name)
        vboxmanage.unregistervm(name, '--delete')
        time.sleep(1)
        return True
    except Exception as e:
        return False


def _remove_clone_folder(clone_name):
    try:
        vbox_path = sed(grep(vboxmanage.list('systemproperties'), 'Default machine folder:'),
                        '-e s/Default machine folder://g').strip()
        clone_path = vbox_path + '/' + clone_name
        shutil.rmtree(clone_path)
        return True
    except OSError as e:
        return True
    except Exception as e:
        return False
