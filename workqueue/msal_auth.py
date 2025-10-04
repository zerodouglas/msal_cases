
import uuid
from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
import msal

User = get_user_model()

SESSION_STATE = "msal_state"
SESSION_TOKEN_CACHE = "msal_token_cache"


def _build_msal_app(request):
    cache = msal.SerializableTokenCache()
    data = request.session.get(SESSION_TOKEN_CACHE)
    if data:
        cache.deserialize(data)
    app = msal.ConfidentialClientApplication(
        client_id=settings.AZURE_AD_CLIENT_ID,
        client_credential=settings.AZURE_AD_CLIENT_SECRET,
        authority=settings.AZURE_AD_AUTHORITY,
        token_cache=cache,
    )
    request._msal_cache = cache
    return app


def _save_cache(request):
    if hasattr(request, "_msal_cache") and request._msal_cache.has_state_changed:
        request.session[SESSION_TOKEN_CACHE] = request._msal_cache.serialize()


def login_begin(request):
    state = str(uuid.uuid4())
    request.session[SESSION_STATE] = state
    app = _build_msal_app(request)
    auth_url = app.get_authorization_request_url(
        scopes=settings.AZURE_AD_SCOPES,
        state=state,
        redirect_uri=request.build_absolute_uri(settings.AZURE_AD_REDIRECT_PATH),
        prompt="select_account",
    )
    return HttpResponseRedirect(auth_url)


def login_callback(request):
    if request.GET.get("state") != request.session.get(SESSION_STATE):
        return redirect("/login/")

    app = _build_msal_app(request)
    result = app.acquire_token_by_authorization_code(
        request.GET.get("code"),
        scopes=settings.AZURE_AD_SCOPES,
        redirect_uri=request.build_absolute_uri(settings.AZURE_AD_REDIRECT_PATH),
    )
    _save_cache(request)

    if "id_token_claims" not in result:
        return redirect("/login/")

    claims = result["id_token_claims"]
    upn = claims.get("preferred_username") or claims.get("upn")
    name = claims.get("name") or upn

    user, _ = User.objects.get_or_create(username=upn, defaults={"first_name": name})
    login(request, user)
    return redirect("/")


def logout_view(request):
    logout(request)
    return redirect("/login/")
