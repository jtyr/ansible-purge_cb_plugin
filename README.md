Purge CB for yum_repository module
==================================

This is an example of how to use the `purge` CallBack plugin with the
`yum_repository` module.


Usage
-----

```
$ mkdir /tmp/yum.repos.d{1..3}
$ ansible-playbook -i hosts site.yaml
```


TODO
----

- Implement `task_executor` in the CB plugin.
- Implement `purge` method in the `yum_repository` module.


Author
------

Jiri Tyr


License
-------

MIT
