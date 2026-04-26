from .models import UserProfile

def user_profile(request):
    if request.user.is_authenticated:
        profile = UserProfile.objects.filter(user=request.user).first()
        return {'user_profile': profile}
    return {'user_profile': None}
