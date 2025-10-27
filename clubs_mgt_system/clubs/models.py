from django.db import models
from django.conf import settings


class Club(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    meeting_time = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="club_logos/", blank=True, null=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="clubs",
        blank=True
    )
    created_by = models.ForeignKey( 
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_clubs",
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

    def member_count(self):
        return self.members.count()



class ClubPost(models.Model):
    club = models.ForeignKey(
        Club, on_delete=models.CASCADE, related_name="posts"
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.club.name})"


class Poll(models.Model):
    club = models.ForeignKey(
        Club, on_delete=models.CASCADE, related_name="polls"
    )
    question = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question

    def total_votes(self):
        """Returns total number of votes across all options"""
        return sum(option.vote_count() for option in self.options.all())


class PollOption(models.Model):
    poll = models.ForeignKey(
        Poll, on_delete=models.CASCADE, related_name="options"
    )
    text = models.CharField(max_length=200)
    votes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="poll_votes",
        blank=True
    )

    def vote_count(self):
        return self.votes.count()

    def __str__(self):
        return f"{self.text} ({self.vote_count()} votes)"


class Event(models.Model):
    club = models.ForeignKey(
        Club, on_delete=models.CASCADE, related_name="events"
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="event_attendees",
        blank=True
    )

    def __str__(self):
        return f"{self.name} ({self.club.name})"

    def attendee_count(self):
        return self.attendees.count()
