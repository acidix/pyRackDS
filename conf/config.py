__config__ = {
    "racktables":
    {
        "apiurl": "http://racktables/api.php",
        "username": "admin",
        "password": "secret",
        "worker": 5
    },
    "tftp":
    {
        "restrict_tftp": True,
        "netboot_tag": "netboot"
    },
    "tags":
    {
        "special_tags": [ "puppet", "cobbler" ]
    }
}
