from django.db import models
from datetime import datetime

class User(models.Model):
    username = models.TextField(primary_key=True)
    user_id = models.TextField()
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
    tags = models.TextField()
    created_by_user = models.ForeignKey(User, on_delete=models.PROTECT)
    created_date = models.DateTimeField(default=datetime.now, blank=True)
    verified_by_users = models.ManyToManyField(User, related_name='verified_ontologies')
    verified_count = models.IntegerField()

