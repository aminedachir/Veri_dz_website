from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Publication


def is_admin(user):
    return user.is_authenticated and user.is_staff


# ── PUBLIC VIEWS ──────────────────────────────────────────

def publication_list(request):
    pub_type = request.GET.get('type', '')
    publications = Publication.objects.filter(is_published=True)
    if pub_type in ['image', 'video']:
        publications = publications.filter(pub_type=pub_type)
    return render(request, 'publications/list.html', {
        'publications': publications,
        'active_type': pub_type,
    })


def publication_detail(request, pk):
    pub = get_object_or_404(Publication, pk=pk, is_published=True)
    pub.views_count += 1
    pub.save(update_fields=['views_count'])
    return render(request, 'publications/detail.html', {'publication': pub})


# ── ADMIN VIEWS ───────────────────────────────────────────

@login_required
@user_passes_test(is_admin)
def publication_create(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        pub_type = request.POST.get('pub_type', 'image')
        is_published = request.POST.get('is_published') == 'on'

        if not title:
            messages.error(request, 'العنوان مطلوب.')
            return render(request, 'publications/form.html')

        pub = Publication(
            title=title,
            description=description,
            pub_type=pub_type,
            author=request.user,
            is_published=is_published,
        )

        if pub_type == 'image' and request.FILES.get('image'):
            pub.image = request.FILES['image']
        elif pub_type == 'video' and request.FILES.get('video'):
            pub.video = request.FILES['video']
            if request.FILES.get('thumbnail'):
                pub.thumbnail = request.FILES['thumbnail']

        pub.save()
        messages.success(request, 'تم نشر المحتوى بنجاح!')
        return redirect('publications:detail', pk=pub.pk)

    return render(request, 'publications/form.html')


@login_required
@user_passes_test(is_admin)
def publication_edit(request, pk):
    pub = get_object_or_404(Publication, pk=pk)

    if request.method == 'POST':
        pub.title = request.POST.get('title', '').strip()
        pub.description = request.POST.get('description', '').strip()
        pub.is_published = request.POST.get('is_published') == 'on'

        if request.FILES.get('image'):
            pub.image = request.FILES['image']
        if request.FILES.get('video'):
            pub.video = request.FILES['video']
        if request.FILES.get('thumbnail'):
            pub.thumbnail = request.FILES['thumbnail']

        pub.save()
        messages.success(request, 'تم تحديث المنشور بنجاح!')
        return redirect('publications:detail', pk=pub.pk)

    return render(request, 'publications/form.html', {'pub': pub})


@login_required
@user_passes_test(is_admin)
def publication_delete(request, pk):
    pub = get_object_or_404(Publication, pk=pk)
    if request.method == 'POST':
        pub.delete()
        messages.success(request, 'تم حذف المنشور.')
    return redirect('publications:list')


@login_required
@user_passes_test(is_admin)
def publication_manage(request):
    """Admin-only page showing all publications with management options."""
    publications = Publication.objects.all()
    return render(request, 'publications/manage.html', {'publications': publications})
