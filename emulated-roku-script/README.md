# emulated_roku

This library is for emulating the Roku API. Discovery is tested with Logitech Harmony and Android remotes.
Only key press / down / up events and app launches (10 dummy apps) are implemented in the RokuCommandHandler callback.  
Other functionality such as input, search will not work.
See the [example](example.py) on how to use.