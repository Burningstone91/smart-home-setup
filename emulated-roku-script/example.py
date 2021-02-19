"""Example script for using the Emulated Roku api."""

if __name__ == "__main__":
    import asyncio
    import logging
    import emulated_roku

    logging.basicConfig(level=logging.DEBUG)

    async def start_emulated_roku(loop):
        roku_api = emulated_roku.EmulatedRokuServer(
            loop, emulated_roku.EmulatedRokuCommandHandler(),
            "test_roku", emulated_roku.get_local_ip(), 8060
        )

        await roku_api.start()


    loop = asyncio.get_event_loop()

    loop.run_until_complete(start_emulated_roku(loop))

    loop.run_forever()
