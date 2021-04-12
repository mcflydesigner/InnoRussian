from django.conf import settings

def project_name(request, *args, **kwargs):
    """
        Custom context processor to provide the name of the project
        in the context for some templates
    """
    return {
        'PROJECT_NAME': settings.PROJECT_NAME
    }