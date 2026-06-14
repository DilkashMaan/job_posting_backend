from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from collections import Counter

from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Job
from .serializers import (
    JobListSerializer,
    JobDetailSerializer,
    JobCreateUpdateSerializer,
)


class JobViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = Job.objects.select_related("user").all()

    def get_queryset(self):
        queryset = Job.objects.select_related(
            "user"
        ).order_by("-created_at")

        search = self.request.query_params.get("search")
        status_filter = self.request.query_params.get("status")

        if search:
            queryset = queryset.filter(
                title__icontains=search
            )

        if status_filter:
            queryset = queryset.filter(
                status__contains=[status_filter]
            )

        return queryset

    def get_serializer_class(self):

        if self.action == "list":
            return JobListSerializer

        if self.action == "retrieve":
            return JobDetailSerializer

        if self.action in [
            "create",
            "update",
            "partial_update"
        ]:
            return JobCreateUpdateSerializer

        return JobDetailSerializer

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )

    @action(detail=False, methods=["get"])
    def my_posts(self, request):

        jobs = Job.objects.filter(
            user=request.user
        ).order_by("-created_at")

        serializer = JobListSerializer(
            jobs,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):

        job = self.get_object()

        if job.user != request.user:
            return Response(
                {
                    "error": "You can only duplicate your own jobs."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        duplicated_job = Job.objects.create(
            user=request.user,
            title=job.title,
            status=job.status,
            category=job.category,
            address=job.address,
            city=job.city,
            state=job.state,
            start_date=job.start_date,
            end_date=job.end_date,
            description=job.description,
            job_picture=job.job_picture
        )

        serializer = JobDetailSerializer(
            duplicated_job
        )

        return Response(
            {
                "message": "Job duplicated successfully",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    @action(detail=False, methods=["get"])
    def analytics(self, request):

        jobs = Job.objects.all()

        status_counter = Counter()
        city_counter = Counter()
        state_counter = Counter()

        for job in jobs:

            if job.status:
                for item in job.status:
                    status_counter[item] += 1

            if job.city:
                city_counter[job.city] += 1

            if job.state:
                state_counter[job.state] += 1

        return Response(
            {
                "total_jobs": jobs.count(),

                "status": [
                    {
                        "name": key,
                        "value": value
                    }
                    for key, value in status_counter.items()
                ],

                "city": [
                    {
                        "name": key,
                        "value": value
                    }
                    for key, value in city_counter.items()
                ],

                "state": [
                    {
                        "name": key,
                        "value": value
                    }
                    for key, value in state_counter.items()
                ],
            }
        )


