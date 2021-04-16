from django.db import models
from datetime import datetime

class Ontologies(models.Model):
    ontology_term = models.TextField()
    ontology_type = models.TextField()
    ontology_id = models.TextField()
    ontology_support = models.TextField()
    ontology_status = models.TextField()
    colour_code = models.TextField()
    users = models.TextField()
    last_updated = models.DateTimeField(default=datetime.now, blank=True)