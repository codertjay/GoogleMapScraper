from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
# Create your models here.
from django.utils import timezone


class SearchInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    keyword = models.CharField(max_length=500, blank=True, null=True)
    location = models.CharField(max_length=500, blank=True, null=True)
    platform = models.CharField(max_length=500, blank=True, null=True)
    completed = models.BooleanField(default=False)
    total_places = models.IntegerField(default=0)
    scraped_places = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    @property
    def progress(self):
        next_twenty_minutes = self.timestamp + timedelta(minutes=40)
        if self.total_places > 150:
            next_twenty_minutes = self.timestamp + timedelta(minutes=120)
        if self.total_places == 0:
            self.total_places = 1
        if self.scraped_places > self.total_places:
            self.scraped_places = self.total_places
            self.completed = True
            self.save()
        if timezone.now() > next_twenty_minutes:
            self.scraped_places = self.total_places
            self.completed = True
            self.save()
        progress = (self.scraped_places / self.total_places) * 100
        return round(progress, 2)

    @property
    def scraped_emails(self):
        return self.history_set.filter(email__contains="@").count()


class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    search_info = models.ForeignKey(SearchInfo, on_delete=models.CASCADE, blank=True, null=True)
    phone_number = models.CharField(max_length=250, blank=True, null=True)
    email = models.CharField(max_length=500, blank=True, null=True)
    business_name = models.CharField(max_length=250, blank=True, null=True)
    municipality = models.CharField(max_length=250, blank=True, null=True)
    plus_code = models.CharField(max_length=250, blank=True, null=True)
    place_id = models.CharField(max_length=250, blank=True, null=True)
    cid = models.CharField(max_length=250, blank=True, null=True)
    opening_hours = models.CharField(max_length=250, blank=True, null=True)
    google_map_url = models.CharField(max_length=250, blank=True, null=True)
    latitude = models.CharField(max_length=250, blank=True, null=True)
    longitude = models.CharField(max_length=250, blank=True, null=True)
    reviews_url = models.CharField(max_length=250, blank=True, null=True)
    average_rating = models.CharField(max_length=250, blank=True, null=True)
    review_count = models.CharField(max_length=250, blank=True, null=True)
    website = models.CharField(max_length=250, blank=True, null=True)
    full_address = models.CharField(max_length=250, blank=True, null=True)
    street = models.CharField(max_length=250, blank=True, null=True)
    categories = models.CharField(max_length=250, blank=True, null=True)
    image = models.URLField(blank=True, null=True, max_length=500)
    social_media_links = models.CharField(blank=True, null=True, max_length=500)
    phones = models.CharField(max_length=250, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
