PTP role
========

This role facilitates configuring Precision Time Protocol (PTP) attributes. It supports setting up the general configuration and the definition of master and client interfaces. This role is abstracted for Dell EMC PowerSwitch platforms running Dell EMC SmartFabric OS10.

Limitation: Currently only basic configuration parameters on the interface level are implemented. But the role is fully usable especially for G8275.1 profile.

The PTP role requires an SSH connection for connectivity to a Dell EMC SmartFabric OS10 device. You can use any of the built-in OS connection variables.

Role variables
--------------

- Role is abstracted using the `ansible_network_os` variable that can take `dellemc.os10.os10` as the value
- If `os10_cfg_generate` is set to true, the variable generates the role configuration commands in a file
- Any role variable with a corresponding state variable set to absent negates the configuration of that variable
- For variables with no state variable, setting an empty value for the variable negates the corresponding configuration
- `os10_ptp` (dictionary) holds the information about the clock definition as well as the interface configuration.
- Variables and values are case-sensitive

**os10_ptp**

| Key        | Type                      | Notes                                                   | Support               |
|------------|---------------------------|---------------------------------------------------------|-----------------------|
| ``clock`` | string | Type of the clock. Either 'boundary' or 'end-to-end-transparent'   | os10 |
| ``domain`` | integer | Domain ID | os10 |
| ``local_priority`` | integer | Local priority for g8275.[12] profiles [default: 128] | os10 |
| ``priority1`` | integer | priority1 attribute [default: 128] | os10 |
| ``priority2`` | integer | priority2 attribute [default: 128] | os10 |
| ``system_time`` | bool | Use PTP time to set local system time [true, false] | os10 |

**boundary**

This dictionary must be defined in the case if clock is set to 'boundary'.

| Key        | Type                      | Notes                                                   | Support               |
|------------|---------------------------|---------------------------------------------------------|-----------------------|
| ``hybrid`` | bool | Set to 'true' if PTP and SyncE should be used.   | os10 |
| ``profile`` | string | PTP profile. Must be one of 'g8275.1', 'g8275.2', or 'system-default'. | os10 |

**source**

| Key        | Type                      | Notes                                                   | Support               |
|------------|---------------------------|---------------------------------------------------------|-----------------------|
| ``ipv4`` | string | IPv4 source address   | os10 |
| ``ipv6`` | string | IPv6 source address | os10 |

**interfaces**

A dictionary of PTP interface descriptions where the key is the name of the interface.

| Key        | Type                      | Notes                                                   | Support               |
|------------|---------------------------|---------------------------------------------------------|-----------------------|
| ``role`` | string | Role of the interface. Either 'master' or 'slave'   | os10 |

Connection variables
--------------------

Ansible Dell EMC network roles require connection information to establish communication with the nodes in your inventory. This information can exist in the Ansible *group_vars* or *host_vars directories* or inventory, or in the playbook itself.

| Key         | Required | Choices    | Description                                         |
|-------------|----------|------------|-----------------------------------------------------|
| ``ansible_host`` | yes      |            | Specifies the hostname or address for connecting to the remote device over the specified transport |
| ``ansible_port`` | no       |            | Specifies the port used to build the connection to the remote device; if value is unspecified, the `ANSIBLE_REMOTE_PORT` option is used; it defaults to 22 |
| ``ansible_ssh_user`` | no       |            | Specifies the username that authenticates the CLI login for the connection to the remote device; if value is unspecified, the `ANSIBLE_REMOTE_USER` environment variable value is used  |
| ``ansible_ssh_pass`` | no       |            | Specifies the password that authenticates the connection to the remote device |
| ``ansible_become`` | no       | yes, no\*   | Instructs the module to enter privileged mode on the remote device before sending any commands; if value is unspecified, the `ANSIBLE_BECOME` environment variable value is used, and the device attempts to execute all commands in non-privileged mode |
| ``ansible_become_method`` | no       | enable, sudo\*   | Instructs the module to allow the become method to be specified for handling privilege escalation; if value is unspecified, the `ANSIBLE_BECOME_METHOD` environment variable value is used |
| ``ansible_become_pass`` | no       |            | Specifies the password to use if required to enter privileged mode on the remote device; if ``ansible_become`` is set to no this key is not applicable |
| ``ansible_network_os`` | yes      | os10, null\*  | Loads the correct terminal and cliconf plugins to communicate with the remote device |

> **NOTE**: Asterisk (\*) denotes the default value if none is specified.


## Example playbook

This example uses the *os10_ptp* role to setup the ptp clock and define one master and one slave interface. It creates a *hosts* file with the switch details and corresponding variables. The hosts file should define the `ansible_network_os` variable with corresponding Dell EMC OS10 name. 

When `os10_cfg_generate` is set to true, the variable generates the configuration commands as a .part file in *build_dir* path. By default, the variable is set to false. It writes a simple playbook that only references the *os10_ptp* role.

**Sample hosts file**

    leaf1 ansible_host= <ip_address> 

**Sample host_vars/leaf1**
     
    hostname: leaf1
    ansible_become: yes
    ansible_become_method: xxxxx
    ansible_become_pass: xxxxx
    ansible_ssh_user: xxxxx
    ansible_ssh_pass: xxxxx
    ansible_network_os: dellemc.os10.os10
    build_dir: ../temp/temp_os10

    os10_ptp:

      # boundary or end-to-end-transparent
      clock: boundary

      domain: 24

      local_priority: 129
      priority1: 129
      priority2: 135

      source:
        ipv4: 10.0.0.1
        ipv6: fe80::1

      # Set system time using PTP
      system_time: true

      # This must be specified if clock is boundary
      boundary:
        # Enable also SyncE
        hybrid: true
        # g8275.2, g8275.1 or system-default
        profile: g8275.1
  
      interfaces:

        ethernet 1/1/7:
          role: slave

        ethernet 1/1/9:
          role: master

> **NOTE**: Interfaces should be created using the *os10_interface* role.

**Simple playbook to setup system — leaf.yaml**

    - hosts: leaf1
      roles:
         - dellemc.os10.os10_ptp
                
**Run**

    ansible-playbook -i hosts leaf.yaml

(c) 2017-2020 Dell Inc. or its subsidiaries. All rights reserved.\
(c) Copyright 2022 Andreas Florath, Deutsche Telekom AG
