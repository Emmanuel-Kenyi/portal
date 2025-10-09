from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("lecturer", "Lecturer"),
        ("admin", "Admin"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.role})"

class StudentPoints(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='points_received')
    club = models.ForeignKey('clubs.Club', on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    reason = models.CharField(max_length=200)
    awarded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='points_awarded')
    awarded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Student Points"
    
    def __str__(self):
        return f"{self.student.username} - {self.points} points for {self.reason}"