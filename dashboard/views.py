from email import message
from django.shortcuts import render,redirect
from . forms import *
from django.contrib import messages
from django.views import generic
from youtubesearchpython import VideosSearch
import requests
import wikipedia
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required
def home(request):
    return render(request,'dashboard/home.html')

@login_required
def notes(request):
    if request.method == "POST":
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user=request.user,title=request.POST['title'],description=request.POST['description'])
            notes.save()
            messages.success(request,f"Notes added {request.user.username} successfully!!")
    else:
        form = NotesForm()
    notes = Notes.objects.filter(user=request.user)
    content = {'notes':notes,'form':form}
    return render(request,'dashboard/notes.html',content)

@login_required
def delete_note(request,id=None):
    Notes.objects.get(id=id).delete()
    return redirect("notes")

class notesDetail(generic.DetailView):
    model = Notes


@login_required
def homeWork(request):
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == "on":
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            homeworks = Homework(
                user = request.user,
                title = request.POST['title'],
                subject = request.POST['subject'],
                description = request.POST['description'],
                due = request.POST['due'],
                is_finished = finished
            )
            homeworks.save()
            messages.success(request,f'Homework Added by {request.user.username} successfully!!')
    else:
        form = HomeworkForm()
    homework = Homework.objects.filter(user=request.user)
    if len(homework)==0:
        homework_done = True
    else:
        homework_done=False
    content = {'homeworks':homework,'homeworks_done':homework_done,'form':form}
    return render(request,'dashboard/homework.html',content)

