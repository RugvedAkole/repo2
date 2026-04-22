from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Material(models.Model):
    # Defining the categories for the dropdown
    CATEGORY_CHOICES = [
        ('Notes', 'Notes'),
        ('Paper', 'Previous Year Papers'),
        ('Assignment', 'Assignments'),
    ]

    SEMESTER_CHOICES = [
        ('Sem 1', 'Semester 1'), ('Sem 2', 'Semester 2'),
        ('Sem 3', 'Semester 3'), ('Sem 4', 'Semester 4'),
        ('Sem 5', 'Semester 5'), ('Sem 6', 'Semester 6'),
        ('Sem 7', 'Semester 7'), ('Sem 8', 'Semester 8'),
    ]

    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    semester = models.CharField(max_length=20, choices=SEMESTER_CHOICES, default='Sem 1')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    
    # This stores the actual PDF file in a folder named 'uploads/'
    file = models.FileField(upload_to='materials/')
    
    # This links the material to the user who uploaded it
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # To track likes (Many users can like many materials)
    likes = models.ManyToManyField(User, related_name='liked_materials', blank=True)

    def __str__(self):
        return self.title

    @property
    def total_likes(self):
        return self.likes.count()

class StudentProfile(models.Model):
    # This links the profile to your existing login user
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Extra fields for the report (matching the image)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    education = models.CharField(max_length=100, blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    
    # Automatically tracks when this enquiry/signup was made
    # (Matches the "Enquiry Date" column in the image)
    enquiry_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"