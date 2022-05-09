from django.contrib import admin
from .models import Contest, Problem, SubContest, SubContestLevel
# Register your models here.

admin.site.register(Problem)
admin.site.register(SubContest)
admin.site.register(SubContestLevel)
admin.site.register(Contest)