@login_required
def update_homework(request,pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    return redirect("homework")

@login_required
def delete_homework(request,pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect("homework")

@login_required
def youtube(request):
    if request.method == "POST":
        form = dashboardCommonForm(request.POST)
        text = request.POST['text']
        video = VideosSearch(text,limit=10)
        result_list =[]
        for i in video.result()['result']:
            result_dict = {
                'input':text,
                'title':i['title'],
                'duration':i['duration'],
                'thumbnails':i['thumbnails'][0]['url'],
                'channel':i['channel']['name'],
                'link':i['link'],
                'viewcount':i['viewCount']['short'],
                'published':i['publishedTime']
            }
            desc = ''
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc += j['text']
            result_dict['description']=desc
            result_list.append(result_dict)
            content = {
                'form':form,
                'result':result_list
            }
        return render(request,'dashboard/youtube.html',content)
    else:
        form = dashboardCommonForm()
    content = {"form":form}
    return render(request,"dashboard/youtube.html",content)

@login_required
def todo(request):
    if request.method == "POST":
        form = ToDoForm(request.POST)
        if form.is_valid:
            try:
                finished = request.POST['is_finished']
                if finished == "on":
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            tododata = ToDo(
                user = request.user,
                title = request.POST['title'],
                is_finished = finished
            )
            tododata.save()
            messages.success(request,f'Your ToDo Added {request.user.username} Successfully!!')
    else:
        form = ToDoForm()
    todo = ToDo.objects.filter(user=request.user)
    if len(todo)==0:
        alltodo_done = True
    else:
        alltodo_done = False
    content = {
        "todo":todo,
        'form':form,
        'alltododone':alltodo_done
    }
    return render(request,'dashboard/todo.html',content)

@login_required
def update_todo(request,pk=None):
    todo = ToDo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True
    todo.save()
    return redirect("todo")

@login_required
def delete_todo(request,pk=None):
    ToDo.objects.get(id=pk).delete()
    return redirect('todo')

@login_required   
def books(request):
    if request.method == "POST":
        form = dashboardCommonForm(request.POST)
        text = request.POST['text']
        # video = VideosSearch(text,limit=10)
        url = "https://www.googleapis.com/books/v1/volumes?q="+text
        r = requests.get(url)
        answer = r.json()
        result_list =[]
        for i in range(10):
            result_dict = {
                'title':answer['items'][i]['volumeInfo']['title'],
                'subtitle':answer['items'][i]['volumeInfo'].get('subtitle'),
                'description':answer['items'][i]['volumeInfo'].get('description'),
                'pageCount':answer['items'][i]['volumeInfo'].get('pageCount'),
                'categories':answer['items'][i]['volumeInfo'].get('categories'),
                'pageRating':answer['items'][i]['volumeInfo'].get('pageRating'),
                'imageLinks':answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
                'preview':answer['items'][i]['volumeInfo'].get('previewLink')
            }
            result_list.append(result_dict)
            content = {
                'form':form,
                'result':result_list
            }
        return render(request,'dashboard/books.html',content)
    else:
        form = dashboardCommonForm()
    content = {"form":form}
    return render(request,"dashboard/books.html",content)

@login_required
def dictionary(request):
    if request.method == "POST":
        form = dashboardCommonForm(request.POST)
        text = request.POST['text']
        # video = VideosSearch(text,limit=10)
        url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/"+text
        r = requests.get(url)
        answer = r.json()
        try:
            phonetics = answer[0]['phonetics'][0]['text']
            audio = answer[0]['phonetics'][0]['audio']
            definition = answer[0]['meanings'][0]['definitions'][0]['definition']
            example = answer[0]['meanings'][0]['definitions'][0]['example']
            synonyms = answer[0]['meanings'][0]['definitions'][0]['synonyms']
            # print(synonyms)
            content={
                "form":form,
                "input":text,
                "phonetics":phonetics,
                "audio":audio,
                "definition":definition,
                "example":example,
                "synonyms":synonyms
            }
        except:
            content={
                "form":form,
                "input":''
            }
        return render(request,'dashboard/dictionary.html',content)
    else:
        form = dashboardCommonForm()
    content = {"form":form}
    return render(request,"dashboard/dictionary.html",content)

@login_required    
def wikepedia(request):
    if request.method=="POST":
        text = request.POST['text']
        form =dashboardCommonForm(request.POST)
        search = wikipedia.page(text)
        print(search)
        content = {
            'form':form,
            'title':search.title,
            'link':search.url,
            'details':search.summary
        }
        return render(request,'dashboard/wiki.html',content)
    else:
        form = dashboardCommonForm()
        content={'form':form}
    return render(request,'dashboard/wiki.html',content)

def conversion(request):
    if request.method=="POST":
        form = MeasurementsForm(request.POST)
        if request.POST.get('measurements')=="length":
            measure_form = ConversionLengthForm()
            content={
                "form":form,
                "m_form":measure_form,
                "input":True
            }
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer=''
                if input and int(input)>=0:
                    if first == "yard" and second == "foot":
                        answer = f'{input} yard ={int(input)*3} foot'
                    if first == "foot" and second == "yard":
                        answer = f'{input} yard ={int(input)/3} foot'
                content = {
                    "form":form,
                    "m_form":measure_form,
                    "input":True,
                    "answer":answer
                }
        if request.POST.get('measurements')=="mass":
            measure_form = ConversionMassForm()
            content={
                "form":form,
                "m_form":measure_form,
                "input":True
            }
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer=''
                if input and int(input)>=0:
                    if first == "pound" and second == "kilogram":
                        answer = f'{input} pound ={int(input)*0.453592} kilogram'
                    if first == "kilogram" and second == "pound":
                        answer = f'{input} kilogram ={int(input)*2.2062} pound'
                content = {
                    "form":form,
                    "m_form":measure_form,
                    "input":True,
                    "answer":answer
                }
    else:
        form=MeasurementsForm()
    content = {
        'form':form,
        'input':False
    }
    return render(request,'dashboard/conversion.html',content)

def userRegistration(request):
    if request.method=="POST":
        form = UserRegistrationForm(request.POST)
        print(form)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f'Register {username} successfully!')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    content={
        "form":form
    }
    return render(request,'dashboard/register.html',content)

@login_required
def profile(request):
    homework = Homework.objects.filter(is_finished=False,user=request.user)
    todos = ToDo.objects.filter(is_finished=False,user=request.user)
    if len(homework)==0:
        complete_homework = True
    else:
        complete_homework = False
    if len(todos)==0:
        complete_todo = True
    else:
        complete_todo = False
    content={
        'homework':homework,
        'todo':todos,
        'complete_homework':complete_homework,
        'complete_todo':complete_todo
    }
    return render(request,'dashboard/profile.html',content)