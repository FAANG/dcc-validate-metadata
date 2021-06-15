from django.db import models
from datetime import datetime

class User(models.Model):
    username = models.TextField(primary_key=True)
    first_name = models.TextField()
    last_name = models.TextField()
    email = models.EmailField()
    institute = models.TextField()

class Ontologies(models.Model):
    ontology_term = models.TextField()
    ontology_type = models.TextField()
    ontology_id = models.TextField()
    ontology_support = models.TextField()
    ontology_status = models.TextField()
    colour_code = models.TextField()
    project = models.TextField()
    species = models.TextField()
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    verified_count = models.IntegerField()
    created_date = models.DateTimeField(default=datetime.now, blank=True)

