# forked from https://github.com/metakermit/django-spa/blob/master/spa/middleware.py

import os

from django.conf import settings
from django.urls import is_valid_path
from whitenoise.middleware import WhiteNoiseMiddleware


class WhiteNoiseSPAMiddleware(WhiteNoiseMiddleware):
    """
    Adds support for serving a single-page app (SPA)
    with frontend routing on /
    """

    index_name = os.path.join(settings.STATIC_URL, "index.html")

    def __call__(self, request):
        # First try to serve the static files (on /static/ and on /)
        # which is relatively fast as files are stored in a self.files dict
        if self.autorefresh:  # debug mode
            static_file = self.find_file(request.path_info)
        else:  # from the collected static files
            static_file = self.files.get(request.path_info)

        if static_file is not None:
            return self.serve(static_file, request)
        else:
            # if no file was found there are two options:

            # 1) the file is in one of the Django urls
            # (e.g. a template or the Djangoadmin)
            # so we'll let Django handle this
            # (just return and let the normal middleware take its course)
            urlconf = getattr(request, "urlconf", None)
            if is_valid_path(request.path_info, urlconf):
                return self.get_response(request)
            if (
                settings.APPEND_SLASH
                and not request.path_info.endswith("/")
                and is_valid_path("%s/" % request.path_info, urlconf)
            ):
                return self.get_response(request)

            # 2) the url is handled by frontend routing
            # redirect all unknown files to the SPA root
            try:
                return self.serve(self.spa_root, request)
            except AttributeError:  # no SPA page stored yet
                self.spa_root = self.find_file("/")
                if self.spa_root:
                    return self.serve(self.spa_root, request)
                # TODO: else return a Django 404 (maybe?)

    def update_files_dictionary(self, *args):
        super(WhiteNoiseSPAMiddleware, self).update_files_dictionary(*args)
        relative_index_name = self.index_name.strip("/")
        index_page_suffix = "/" + relative_index_name
        index_name_length = len(relative_index_name)
        static_prefix_length = len(settings.STATIC_URL) - 1
        directory_indexes = {}
        for url, static_file in self.files.items():
            if url.endswith(index_page_suffix):
                # For each index file found, add a corresponding URL->content
                # mapping for the file's parent directory,
                # so that the index page is served for
                # the bare directory URL ending in '/'.
                parent_directory_url = url[:-index_name_length]
                directory_indexes[parent_directory_url] = static_file
                # remember the root page for any other unrecognised files
                # to be frontend-routed
                self.spa_root = static_file
            else:
                # also serve static files on /
                # e.g. when /my/file.png is requested, serve /static/my/file.png
                directory_indexes[url[static_prefix_length:]] = static_file
        self.files.update(directory_indexes)

    def find_file(self, url):
        # In debug mode, find_file() is used to serve files directly
        # from the filesystem instead of using the list in `self.files`,
        # we append the index filename so that will be served if present.
        # TODO: handle the trailing slash for the case of e.g. /welcome/
        # (should be frontend-routed)
        if url.endswith("/"):
            url += self.index_name.strip("/")
            self.spa_root = super(WhiteNoiseSPAMiddleware, self).find_file(url)
            return self.spa_root
        else:
            # also serve static files on /
            # e.g. when /my/file.png is requested, serve /static/my/file.png
            if not url.startswith(settings.STATIC_URL):
                url = os.path.join(settings.STATIC_URL, url[1:])
            return super(WhiteNoiseSPAMiddleware, self).find_file(url)
