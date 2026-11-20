from channels.generic.websocket import AsyncJsonWebsocketConsumer


class StockConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()

        await self.send_json(
            {
                "symbol": "AAPL",
                "price": 150.25,
                "status": "success",
            }
        )

        await self.send_json({"symbol": "GOOGL", "price": 2800.75, "status": "success"})

    async def disconnect(self, close_code):
        pass
