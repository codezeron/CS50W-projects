from django.shortcuts import render
import random
from . import util
from markdown2 import Markdown

def convert_md_to_html(title):
    content = util.get_entry(title)
    markdowner = Markdown()
    if content == None:
        return None
    else:
        return markdowner.convert(content)

def index(request):
    entries = util.list_entries()
    css_file = util.get_entry("css")
    coffee = util.get_entry("coffee")
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    html_content = convert_md_to_html(title)
    if html_content == None:
        return render(request, "encyclopedia/error.html",{
            "message": "This entry does not exist"
        })
    else:
        return render(request, "encyclopedia/entry.html",{
            "title": title,
            "content": html_content
        })
def search(request):
    if request.method == "POST":
        entry_search = request.POST['q']
        html_content = convert_md_to_html(entry_search)
        if html_content is not None:
            return render(request, "encyclopedia/entry.html",{
            "title": entry_search,
            "content": html_content
        })
        else:
            allEntries = util.list_entries()
            recomendations = []
            for entries in allEntries:
                if entry_search.lower() in entries.lower():
                    recomendations.append(entries)
            return render(request, "encyclopedia/search.html", {
                "recomendation" : recomendations
            })
def new_page(request):
    if request.method == "GET":
        return render(request, "encyclopedia/new.html")
    else:
        title = request.POST['title']
        content = request.POST['content']
        titleExists = util.get_entry(title)
        if titleExists is not None:
            return render(request, "encyclopedia/error.html", {
                "message": "This title already exists"
            })
        else:
            util.save_entry(title, content)
            html_content = convert_md_to_html(title)
            return render(request, "encyclopedia/entry.html", {
                "title": title,
                "content": html_content
            })

def edit(request):
    if request.method == "POST":
        title = request.POST['entry_title']
        content = util.get_entry(title)
        return render(request, "encyclopedia/edit.html",{
            "title": title,
            "content": content
        })
def save_edit(request):
     if request.method == "POST":
        title = request.POST['title']
        content = request.POST['content'] 
        util.save_entry(title, content)
        html_content = convert_md_to_html(title)
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": html_content
        })
def R_page(request):
    allEntris = util.list_entries()
    rand_entry = random.choice(allEntris)
    html_content = convert_md_to_html(rand_entry)
    return render(request, "encyclopedia/entry.html", {
            "title": rand_entry,
            "content": html_content
        })