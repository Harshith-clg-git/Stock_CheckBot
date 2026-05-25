import asyncio
import sys
from main import scan_all

sys.stdout.reconfigure(encoding="utf-8")

async def test():
    print("Running a single scan across all platforms...")
    await scan_all()
    print("Test complete!")

if __name__ == "__main__":
    asyncio.run(test())
