from django.utils.html import strip_tags
from rest_framework import serializers

from main.forms import collaborators, find_or_create_collaborator
from main.models import Experience, Peer, Project


class PeerSerializer(serializers.ModelSerializer):
    """Read-only builder chip: name and photo only, never the guestbook message."""
    icon_url = serializers.CharField(source="icon_src", read_only=True)

    class Meta:
        model = Peer
        fields = ["id", "name", "icon_url"]
        read_only_fields = fields


class ProjectSerializer(serializers.ModelSerializer):
    # Computed for the client; a client can never write these
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()
    image_src = serializers.CharField(read_only=True)
    tech_list = serializers.ListField(child=serializers.CharField(), read_only=True)
    team_label = serializers.CharField(read_only=True)
    peers = PeerSerializer(many=True, read_only=True)

    # Builders are written by id, or typed in as a new collaborator
    peer_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, required=False, source="peers",
        queryset=collaborators(),
    )
    new_peer = serializers.CharField(write_only=True, required=False, allow_blank=True, max_length=100)
    new_peer_icon = serializers.URLField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Project
        fields = [
            "id", "title", "year", "role", "context", "description", "tech_stack",
            "image", "repo_url", "live_url",
            "image_src", "tech_list", "team_label", "peers",
            "peer_ids", "new_peer", "new_peer_icon",
            "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id"]

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_role(self, value):
        return strip_tags(value).strip()

    def validate_context(self, value):
        return strip_tags(value).strip()

    def validate_description(self, value):
        return strip_tags(value)

    def validate_tech_stack(self, value):
        return strip_tags(value)

    def validate_new_peer(self, value):
        return strip_tags(value).strip()

    def _add_new_peer(self, project, name, icon):
        if name:
            project.peers.add(find_or_create_collaborator(name, icon))

    def create(self, validated_data):
        name = validated_data.pop("new_peer", "")
        icon = validated_data.pop("new_peer_icon", "")
        project = super().create(validated_data)
        self._add_new_peer(project, name, icon)
        return project

    def update(self, instance, validated_data):
        name = validated_data.pop("new_peer", "")
        icon = validated_data.pop("new_peer_icon", "")
        project = super().update(instance, validated_data)
        self._add_new_peer(project, name, icon)
        return project

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())


class ExperienceSerializer(serializers.ModelSerializer):
    category_label = serializers.CharField(source="get_category_display", read_only=True)
    period = serializers.CharField(read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    points = serializers.ListField(child=serializers.CharField(), read_only=True)
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()

    class Meta:
        model = Experience
        fields = [
            "id", "title", "organization", "category", "category_label",
            "started_at", "ended_at", "description",
            "period", "is_ongoing", "points", "star_count", "is_starred",
        ]
        read_only_fields = ["id"]

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Role cannot be empty.")
        return value

    def validate_organization(self, value):
        return strip_tags(value).strip()

    def validate_description(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Write at least one point that isn't only HTML tags.")
        return value

    def validate(self, attrs):
        started = attrs.get("started_at", getattr(self.instance, "started_at", None))
        ended = attrs.get("ended_at", getattr(self.instance, "ended_at", None))
        if started and ended and ended < started:
            raise serializers.ValidationError({"ended_at": "End date can't be before the start date."})
        return attrs

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return obj.starred_by.filter(pk=request.user.pk).exists()
