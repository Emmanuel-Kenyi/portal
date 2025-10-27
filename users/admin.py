from django.contrib import admin
from .models import Profile, StudentPoints, Course, StudentMark, StudentGPA

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'role')
    search_fields = ('user__username', 'name', 'role')


@admin.register(StudentPoints)
class StudentPointsAdmin(admin.ModelAdmin):
    list_display = ('student', 'club', 'points', 'reason', 'awarded_by', 'awarded_at')
    readonly_fields = ('awarded_at',)
    list_filter = ('club', 'student', 'awarded_by')
    search_fields = ('student__username', 'club__name', 'reason')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'credit_units')
    search_fields = ('code', 'name')


@admin.register(StudentMark)
class StudentMarkAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'marks', 'grade_letter', 'grade_point', 'date_recorded')
    readonly_fields = ('grade_letter', 'grade_point', 'date_recorded')
    list_filter = ('course', 'student', 'semester')
    search_fields = ('student__username', 'course__code')


@admin.register(StudentGPA)
class StudentGPAAdmin(admin.ModelAdmin):
    list_display = ('student', 'gpa', 'cgpa', 'updated_at')
    readonly_fields = ('gpa', 'cgpa', 'updated_at')
    search_fields = ('student__username',)
