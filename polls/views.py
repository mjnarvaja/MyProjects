from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required 
from django.views.generic import View
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from django.views.generic.base import TemplateView, TemplateResponseMixin, ContextMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User

from .models import Question, Choice, Comment
from polls.forms import CommentForm, Comments


class LoginRequiredMixin(object):
	'''@classmethod
	def as_view(cls, **kwargs):
		view = super(LoginRequiredMixin, cls).as_view(**kwargs)
		return login_required(view)'''
	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class HomePageView(TemplateView):

	template_name = "polls/home.html"

	def get_context_data(self, *args, **kwargs):
		context = super(HomePageView, self).get_context_data(*args, **kwargs)
		context["title"] = "Home page"
		return context


class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by('-pub_date')[:5]


class DetailView(LoginRequiredMixin, generic.DetailView):
    # form = CommentForm
    # template_name = 'polls/detail.html'
    # error = None
    # def post(self, request, *args, **kwargs):
    #     print(self.request.user.id)
    #     if form.is_valid():
    #     	form.save()

    #     return HttpResponseRedirect("/polls/")


    #     if form.errors:
    #     	errors = form.errors


    #     template_name = "polls/detail.html"
    #     context = {"form": form, "errors": errors}
    #   return render(request, template_name, context)
    form_class = Comments()
    model = Question
    template_name = 'polls/detail.html'

    def get_context_data(self, **kwargs):
        print(kwargs['object'])
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(
            question=Question.objects.get(question_text=kwargs['object'])
        )
        context['form'] = Comments()
        return context

    def post(self, request, *args, **kwargs):
        print(self.request.user.id)
        if request.POST.get('comment'):
            self.object = self.get_object()
            new = Comment(
                content=request.POST.get('comment'),
                question=Question.objects.get(pk=kwargs['pk']),
                userProfile=User.objects.get(pk=self.request.user.id),
                date = timezone.now())
            new.save()
            return HttpResponseRedirect(self.request.path_info)
        else:
            question = get_object_or_404(Question, pk=kwargs['pk'])
            try:
                selected_choice = question.choice_set.get(
                    pk=request.POST['choice'])
            except (KeyError, Choice.DoesNotExist):
                return render(request, 'polls/detail.html', {
                    'question': question,
                    'error_message': "You didn't select a choice.",
                })
            else:
                selected_choice.votes += 1
                selected_choice.save()
                return HttpResponseRedirect(reverse(
                    'polls:results', args=(kwargs['pk'],)))
        

class ResultsView(LoginRequiredMixin, generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


def vote(LoginRequiredMixin, request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyErrors, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))