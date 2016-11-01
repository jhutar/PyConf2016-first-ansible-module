#!/usr/bin/env python

DOCUMENTATION = '''
---
module: yum-repo-manager
short_description: Enable or disable repos as per their name or wildcard
# ... snip ...
'''

EXAMPLES = '''
- yum-repo-manager:

- yum-repo-manager:
    disable: *
    enable:
      - fedora
      - updates
'''

RETURN = '''
enabled:
    description: List of currently enabled repositories
    returned: success or changed
    type: list
    sample: "['fedora', 'updates']"
disabled:
    description: List of currently disabled repositories
    returned: success or changed
    type: list
    sample: "['rpmfusion-free', 'rpmfusion-free-updates']"
...
'''

# WANT_JSON

def main():
    module = AnsibleModule(
        argument_spec = dict(
            disable = dict(),
            enable = dict()
        ),
        supports_check_mode = True
    )
    import yum
    ayum = yum.YumBase()
    enabled = list(str(i) for i in ayum.repos.listEnabled() )
    module.exit_json(changed=False, enabled=enabled, disabled=[])

from ansible.module_utils.basic import AnsibleModule
if __name__ == '__main__':
    main()
