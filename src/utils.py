#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of ppaurl
#
# Copyright (C) 2016-2017 Lorenzo Carbonell
# lorenzo.carbonell.cerezo@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import subprocess
import shlex


def get_version():
    command = 'lsb_release -c'
    po = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, shell=False)
    out, err = po.communicate()
    return_code = po.wait()
    if return_code == 0:
        return out.decode().split('Codename:\t')[1].replace('\n', '')
    return None


def is_package_installed(package_name):
    command = 'dpkg-query --show --showformat="${db:Status-Status}\n" "%s"' % (
        package_name)
    po = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, shell=False)
    out, err = po.communicate()
    return_code = po.wait()
    if return_code == 0:
        return True
    return False


if __name__ == '__main__':
    print(is_package_installed('my-weather-indicator'))
    print(is_package_installed('utext'))
    print(get_version())
