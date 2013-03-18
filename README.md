pyRackDS
========

Racktables data services

This package is intended to, ultimately, be a two-way interface to:
* use data from racktables to create different kinds of configuration files, and
* use third-party applications to pump data into racktables (such as facter)

Currently this heavily relies on the work of ibettinger from which I use both, the PHP racktables API and the corresponding Python module to consume the data. What my script does is:

1. It queries the racktables API for information about 2 kinds of objects
	* Hosts
	* Networks
2. With that it builds two trees (the host tree and the network tree) that can be consumed by ##The templating engine##
3. It runs ##The templating engine## and creates the files it should


Roadmap:
- include templating engine
- make the trees more flexible
- think of a way of getting data back into racktables



