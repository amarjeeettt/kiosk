import asyncio

async def delay(seconds):
    await asyncio.sleep(seconds)

async def main():
    print("Start")
    await delay(3)
    print("After 3 seconds")

asyncio.run(main())
