pyRackDS
========

Python data services for [Racktables](http://github.com/RackTables/racktables).

# What does it do?

This package is intended to, ultimately, be a two-way interface to:
* use data from [Racktables](http://github.com/racktables/racktables) to create different kinds of configuration files, and
* use third-party applications to pump data into [Racktables](http://github.com/racktables/racktables) (such as facter)

Currently this heavily relies on the work of [Ian Bettinger](https://github.com/ibettinger) from which I borrow both, the PHP-based [Racktables-API](https://github.com/ibettinger/racktables) and the corresponding [Python module](https://github.com/ibettinger/racktables-py-client) to consume the data. 

What you will get is a well documented, Python-dictionary based way of creating files via the Cheetah templating engine. This by itself is sufficient to create e.g.

* Puppet node definitions
* Cobbler system registrations
* Nagios / Icinga configurations

Those templates are supplied as examples how to use both, the templating engine and the definitions to create the files needed to run the service(s).

pyRackDS is fully customizable and I've spent enough time documenting the iterations for you to extend it. Need information about the asset tag? Just add it to the tree … I thought about making the content of the tree configurable -- but given the expected audience I decided against it. Hacking a couple of lines in Python will get you there goal anyway.

# How do I use it?

Just clone the repository. It's all there, including examples how to use the templating engine. There are 3 dictionary trees:

- allHosts
- allNetworks
- allTags

A detailled description with example data will be made available soon.

To activate a template, you need 2 things:

- the template (surprise) 
(ending in **.tmpl** in the **templates.d** directory)
- a definition (*surprise!*) 
(ending in **.cfg** in the **definitions.d** directory)

The definition is mainly there to some more flexibility in the way you can create files. It'll give you the option to specify

- a target directory with the variable **outputdir** (such as /etc/puppet/manifests/nodes)
- a file extension with the variable **extension** (such as .pp)
- burst mode (*what?*) with the variable **burst**

## Burst mode

This is tricky. And the name might be confusing - but it works for me. I wanted to not only be able to run through the template with all the trees at once, but for each object in a specific tree as well. This gives you the ability to create one file per host, per network, per tag (you get the idea). Currently available *burst modes* are:

- **none** (default) 
(available dictionaries: *allHosts, allNetworks, allTags*)
- hosts
(available dictionary: *host*)
- networks
(available dictionary: *network*)
- tags
(available dictionary: *tag*)
- tftp
(available dictionary: *iface*)

For burst mode *none*, the output file will be named like the template, with the ending specified in the definition (mytemplate.tmpl with mytemplate.cfg will create mytemplate.extension). For all other burst methods, the files will be named like the subelement-name followed by the extension. For hosts, this means you get:

- hostname1.pp
- hostname2.pp
- hostname3.pp

The definition uses the default Python *ConfigParser* module and therefore looks like an ini-style configuration:

    [definition]
    outputdir = /var/tmp/puppet/
    extension = .pp
    burst = hosts

The configuration option *extension* is optional (aka not used) for burst methode *tftp*


# Configuring pyRackDS

pyRackDS only needs some minor configuration, thus, basically, the API URL plus username and password. It's stored in the *conf* directory and named *main.cfg*:

    [main]
    apiurl = "http://racktables/api.php"
    username = admin
    password = mypassword
     
    [tags]
    puppet_parent = puppet
    cobbler_parent = cobbler

The two additional configurations are specific to the main purpose - configuration management. You need to specify the parent tag names for puppet and cobbler tags.

The *puppet* parent tag is for assigning one or multiple *puppet* classes to a node.

The *cobbler* tag is to assign a *cobbler* profile. At least that's how I implemented it. Change it as you like - as I said - it's easily customizable and should ideally serve whatever use-case you need.

