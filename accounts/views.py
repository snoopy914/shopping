from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView


class SignUpView(CreateView):
    """회원가입 뷰"""
    form_class = UserCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('courses:course_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # 회원가입 후 자동 로그인
        login(self.request, self.object)
        messages.success(self.request, f'{self.object.username}님, 회원가입이 완료되었습니다!')
        return response


def signup(request):
    """회원가입 함수 뷰 (클래스 뷰 대신 사용 가능)"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 회원가입 후 자동 로그인
            login(request, user)
            messages.success(request, f'{user.username}님, 회원가입이 완료되었습니다!')
            return redirect('courses:course_list')
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/signup.html', {'form': form})
