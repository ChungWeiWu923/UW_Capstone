from django.db import models


""" Table1: kol_kolinfo
"""
class KolInfo(models.Model):
    # KOL name
    name = models.CharField(max_length=32)

    # KOL field
    field = models.CharField(max_length=32)

    # KOL affiliation
    affiliation = models.CharField(max_length=10000)

    # Score (DC, CC, BC, YOE_FEATURE)
    score = models.FloatField()

    # Number of publication
    pub_count = models.IntegerField()

    # Number of co-authorship
    coauthorship_count = models.IntegerField()

    # Year of experience
    yoe = models.FloatField()


""" Table2: kol_kolpublist
"""
class KolPubList(models.Model):
    # KOL name
    name = models.CharField(max_length=32)

    # Title of publication
    article_title = models.CharField(max_length=1000)
