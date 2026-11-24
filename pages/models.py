from django.db import models
from django.conf import settings


class Stock(models.Model):
    """ Represents a stock, index, or ETF with its ticker code, display name, and asset type."""
    class AssetType(models.TextChoices):
        # Defines the types of assets that can be represented in the Stock model.
        STOCK = "STK", "Stock"
        INDEX = "IDX", "Index"
        ETF = "ETF", "ETF"

    ticker_code = models.CharField(max_length=15, unique=True)
    display_name = models.CharField(max_length=100, blank=True)
    asset_type = models.CharField(
        max_length=3,
        choices=AssetType.choices,
        default=AssetType.STOCK,
    )

    @staticmethod
    def infer_asset_type(symbol):
        # Yahoo Finance-style index symbols start with "^".
        # ETFs can't be detected from the symbol, so set them in the admin.
        if symbol.startswith("^"):
            return Stock.AssetType.INDEX
        return Stock.AssetType.STOCK


    def __str__(self):
        return f"{self.display_name} - {self.ticker_code}"


class Watchlist(models.Model):
    """Watchlist model that associates a user with multiple stocks through WatchlistItem."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="watchlist"
    )

    stocks = models.ManyToManyField(
        Stock,
        through="WatchlistItem",
        blank=True,
    )

    def __str__(self):
        return f"{self.user}'s watchlist"

class WatchlistItem(models.Model):
    """Intermediate model to represent the many-to-many relationship between Watchlist and Stock."""
    watchlist = models.ForeignKey(
        Watchlist, 
        on_delete=models.CASCADE,
        related_name="items"
        )

    stock = models.ForeignKey(
        Stock, 
        on_delete=models.CASCADE, 
        related_name="watchlist_items"
        )
        
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensures that each stock can only appear once in a user's watchlist and orders items by the time they were added.
        ordering = ["-added_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["watchlist", "stock"],
                name="unique_watchlist_stock",
            ),
        ]

    def __str__(self):
        return f"{self.watchlist.user} - {self.stock.ticker_code}"