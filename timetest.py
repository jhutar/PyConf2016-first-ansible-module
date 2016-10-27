#!/usr/bin/env python

DOCUMENTATION = '''
---
module: timetest
short_description: Get or set time
# ... snip ...
'''

EXAMPLES = '''
- timetest:

- timetest:
    time: 2017-01-01 00:00:00
'''

RETURN = '''
time:
    description: Current time on remote syste,
    returned: success or changed
    type: string
    sample: "2017-01-01 00:00:00"
...
'''

import subprocess
import sys
import datetime

def main():
    module = AnsibleModule(
        argument_spec = dict(
            time = dict()
        )
    )
    changed = False
    if module.params['time']:
        rc = subprocess.call(["date", "-s", "'%s'" % module.params['time']])
        if rc == 0:
            changed = True
        else:
            module.fail_json(msg="failed setting the time")
            sys.exit(1)
    date = str(datetime.datetime.now())
    module.exit_json(changed=changed, time=date)

from ansible.module_utils.basic import AnsibleModule
if __name__ == '__main__':
    main()
