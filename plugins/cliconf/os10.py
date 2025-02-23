#
# (c) 2020 Red Hat Inc.
#
# (c) 2020 Dell Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
---
cliconf: os10
short_description: Use os10 cliconf to run command on Dell OS10 platform
description:
  - This os10 plugin provides low level abstraction apis for
    sending and receiving CLI commands from Dell OS10 network devices.
"""

import re
import json

from itertools import chain

from ansible.module_utils._text import to_bytes, to_text
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import to_list
from ansible.plugins.cliconf import CliconfBase, enable_mode


class Cliconf(CliconfBase):

    def get_device_info(self):
        device_info = {}

        device_info['network_os'] = 'dellemc.os10.os10'
        reply = self.get('show version')
        data = to_text(reply, errors='surrogate_or_strict').strip()

        match = re.search(r'OS Version (\S+)', data)
        if match:
            device_info['network_os_version'] = match.group(1)

        match = re.search(r'System Type (\S+)', data, re.M)
        if match:
            device_info['network_os_model'] = match.group(1)

        reply = self.get('show running-configuration | grep hostname')
        data = to_text(reply, errors='surrogate_or_strict').strip()
        match = re.search(r'^hostname (.+)', data, re.M)
        if match:
            device_info['network_os_hostname'] = match.group(1)

        return device_info

    @enable_mode
    def get_config(self, source='running', flags=None, format='text'):
        if source not in ('running', 'startup'):
            return self.invalid_params("fetching configuration from %s is not supported" % source)
        if source == 'running':
            cmd = 'show running-config all'
        else:
            cmd = 'show startup-config'
        return self.send_command(cmd)

    @enable_mode
    def edit_config(self, command):
        for cmd in chain(['configure terminal'], to_list(command), ['end']):
            self.send_command(to_bytes(cmd))

    def get(self, command, prompt=None, answer=None, sendonly=False, newline=True, check_all=False):
        return self.send_command(command=command, prompt=prompt, answer=answer, sendonly=sendonly, newline=newline, check_all=check_all)

    def get_capabilities(self):
        result = super(Cliconf, self).get_capabilities()
        return json.dumps(result)
