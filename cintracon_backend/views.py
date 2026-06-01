import os
from django.http import HttpResponse, HttpResponseNotFound


def home(request):
    return HttpResponse(
        "Welcome to the CINTRACON Backend! "
        "This backend supplies data to the CINTRACON Frontend through REST API."
    )


# ─── OG Meta helpers ─────────────────────────────────────────────────────────

def _og_html(title, description, image, redirect_url):
    title = (title or '').replace('"', '&quot;')
    desc = (description or '')[:150].replace('"', '&quot;')
    image = image or ''
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:image" content="{image}" />
  <meta property="og:url" content="{redirect_url}" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="CINTRACON" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{title}" />
  <meta name="twitter:description" content="{desc}" />
  <meta name="twitter:image" content="{image}" />
  <meta http-equiv="refresh" content="0; url={redirect_url}" />
  <title>{title}</title>
</head>
<body>Redirecting to <a href="{redirect_url}">CINTRACON</a>...</body>
</html>"""


def _frontend_url():
    return os.getenv('FRONTEND_URL', 'http://localhost:5173')


# ─── Share meta views (no auth — crawled by Facebook/WhatsApp/Twitter) ───────

def share_post_meta(request, post_id):
    from home.models import Post
    redirect_url = f"{_frontend_url()}/post/{post_id}"
    try:
        post = Post.objects.select_related('user').get(id=post_id)
        title = f"{post.user.full_name} on CINTRACON"
        description = post.caption or ''
        image = str(post.post_image) if post.post_image else ''
        return HttpResponse(_og_html(title, description, image, redirect_url), content_type='text/html')
    except Post.DoesNotExist:
        return HttpResponseNotFound('<h1>Post not found</h1>')


def share_note_meta(request, note_id):
    from notesharing.models import Note
    redirect_url = f"{_frontend_url()}/note/{note_id}"
    try:
        note = Note.objects.select_related('user').get(id=note_id)
        title = f"{note.title} - CINTRACON Notes"
        description = note.description or ''
        image = ''
        return HttpResponse(_og_html(title, description, image, redirect_url), content_type='text/html')
    except Note.DoesNotExist:
        return HttpResponseNotFound('<h1>Note not found</h1>')


def share_job_meta(request, job_id):
    from jobopportunities.models import JobPost
    redirect_url = f"{_frontend_url()}/job/{job_id}"
    try:
        job = JobPost.objects.get(id=job_id)
        title = f"{job.title} at {job.company_name} - CINTRACON Jobs"
        description = job.description or ''
        image = str(job.job_post_image) if job.job_post_image else ''
        return HttpResponse(_og_html(title, description, image, redirect_url), content_type='text/html')
    except JobPost.DoesNotExist:
        return HttpResponseNotFound('<h1>Job not found</h1>')


def share_event_meta(request, event_id):
    from upcomingevents.models import Event
    redirect_url = f"{_frontend_url()}/event/{event_id}"
    try:
        event = Event.objects.get(id=event_id)
        title = f"{event.title} - CINTRACON Events"
        description = event.description or ''
        image = str(event.event_image) if event.event_image else ''
        return HttpResponse(_og_html(title, description, image, redirect_url), content_type='text/html')
    except Event.DoesNotExist:
        return HttpResponseNotFound('<h1>Event not found</h1>')
