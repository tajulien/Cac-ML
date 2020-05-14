from django.http import HttpResponse
from django.shortcuts import render, redirect
import apimkd

def redi_index(request):
    return redirect("home", days_range=800, name_action='Lvmh')

# Create your views here.
def dashboard(request,days_range=360, name_action="Lvmh"):
    #print(name_action)
    values, days, mma10, mma20, mma50, mma100, mma200, bol_inf, bol_sup, plage_max = apimkd.starting(plage=days_range, action_studied=name_action)
    title = "Test de titre"
    page_label = {7: "Semaine", 30: "Mois", 365: "Année", plage_max: "Max"}.get(days_range, "Durée Personnalisée")
    # return HttpResponse("<h1>Bonjour Tout le monde </h1>")
    return render(request,"cac/index.html", context={"title": title,"name_action": name_action, "data": values,"days_labels": days, "page_label":page_label, "mma10":mma10,"mma20": mma20,"mma50": mma50, "mma100":mma100, "mma200": mma200, "bol_inf": bol_inf, "bol_sup": bol_sup, "nb_jour": plage_max})