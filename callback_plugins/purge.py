# (c) 2016, Jiri Tyr <jiri.tyr@gmail.com>
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

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

from sets import Set

try:
    from __main__ import display as global_display
except ImportError:
    from ansible.utils.display import Display
    global_display = Display()

__metaclass__ = type
__all__ = ["CallbackBase"]


class CallbackModule:
    def __init__(self, display=None):
        if display:
            self._display = display
        else:
            self._display = global_display

        # Purge info
        self.enabled = False
        self.modules = []
        self.module_options = []
        self.results = {}

        # Playbook info
        self.playbook_inventory = None

    def v2_playbook_on_start(self, playbook):
        # Seach for magic variables in all plays
        for play in playbook.get_plays():
            vm = play.get_variable_manager()
            all_vars = vm.get_vars(loader=play.get_loader(), play=play)

            # Check if purging is enabled
            if (
                    '_purge_enabled' in all_vars and
                    all_vars['_purge_enabled']):
                self.enabled = True

            # Get list of modules to purge
            if (
                    self.enabled and
                    '_purge_modules' in all_vars and
                    isinstance(all_vars['_purge_modules'], list)):
                self.modules = all_vars['_purge_modules']

            # Get list of options for the module purging
            if (
                    self.enabled and
                    '_purge_module_options' in all_vars and
                    isinstance(all_vars['_purge_module_options'], dict)):
                self.options = all_vars['_purge_module_options']

    def v2_runner_on_ok(self, result):
        if not self.enabled:
            return

        res = result._result
        module_name = None

        if 'invocation' in res:
            module_name = res['invocation']['module_name']

        # Remember information for selected modules
        if (
                module_name is not None and
                module_name in self.modules):

            host = result._host

            # Create module record
            if module_name not in self.results:
                self.results[module_name] = {}
            if host not in self.results[module_name]:
                self.results[module_name][host] = Set()

            # Record module result for the host
            self.results[module_name][host].add(res['_managed'])

    def v2_playbook_on_stats(self, stats):
        if not self.enabled:
            return

        self._display.warning("tasks:")

        # Show which tasks should be run
        for module, hosts in self.results.iteritems():
            for host, results in hosts.iteritems():
                self._display.warning(
                    "  - %s[%s] stage=purge _managed=[\"%s\"]" % (
                        module, host,
                        '", "'.join(results)))
