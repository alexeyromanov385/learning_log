from django.shortcuts import render, redirect,get_object_or_404
from .models import Topic, Entry
from .forms import TopicForm, EntryForm
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.db.models import Q

def check_topic_owner(topic_user, request_user):
    return topic_user == request_user
        
def index(request):
    return render(request, 'learning_logs/index.html')

@login_required
def topics(request):
    topics = Topic.objects.filter(Q(owner=request.user) | Q(public=True)).order_by('date_added')
    context = {'topics' : topics}
    return render(request, 'learning_logs/topics.html', context)

@login_required
def topic(request, topic_id):
    topic : Topic = get_object_or_404(Topic, id=topic_id)
    if not check_topic_owner(topic.owner, request.user) and not topic.public:
        raise Http404
    
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic' : topic, 'entries' : entries}
    return render(request, 'learning_logs/topic.html', context)

@login_required
def new_topic(request):
    if request.method != 'POST':
        form = TopicForm()
    else:
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_form = form.save(commit = False)
            new_form.owner = request.user
            new_form.save()
            return redirect('learning_logs:topics')
    context = {'form' : form}
    return render(request, 'learning_logs/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
    topic : Topic = get_object_or_404(Topic, id=topic_id)

    if not check_topic_owner(topic.owner, request.user):
        raise Http404  
    if request.method != 'POST':
        form = EntryForm()
    else:
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic',topic_id = topic_id)
    context = {'topic' : topic, 'form' : form}
    return render(request, 'learning_logs/new_entry.html', context)

@login_required
def edit_entry(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id)
    topic = entry.topic
    if not check_topic_owner(topic.owner, request.user):
        raise Http404
    if request.method != 'POST':
        form = EntryForm(instance=entry)
    else:
        form = EntryForm(instance=entry, data = request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id = topic.id)
    context = {'entry' : entry, 'topic' : topic, 'form' : form}
    return render(request, 'learning_logs/edit_entry.html', context)    

@login_required
def delete_entry(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id)
    topic = entry.topic
    if not check_topic_owner(topic.owner, request.user):
        raise Http404
    if request.method == "POST":
        entry.delete()
        return redirect('learning_logs:topic', topic_id = topic.id)
    context = {'entry' : entry, 'topic' : topic,}
    return render(request, 'learning_logs/topic.html', context)

@login_required
def delete_topic(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    if not check_topic_owner(topic.owner, request.user):
        raise Http404
    if request.method == "POST":
        topic.delete()
        return redirect('learning_logs:topics')
    context = {'topic' : topic}
    return render(request,'learning_logs/topics.html', context)

@login_required
def make_topic_public(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    if not check_topic_owner(topic.owner, request.user):
        raise Http404
    topic.public = not topic.public
    topic.save()  
    return redirect('learning_logs:topic', topic_id=topic_id)