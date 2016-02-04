import time
import random
import shutil
import threading
import glob
import os
from sh import vboxmanage, grep, sed, cut, wc
from config import DEFAULT_BOX, BOX_SNAPSHOT, HOST_SHARED_PATH


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
                if device_id in vms and vm_status is not 0:
                    try:
                        print("Remove the unused vm -> " + device_id)
                        remove_vm_clone(vm)
                    except Exception as e:
                        print(e)
                        # TODO: Handle if could not delete
                elif device_id not in vms:
                    clone_and_start_vm(clone_name=device_id)
        elif vms:
            for vm in vms:
                if vm != DEFAULT_BOX:
                    print("Remove vm -> " + vm)
                    remove_vm_clone(vm)

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
        for uuid in result.split('\n'):
            devices.append(uuid)
    except Exception as e:
        print(e)
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


def get_new_port():
    return random.randrange(1000, 1500)


def get_number_of_vm():
    return int(wc(vboxmanage.list.vms(), "-l"))


def clone_vm(base_name, clone_name=None, clone_order=get_number_of_vm()):
    try:
        _remove_clone_folder(clone_name)
        vboxmanage.clonevm(base_name, '--snapshot', BOX_SNAPSHOT, '--name',
                           clone_name, '--options', 'link', '--mode', 'machine', '--register')
        port = 10000 + clone_order
        # TODO : Check for ios-webkit-debug-proxy port requirement
        portrule = 'portrule1,tcp,,%s,,4723' % str(port)
        vboxmanage.modifyvm(clone_name, '--natpf1', portrule)

        vboxmanage.sharedfolder.add(
            clone_name, "--name", "sharedfolder", "--hostpath", HOST_SHARED_PATH)
        filename = "%s/%s_%s" % (HOST_SHARED_PATH, clone_name, port)
        open(filename, 'w+')
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
        grep(grep(vboxmanage.showvminfo(vm_name), "-A", "2",
                  'Currently Attached USB Devices:'), 'UUID')
        return True
    except Exception as e:
        print(e)
        return False


def shutdown_vm(vm_name):
    try:
        vboxmanage.controlvm(vm_name, "poweroff")
        if get_vm_status(vm_name) is 9:
            return True
        else:
            return False
    except Exception as e:
        print(e)
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
    except Exception as e:
        print(e)
        status = -1
        return status


def remove_vm_clone(name):
    try:
        shutdown_vm(name)
        vboxmanage.unregistervm(name, '--delete')
        time.sleep(1)
        tmp_file = HOST_SHARED_PATH + "/" + name + "*"
        for fl in glob.glob(tmp_file):
            os.remove(fl)
        return True
    except Exception as e:
        print(e)
        return False


def _remove_clone_folder(clone_name):
    try:
        vbox_path = sed(grep(vboxmanage.list('systemproperties'), 'Default machine folder:'),
                        '-e s/Default machine folder://g').strip()
        clone_path = vbox_path + '/' + clone_name
        shutil.rmtree(clone_path)
        return True
    except OSError as e:
        print(e)
        return True
    except Exception as e:
        print(e)
        return False
