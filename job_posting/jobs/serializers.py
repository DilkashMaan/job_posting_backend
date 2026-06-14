from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Job

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
        ]


class JobCreateUpdateSerializer(serializers.ModelSerializer):
    ALLOWED_STATUSES = [
        "Draft",
        "Requested",
        "Posted",
        "Filled",
    ]

    ALLOWED_CATEGORIES = [
        "Full-time",
        "Part-time",
        "Intern",
    ]

    class Meta:
        model = Job
        exclude = [
            "user",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):

        start_date = attrs.get(
            "start_date",
            getattr(self.instance, "start_date", None)
        )

        end_date = attrs.get(
            "end_date",
            getattr(self.instance, "end_date", None)
        )

        if (
            start_date
            and end_date
            and end_date < start_date
        ):
            raise serializers.ValidationError(
                {
                    "end_date": (
                        "End date cannot be before start date."
                    )
                }
            )

        return attrs

    def validate_status(self, value):

        invalid = [
            item
            for item in value
            if item not in self.ALLOWED_STATUSES
        ]

        if invalid:
            raise serializers.ValidationError(
                f"Invalid status values: {invalid}"
            )

        return value

    def validate_category(self, value):

        invalid = [
            item
            for item in value
            if item not in self.ALLOWED_CATEGORIES
        ]

        if invalid:
            raise serializers.ValidationError(
                f"Invalid category values: {invalid}"
            )

        return value


class JobListSerializer(serializers.ModelSerializer):
    posted_by = serializers.CharField(
        source="user.username",
        read_only=True
    )

    job_picture = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "status",
            "category",
            "city",
            "state",
            "description",
            "job_picture",
            "posted_by",
            "created_at",
        ]

    def get_job_picture(self, obj):
        request = self.context.get("request")

        if obj.job_picture:
            filename = obj.job_picture.name.split("/")[-1]
            return request.build_absolute_uri(
                f"/jobs/job_picture/{filename}"
            )

        return None



class JobDetailSerializer(serializers.ModelSerializer):
    posted_by = UserSerializer(
        source="user",
        read_only=True
    )

    class Meta:
        model = Job
        fields = "__all__"