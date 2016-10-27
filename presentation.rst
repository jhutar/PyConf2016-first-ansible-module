Writing my first Ansible module
===============================

Maybe you are using Ansible but realized you are using "shell" module where something nicer could be used? We will go through creating a simple "yum-repo-manager" module.

PyConf2016 Brno
Jan Hutař

~~~~

What is Ansible?
================

From ansible.com: App deployment, configuration management and orchestration - all from one system. Ansible is powerful IT automation that you can learn quickly.

In normal worlds: Write playbooks (scripts in simple YAML format) which describes correct state (i.e. playbook are supposed to say something like "package httpd is installed" instead of "if httpd is not installed install it") of the system and run them on your systems. Playbooks are made of plays and plays are made of modules. There is a big library of modules already in default Ansible, but maybe you need a custom one? Lets create it.

Competitors: Pulp, Chef, Salt, CFEngine...
Google trends on these: https://www.google.cz/trends/explore?cat=5&date=all&q=%2Fm%2F0k0vzjb,%2Fm%2F03d3cjz,%2Fm%2F05zxlz3,%2Fm%2F0hn8c6s,CFEngine

~~~~

Resources
=========

Official guide:

  http://docs.ansible.com/ansible/developing_modules.html

Do not create unnecessary modules:

  http://docs.ansible.com/ansible/modules_by_category.html

~~~~

How module interfaces with Ansible
==================================

Super easy - no python magic involved. Module is script in any language (any which target system can execute) which prints JSON on its output when done.

How is the module executed:

 * transfered to target system
 * executed
 * its JSON formatted stdout is parsed and transfered back to source system

Lets take a look at this during module's runtime:

 * content of sys.argv module
 * different input types

~~~~

Content of sys.argv module is:
==============================

Content of `sys.argv` is:

.. code:: python

    ['/home/pok/.ansible_module_generated', '/home/pok/.ansible_test_module_arguments']

.. code:: sh

    $ cat /home/pok/.ansible_module_generated
    #!/usr/bin/env python
    [...module here...]
    $ cat /home/pok/.ansible_test_module_arguments
    key=value

It is up to the module to parse this input values file if it wants some input.

~~~~

Different input types possible:
===============================

Input provided in temp file (first argument when executing), but can have multiple formats:

 * by `key=value` pairs
   * we need shell like splitting when parsing this
 * in JSON format
 * using free-form syntax (e.g. *command* module uses this)

~~~~

key=value
---------

This is default mode:

.. code:: sh

    $ ansible/hacking/test-module -m ./timetest.py -a "key1=value1 key2=value2"
    [...]
    $ cat /home/pok/.ansible_test_module_arguments
    key1=value1 key2=value2

Correct splitting key=value arguments
-------------------------------------

When splitting `key1=value1 key2="va lue 2"` strings, we have to be cautions:

.. code:: python

    >>> "Hello 'my world'".split()
    ['Hello', "'my", "world'"]
    >>> import shlex
    >>> shlex.split("Hello 'my world'")
    ['Hello', 'my world']

~~~~

In json
-------

Place string **WANT_JSON** somewhere into the module's file:

.. code:: sh

    $ ansible/hacking/test-module -m ./timetest.py -a "key1=value1 key2=value2"
    [...]
    $ cat /home/pok/.ansible_test_module_arguments
    {"key1": "value1", "key2": "value2"}

~~~~

Free-form syntax
----------------

Used by *command* module for example:

.. code:: yaml

    - name: "Synchronize time"
      command:
        rdate -s tak.cesnet.cz

Not recemended by docs, but doable:

.. code:: sh

    $ ansible/hacking/test-module -m ./timetest.py -a "bla bal bla kay=value"
    Without WANT_JSON:
    $ cat /home/pok/.ansible_test_module_arguments
    bla bal bla kay=value
    With WANT_JSON:
    $ cat /home/pok/.ansible_test_module_arguments
    {"_raw_params": "bla bal bla", "kay": "value"}

~~~~

