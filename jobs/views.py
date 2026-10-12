"""Handle HTTP requests without running collection inline. / 수집을 직접 실행하지 않고 HTTP 요청을 처리합니다."""

from uuid import UUID
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
from job_pipeline.records import CATEGORIES, STATUSES
from .forms import CollectionForm
from .models import CollectionJob, JobAnalysis

@login_required
@require_GET
def dashboard(request: HttpRequest) -> HttpResponse:
    """Read DB results for the web; do not call ATS or Ollama. / 웹에서는 DB 결과를 읽고 ATS·Ollama를 호출하지 않습니다."""
    category = request.GET.get("category", "visa_sponsorship")
    status = request.GET.get("status", "")
    if category not in CATEGORIES or (status and status not in STATUSES):
        return HttpResponse("Invalid classification filter", status=400)
    analyses = JobAnalysis.objects.all()
    if status:
        analyses = analyses.filter(**{f"record__analysis__{category}_status": status})
    cards = [{
        "job": item,
        "status": item.record["analysis"][f"{category}_status"],
        "evidence": item.record["analysis"][f"{category}_evidence"],
    } for item in analyses[:100]]
    return render(request, "jobs/dashboard.html", {
        "cards": cards, "category": category, "status": status,
        "categories": CATEGORIES, "statuses": STATUSES,
        "total": analyses.count(), "form": CollectionForm(),
        "runs": CollectionJob.objects.filter(owner=request.user).order_by("-created_at")[:10],
    })


@login_required
@require_POST
def create_collection(request: HttpRequest) -> JsonResponse:
    """Enqueue a DB job and immediately return its ID. / DB에 작업을 등록하고 ID를 즉시 반환합니다."""
    form = CollectionForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors.get_json_data()}, status=400)
    job = CollectionJob.objects.create(owner=request.user, **form.cleaned_data)
    return JsonResponse({
        "job_id": str(job.pk), "status": job.status,
        "status_url": reverse("jobs:collection_status", args=[job.pk]),
    }, status=202)


@login_required
@require_GET
def collection_status(request: HttpRequest, job_id: UUID) -> JsonResponse:
    """Read worker status from the DB. / DB에서 작업자 상태를 조회합니다."""
    job = get_object_or_404(CollectionJob, pk=job_id, owner=request.user)
    return JsonResponse({"job_id": str(job.pk), "status": job.status, "error": job.error})
