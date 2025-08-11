# core/views/auth_extra.py
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView
from core.forms import PasswordResetConValidacionForm

class PasswordResetViewWithEcho(PasswordResetView):
    template_name = 'usuario/password_reset.html'
    email_template_name = 'usuario/email/password_reset_email.txt'
    subject_template_name = 'usuario/email/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    from_email = settings.DEFAULT_FROM_EMAIL
    form_class = PasswordResetConValidacionForm

    def form_valid(self, form):
        # Solo se ejecuta si el correo EXISTE (porque el form valida)
        self.request.session['pr_email'] = form.cleaned_data.get('email')
        return super().form_valid(form)

class PasswordResetDoneViewWithEcho(PasswordResetDoneView):
    template_name = 'usuario/password_reset_sent.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Lo mostramos una vez y lo sacamos de sesión
        ctx['pr_email'] = self.request.session.pop('pr_email', None)
        return ctx