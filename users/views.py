import jwt, datetime

from django.views import View
from django.http  import JsonResponse
from django.conf  import settings

from users.models import User
from users.kakao  import KakaoAPI

from cores.decorator    import login_authorization

class KakaoLoginView(View):
    def get(self, request):
        try:
            acces_token = request.headers.get('Authorization')
            kakao_user  = KakaoAPI(acces_token).kakao_user()

            if kakao_user.get('code') == -401: 
                return JsonResponse({'message' : 'Invalid token'}, status=401)

            user, state = User.objects.get_or_create(
                social_id     = kakao_user['id'],
                email         = kakao_user['kakao_account']['email'],
                nickname      = kakao_user['properties']['nickname'],
                defaults={'profile_image': kakao_user['kakao_account']['profile'].get('profile_image_url', None)}
            )

            if not state:
                user.profile_image = kakao_user['kakao_account']['profile'].get('profile_image_url', None)
                user.save()

            status = 200 if not state else 201
            
            payload={
                'user_id': user.id,
                'exp'          : datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }

            new_token = jwt.encode(payload, settings.SECRET_KEY, settings.ALGORITHM)

            return JsonResponse({'new_token' : new_token}, status = status)
            
        except KeyError: 
            return JsonResponse({'message' : 'Key error'}, status=400)      

class UserInfomation(View):
    @login_authorization
    def get(self,request):
        user = request.user
        
        user_info = {
                "nickname" : user.nickname,
                "email"    : user.email,
                "point"    : user.point,
                "profile_image" : user.profile_image,
            }
            
        return JsonResponse({'user_info' : user_info}, status = 200)
