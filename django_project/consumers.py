import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
from pages.services import get_market_snapshot


class StockConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send_stock_updates()

        self.update_task = asyncio.create_task(self.stock_update_loop())

    async def send_stock_updates(self):
        symbols = ["AAPL", "MSFT", "GOOG", "NVDA"]
        market_data = await sync_to_async(get_market_snapshot)(symbols)

        for stock in market_data:
            if not stock.get("error"):
                await self.send_json(
                    {
                        "symbol": stock["ticker_code"],
                        "price": stock["price"],
                        "status": "success",
                    }
                )

    async def stock_update_loop(self):
        while True:
            await asyncio.sleep(300)
            await self.send_stock_updates()

    async def disconnect(self, close_code):
        if hasattr(self, "update_task"):
            self.update_task.cancel()

            try:
                await self.update_task
            except asyncio.CancelledError:
                print("Stock update task cancelled successfully.")
