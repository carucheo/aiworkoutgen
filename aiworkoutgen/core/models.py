from django.db import models

class WorkoutPlan(models.Model):
    WORKOUT_DURATIONS = [
        ('15', '15 minutes'),
        ('30', '30 minutes'),
        ('45', '45 minutes'),
        ('60', '60 minutes'),
        ('75', '75 minutes'),
        ('90', '90 minutes'),
    ]

    TARGET_AREAS = [
        ('Core/Abs', 'Core/Abs'),
        ('Legs', 'Legs'),
        ('Arms', 'Arms'),
        ('Full Body', 'Full Body'),
        ('Chest', 'Chest'),
        ('Back', 'Back'),
    ]

    EQUIPMENT_CHOICES = [
        ('Dumbbells', 'Dumbbells'),
        ('Barbell', 'Barbell'),
        ('Bench', 'Bench'),
        ('Squat Rack', 'Squat Rack'),
        ('Cables', 'Cables'),
        ('Bodyweight', 'Bodyweight'),
    ]

    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    duration = models.CharField(max_length=15, choices=WORKOUT_DURATIONS)
    target_area = models.CharField(max_length=50, choices=TARGET_AREAS)
    equipment = models.CharField(max_length=50, choices=EQUIPMENT_CHOICES)
    custom_target = models.CharField(max_length=100, blank=True, null=True)
    custom_equipment = models.CharField(max_length=100, blank=True, null=True)
    sections = models.JSONField()  # Updated to use django.db.models.JSONField
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s workout plan for {self.target_area} - {self.duration} mins"