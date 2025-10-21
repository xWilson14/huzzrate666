from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="items/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def avg_appearance(self):
        agg = self.ratings.aggregate(avg=models.Avg("appearance_score"))
        return round(agg["avg"] or 0, 2)

    def avg_personality(self):
        agg = self.ratings.aggregate(avg=models.Avg("personality_score"))
        return round(agg["avg"] or 0, 2)

    def avg_total(self):
        appearance = self.avg_appearance()
        personality = self.avg_personality()
        return round((appearance + personality) / 2, 2)

    def ratings_count(self):
        return self.ratings.count()

    def __str__(self):
        return self.name

class Token(models.Model):
    value = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.value

class Rating(models.Model):
    token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name="ratings")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="ratings")
    appearance_score = models.PositiveSmallIntegerField()  # 1-10
    personality_score = models.PositiveSmallIntegerField()  # 1-10
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("token", "item")

    def __str__(self):
        return f"{self.token} -> {self.item} = A:{self.appearance_score} P:{self.personality_score}"