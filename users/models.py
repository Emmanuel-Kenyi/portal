from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .utils import get_grade_point, calculate_gpa, calculate_cgpa


# =====================
# 👥 USER & PROFILE MODELS
# =====================

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


# =====================
# 🏅 STUDENT POINTS MODEL
# =====================

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


# =====================
# 🎓 ACADEMIC MODELS
# =====================

class Course(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    credit_units = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.code} - {self.name}"


class StudentMark(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_marks')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    marks = models.DecimalField(max_digits=5, decimal_places=2)
    grade_letter = models.CharField(max_length=2, blank=True)
    grade_point = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    remarks = models.CharField(max_length=50, blank=True)
    semester = models.CharField(max_length=20, blank=True, null=True)
    date_recorded = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Automatically assign grade details when saving
        gp, grade, remark = get_grade_point(float(self.marks))
        self.grade_point = gp
        self.grade_letter = grade
        self.remarks = remark
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.username} - {self.course.code}: {self.marks} ({self.grade_letter})"


class StudentGPA(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE, related_name='academic_record')
    gpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)

    def update_gpa(self):
        """Recalculate GPA and CGPA from StudentMark entries."""
        marks_list = [
            {'mark': float(m.marks), 'credit_units': m.course.credit_units}
            for m in self.student.student_marks.all()
        ]
        if not marks_list:
            self.gpa = 0.00
            self.cgpa = 0.00
        else:
            self.gpa = calculate_gpa(marks_list)
            self.cgpa = calculate_cgpa([{'marks': marks_list}])
        self.save()

    def __str__(self):
        return f"{self.student.username} - GPA: {self.gpa}, CGPA: {self.cgpa}"


# =====================
# ⚙️ SIGNALS FOR AUTO GPA UPDATE
# =====================

@receiver(post_save, sender=StudentMark)
def update_student_gpa(sender, instance, **kwargs):
    """
    Automatically recalculate GPA and CGPA
    whenever a student's mark is created or updated.
    """
    record, _ = StudentGPA.objects.get_or_create(student=instance.student)
    record.update_gpa()


class Report(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    title = models.CharField(max_length=255)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    file = models.FileField(upload_to='reports/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.status})"
