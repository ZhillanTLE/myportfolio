from django.contrib import admin

from main.models import Experience, Peer, Project

admin.site.register(Experience)


@admin.register(Peer)
class PeerAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "order", "show_in_peers")
    list_editable = ("order","show_in_peers")
    search_fields = ("name",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "year", "order")
    list_editable = ("order",)
    filter_horizontal = ("peers",)
    search_fields = ("title", "description", "tech_stack")