Running the module:
===================

 * using `test-module` script from ansible's git
 * directly with `ansible` command (so called ad-hoc command)
 * from playbook using `ansible-playbook`

NOTE: To specify where Ansible should get additional modules, use either *ANSIBLE_LIBRARY* env variable, *--module-path* command line option or put your module to *./library/*.

~~~~

Running module with `test-module`
---------------------------------

.. code:: sh

    $ git clone git://github.com/ansible/ansible.git --recursive
    $ source ansible/hacking/env-setup
    $ ansible/hacking/test-module -m ./timetest.py

Produces:

.. code::

    * including generated source, if any, saving to: /home/pok/.ansible_module_generated
    ***********************************
    RAW OUTPUT
    {"time": "2016-10-27 10:54:09.638336"}
    
    
    ***********************************
    PARSED OUTPUT
    {
        "time": "2016-10-27 10:54:09.638336"
    }

Ad-hoc command to run our module:
---------------------------------

.. code:: sh

    $ ansible -i hosts.ini --module-path=. -m timetest --connection=local all
    localhost | SUCCESS => {
        "changed": false, 
        "time": "2016-10-27 10:58:39.565884"
    }

Run the module from playbook:
-----------------------------

Having this in the *timetest.yaml*:

.. code:: yaml

    ---
    - hosts: localhost
      connection: local
      tasks:
        - timetest:
          register: timetest_result
        - debug: var=timetest_result
    ....

and just *localhost* in *hosts.ini*, run the playbook with:

.. code:: sh

    $ ansible-playbook timetest.yaml -i hosts.ini --module-path=.
    
    PLAY [localhost] ***************************************************************
    
    TASK [setup] *******************************************************************
    ok: [localhost]
    
    TASK [timetest] ****************************************************************
    ok: [localhost]
    
    TASK [debug] *******************************************************************
    ok: [localhost] => {
        "timetest_result": {
            "changed": false, 
            "time": "2016-10-27 11:06:37.366455"
        }
    }
    
    PLAY RECAP *********************************************************************
    localhost                  : ok=3    changed=0    unreachable=0    failed=0

Running the module in a loop:
-----------------------------

Change your playbook to run the module in the loop with 2 items (well, our module actually does not take options now, but that does not stop me :-)):

.. code:: yaml

    - timetest:
      with_items:
        - a
        - b
      register: timetest_result

Module is actually executed twice now:

.. code::

    TASK [timetest] ****************************************************************
    ok: [localhost] => (item=a)
    ok: [localhost] => (item=b)
    
    TASK [debug] *******************************************************************
    ok: [localhost] => {
        "timetest_result": {
            "changed": false, 
            "msg": "All items completed", 
            "results": [
                {
                    "_ansible_item_result": true, 
                    "_ansible_no_log": false, 
                    "_ansible_parsed": true, 
                    "invocation": {
                        "module_name": "timetest"
                    }, 
                    "item": "a", 
                    "time": "2016-10-27 11:10:17.417317"
                }, 
                {
                    "_ansible_item_result": true, 
                    "_ansible_no_log": false, 
                    "_ansible_parsed": true, 
                    "invocation": {
                        "module_name": "timetest"
                    }, 
                    "item": "b", 
                    "time": "2016-10-27 11:10:17.446832"
                }
            ]
        }
    }

Some more wisdom:
=================

 * module can enhance facts gathered by *setup* module by returning `ansible_facts` variable in the JSON
 * if you want your module to support *check mode*, variable *_ansible_check_mode=True* will be in the input, but official way would be to use *AnsibleModule* boilpreparate
 * in case of failure, JSON output should include *failed* key and explanation in *msg*
 * writing to *stderr* in the module makes it fail from Ansible's pow
 * to document your module, use *DOCUMENTATION* variable







$ ansible/hacking/test-module -m yum-repo-manager.py  -c
* including generated source, if any, saving to: /home/pok/.ansible_module_generated
***********************************
INVALID OUTPUT FROM ANSIBALLZ MODULE WRAPPER
