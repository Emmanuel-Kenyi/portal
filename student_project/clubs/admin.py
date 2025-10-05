from django.contrib import admin
from .models import Club, ClubPost, Poll, PollOption, Event

# Club
@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'meeting_time')
    search_fields = ('name',)

# ClubPost
@admin.register(ClubPost)
class ClubPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'club', 'author', 'created_at')
    search_fields = ('title', 'content')
    list_filter = ('club', 'created_at')

# Poll
@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('question', 'club', 'created_by', 'created_at')
    search_fields = ('question',)
    list_filter = ('club', 'created_at')

# PollOption
@admin.register(PollOption)
class PollOptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'poll', 'vote_count')
    search_fields = ('text',)

# Event
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'club', 'date')
    list_filter = ('club', 'date')
    search_fields = ('name', 'description')
