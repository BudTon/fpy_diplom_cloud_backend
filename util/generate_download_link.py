from django.urls import reverse


def generate_download_link(request, uploaded_file):
    internal_url_view = reverse(
        "download_file_link", args=[uploaded_file.short_hash, "view"]
    )
    view_url = request.build_absolute_uri(internal_url_view)
    internal_url_download = reverse(
        "download_file_link", args=[uploaded_file.short_hash, "download"]
    )
    download_url = request.build_absolute_uri(internal_url_download)
    full_url = {"view": view_url, "download": download_url}
    return full_url
