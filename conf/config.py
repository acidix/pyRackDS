__config__ = {
			"main":
				{
					apiurl: "http://racktables/api.php",
					username: "admin",
					password: "secret"
				}
			"conf":
				{
					restrict_tftp: True
				}
			"tags":
				{
					puppet_parent: "puppet",
					cobbler_parent: "cobbler",
					netboot: "netboot"
				}
}
