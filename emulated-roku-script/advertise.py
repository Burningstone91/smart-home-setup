"""Advertise an emulated Roku API on the specified address."""

if __name__ == "__main__":
    import logging

    from asyncio import get_event_loop
    from argparse import ArgumentParser
    from os import name as osname

    from emulated_roku import EmulatedRokuDiscoveryProtocol, \
        get_local_ip, \
        MULTICAST_GROUP, MULTICAST_PORT

    logging.basicConfig(level=logging.DEBUG)

    parser = ArgumentParser(description='Advertise an emulated Roku API on the specified address.')
    parser.add_argument('--multicast_ip', type=str,
                        help='Multicast interface to listen on')
    parser.add_argument('--api_ip', type=str, required=True,
                        help='IP address of the emulated Roku API')
    parser.add_argument('--api_port', type=int, required=True,
                        help='Port of the emulated Roku API.')
    parser.add_argument('--name', type=str, default="Home Assistant",
                        help='Name of the emulated Roku instance')
    parser.add_argument('--bind_multicast', type=bool,
                        help='Whether to bind the multicast group or interface')

    args = parser.parse_args()


    async def start_emulated_roku(loop):
        multicast_ip = args.multicast_ip if args.multicast_ip else get_local_ip()
        bind_multicast = args.bind_multicast if args.bind_multicast else osname != "nt"

        _, discovery_proto = await loop.create_datagram_endpoint(
            lambda: EmulatedRokuDiscoveryProtocol(loop,
                                                  multicast_ip, args.name,
                                                  args.api_ip,
                                                  args.api_port),
            local_addr=(
                MULTICAST_GROUP if bind_multicast else multicast_ip,
                MULTICAST_PORT),
            reuse_address=True)


    loop = get_event_loop()

    loop.run_until_complete(start_emulated_roku(loop))

    loop.run_forever()
