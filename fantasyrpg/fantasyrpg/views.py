from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from fantasyrpg.forms import UserForm, HeroForm, EquipmentForm, BossForm, BossEquipmentForm, UpdateEquipmentForm, \
    UpdateBossForm, AddEquipmentForm, AddBossForm, DeleteEquipmentForm, DeleteBossForm
from fantasyrpg.models import MyUser, Hero, BossEquipment, Equipment, Boss
from fantasyrpg.jsonSerialize import serialize
from django.contrib import messages

import json
import random

"""In questa view il team ha deciso di occuparsi esclusivamente della parte di registrazione dell'utente che sarà organi
zzata con un form di inserimento dati creato in forms.py e un radioselect per scegliere il tipo di utenza che si 
gradisce utilizzare per iniziare l'approccio al programma, attraverso i controlli del form la views gestisce non 
presenta controlli sui dati forniti che hanno già passato le barriere del form"""


def signup(request):
    if request.user.is_authenticated:  # Un pre controllo dell'identità di chi accede alla pagina
        if request.user.is_staff:  # Se si sei un amministratore del database allora:
            return HttpResponseRedirect(reverse('admin:index'))
        else:
            return redirect('index')  # Se sei un utente normale non loggato allora accedi alla pagina index
    else:
        if request.method == 'POST':  # Se la richiesta del form è di tipo post esegui il codice diversamente riproponi
            user_form = UserForm(request.POST)  # Salviamo i dati nel form nella variabile

            if user_form.is_valid():  # Se i dati ottenuti sono validi creiamo una riga nel nostro database
                myuser = MyUser(first_name=user_form.cleaned_data['first_name'],  # con i dati ottenuti
                                last_name=user_form.cleaned_data['last_name'],
                                username=user_form.cleaned_data['username'],
                                password=user_form.cleaned_data['password'],
                                usertype=user_form.cleaned_data['user_type'],
                                )

                myuser.set_password(user_form.cleaned_data['password'])
                myuser.save()

                # In base al tipo di use scelto l'utente verrà rimandato alle rispettive paging d'accesso con conferma
                if myuser.usertype == 'USER':
                    messages.success(request, 'L\'utente ' + myuser.username + ' è stato creato correttamente.')
                    return redirect('loginPage')

                elif myuser.usertype == 'GAMEDEVELOPER':
                    messages.success(request, 'Il Gamedeveloper ' + myuser.username + ' è stato creato correttamente.')
                    return redirect('loginPage')
        else:
            user_form = UserForm()

    return render(request, 'signup.html', {"form": user_form})


""" Questa views si occupa della pagina di login attraverso due input per username e password se la convalida non viene
effettuata in modo corretto viene mostrato un messaggio di errore e viene riproposto il form nel template"""


def loginPage(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return HttpResponseRedirect(reverse('admin:index'))
        else:
            return redirect('index')
    else:
        if request.method == 'POST':  # Se la richiesta è di tipo post allora autentica lo user con i dati di input
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:  # Se lo user non è nullo
                if user.is_active:
                    request.session.set_expiry(86400)  # La sua sessione di autenticazione sarà on finchè farà il loguot
                    login(request, user)

                    if user.usertype == 'USER' and user.protagonist is None:  # Se chi logga non ha ancora un eroe
                        return redirect('first_creation_hero')                # Crea prima l'eroe nella pagina
                    elif user.usertype == 'GAMEDEVELOPER':  # Altrimenti logga nelle rispettive pagine secondo il tipo
                        return redirect('gamedev_home')
                    else:
                        return redirect('user_home')
            else:                                          # Se i dati inseriti non sono corretti presenta il messaggio
                messages.info(request, 'Username o password sbagliati')

        return render(request, 'login.html')


"""Questa view si occupa di di effettuare il logout per l'utente in sessione implementa particolari funzionalità 
ma fondamentale, viene posta in tutte le navbar delle pagine per poter eseguire l'azione da qualunque pagina l'utente
abbia necessità di farlo """


def logoutUser(request):
    logout(request)
    messages.info(request, "Utente disconnesso correttamente")
    return redirect('loginPage')


"""Questa view si occupa dei re indirizzamenti per chi conosce il sito per la prima volta si occupa appunto dell'index 
 la pagina radice del sito quella che se il sito fosse in rete verrebbe visualizzata come prima soluzione """


def index(request):  # All'interno della stessa come nelle altre pagine di accesso libero vengono eseguiti i controlli 0
    if request.user.is_authenticated:  # sul tipo di utente che prova ad accedervi
        if request.user.usertype == 'GAMEDEVELOPER':
            return redirect('gamedev_home')
        elif request.user.is_staff:
            return HttpResponseRedirect(reverse('admin:index'))
        else:
            return redirect('user_home')

    return render(request, 'index.html')


"""Nella view seguente troviamo un tag importante che ci permette di assicuraci che alla pagina possano accedere solo 
gli utenti effettivamente loggati e che la loro sessione non sia scaduta quindi non siano affettivamente attivi, 
la view in se si occupa di settare il personaggio principale dell'utente e ci permette di scegliere e settare 
attraverso un form implementato in form.py le caratteristiche dell'eroe iniziale che sono permesse di scegliere allo 
user """


@login_required(login_url='/login/')  # E' richiesto che l'utente sia loggato e in sessione
def first_creation_hero(request):  # Controlliamo il tipo di utente loggato che cerca di accedere
    if request.user.protagonist is not None or request.user.usertype == 'GAMEDEVELOPER':
        return redirect('index')  # Nell index vengono reindirizzati alle pagine permesse per il loro tipo di user
    elif request.user.is_staff:
        return HttpResponseRedirect(reverse('admin:index'))
    else:
        if request.method == 'POST':
            hero_form = HeroForm(request.POST)  # Salviamo nella variabile il form compilato corretamente

            if hero_form.is_valid():
                myhero = Hero(name=hero_form.cleaned_data['name'],
                              equip=hero_form.cleaned_data['equipments'],
                              life=50,
                              attack=50,
                              defence=50,
                              )

                myhero.build_in_equipment()  # Equipaggiamo all'eroe l'arma scelta
                myhero.save()                # Salviamo il nuovo eroe creato

                # Salviamo l'eroe creato nella chiave esterna di user per associare le taballe

                my_user = request.user
                my_user.protagonist = myhero
                my_user.save()

                # Messaggio di eroe creato correttamente

                messages.success(request, 'Eroe creato correttamente.', extra_tags='hero_created')
                return redirect('user_home')
        else:
            hero_form = HeroForm()  # Se il form non è valido lo riproponiamo

    return render(request, 'first_creation_hero.html', {"form": hero_form})


""" La view user home è collegata al rispettivo templete come le altre e si occupa di mostrare oltre che la navbar di 
di navigazione anche lo status dell'utente per quanto riguarda l'eroe e le sue statistiche compreso l'equipaggiamento 
in suo possesso"""


@login_required(login_url='/login/')
def user_home(request):
    if request.user.usertype == 'GAMEDEVELOPER':
        return redirect('gamedev_home')
    elif request.user.is_staff:
        return HttpResponseRedirect(reverse('admin:index'))
    else:               # Recuperiamo tutte le caratteristiche dell'user in sessione
        username = request.user.username                   # Username

        user_hero = request.user.protagonist               # Eroe
        hero_life = request.user.protagonist.life          # Vita dell'eroe
        hero_attack = request.user.protagonist.attack      # Attacco dell'eroe
        hero_defence = request.user.protagonist.defence    # Difesa dell'eroe

        if request.user.protagonist.equip is not None:     # Se l'eroe possiede un equipaggiamento
            hero_equip = request.user.protagonist.equip                    # Prendiamo l'equipaggiamento in particolare:
            hero_equip_role = request.user.protagonist.equip.role.lower()  # Ruolo  con custom in minuscolo
            hero_equip_stat = request.user.protagonist.equip.stat          # Statistica che va a modificare
        else:                                              # Se l'eroe invece non lo possiede
            hero_equip = "Il personaggio non presenta alcun equipaggiamento"
            hero_equip_role = " "
            hero_equip_stat = 0

        # Context è la variabile che utilizziamo per raggruppare tutti i dati che vanno inidirizzati al template

        context = {'user_hero': user_hero, 'username': username, 'hero_life': hero_life, 'hero_attack': hero_attack,
                   'hero_defence': hero_defence, 'hero_equip': hero_equip, 'hero_equip_role': hero_equip_role,
                   'hero_equip_stat': hero_equip_stat}

        return render(request, 'user_home.html', context)


"""Questa view si occupa di permettere all'utente attraverso un form creato in form.py di cambiare l'equipaggiamento 
al suo eroe e salvarlo correttamente nel database aggiornando le statistiche che lo stesso equipaggiamento va a cambiare
"""


@login_required(login_url='/login/')
def change_equipment(request):
    if request.user.usertype == 'GAMEDEVELOPER':
        return redirect('gamedev_home')
    elif request.user.is_staff:
        return HttpResponseRedirect(reverse('admin:index'))
    else:
        equipment_form = EquipmentForm(request.POST)                  # Mettiamo il form con la scelta in una variabile
        user_hero = request.user.protagonist                          # Richiamiamo l'eroe dell'utente

        if request.method == 'POST':
            if equipment_form.is_valid():
                new_equip = equipment_form.cleaned_data['equipments']   # La scleta va nella variabile

                user_hero.remove_equipment()       # Usiamo il metodo della classe hero per rimuovere l'equipagggiamento
                user_hero.equip = new_equip        # Salviamo il nuovo equipaggiamento nel databata
                user_hero.build_in_equipment()     # Aggiorniamo le statistiche dell'eroe con il metodo della classe
                user_hero.save()

                # Attraverso un messaggio di conferma avvisiamo dell'avvenuto cambio

                messages.success(request, 'Equipaggiamento aggiornato correttamente.', extra_tags='equip_changed')
                return redirect('user_home')
        else:
            equipment_form = EquipmentForm()

        context = {'form': equipment_form}
        return render(request, 'change_equipment.html', context)


"""La view fight si occupa di mettere in condizione l'utente di attivare una battaglia simulata, mette a disposizione
un form creato in form.py che permette all'utente di scegliere uno dei boss disponibili, di sfidarlo e di ricevere il 
risultato calcolato in base alle statistiche del proprio eroe e di quelle del boss"""


@login_required(login_url='/login/')
def fight(request):
    if request.user.usertype == 'GAMEDEVELOPER':
        return redirect('gamedev_home')
    elif request.user.is_staff:
        return HttpResponseRedirect(reverse('admin:index'))
    else:                  # Inizializziamo tutte le variabili che ci servono in modo da non risultare mai vuote
        result = None
        boss_stats = None
        boss_equip = None
        possible_drop = None

        boss_form = BossForm(request.POST)  # In una variabile prendiamo il nostro form con la scelta

        username = request.user.username                # Recuperiamo tutte le caratteristiche dell'eroe

        user_hero = request.user.protagonist
        hero_life = request.user.protagonist.life
        hero_attack = request.user.protagonist.attack
        hero_defence = request.user.protagonist.defence

        if request.user.protagonist.equip is not None:                  # Controlliamo e recuperiamo il suo
            hero_equip = request.user.protagonist.equip                 # equipaggiamento
            hero_equip_role = request.user.protagonist.equip.role
            hero_equip_stat = request.user.protagonist.equip.stat
        else:
            hero_equip = "L'eroe non presenta alcun equipaggiamento"   # Se l'equipaggiamento non esiste
            hero_equip_role = ""
            hero_equip_stat = 0

        all_boss_equip = BossEquipment.objects.all()            # Creiamo una query per tutti i possibili boss e drop

        if request.method == 'POST':
            equip_list = []                                    # Inizializziamo una lista d'appoggio

            if boss_form.is_valid():                           # Se la scelta è valida
                boss_choose = boss_form.cleaned_data['boss']   # Prendiamo la scelta

                # Filtriamo una query per i drop di del boss scelto

                possible_drop = BossEquipment.objects.filter(enemy=boss_choose)

                # Recuperiamo il tasto Combatti dal template per utilizzarlo in una casistica sotto espressa

                confirm = request.POST.get('combatti')

                if possible_drop.exists():            # Se esistono i possibili drop del boss
                    for equip in possible_drop:       # Allora salvali dento la lista inizializzata in precedenza
                        equip_list.append(equip.equip)

                    random_equip = random.choice(equip_list)   # Con il metodo random ne scegliamo uno

                    boss_choose.build_equip(random_equip)     # Con il metodo della classe boss lo equipaggiamo al boss

                    # Attraverso il metodo fight di hero simuliamo la battaglia e salviamo il risultato

                    result = request.user.protagonist.fight(boss_choose)

                    # Recuperiamo le statistiche con equipaggiamento del boss sfidato

                    boss_stats = f"Vita: +{boss_choose.life}, Attacco: +{boss_choose.attack}, " \
                                 f"Difesa: +{boss_choose.defence}"
                    boss_equip = random_equip

                    if result == "YOU WIN":  # Se il boss perde, perde anche l'equipaggiamento
                        equip_drop = BossEquipment.objects.filter(enemy=boss_choose, equip=random_equip).get()
                        equip_drop.delete()
                elif not possible_drop and confirm:  # Se il boss non ha equipaggiamenti e si tenta di combattere
                    messages.error(                  # Messaggio di errore
                        request, 'Impossibile avviare la battaglia, il boss non possiede alcun equipaggiamento.',
                        extra_tags='no_battle'
                    )

        else:
            boss_form = BossForm()

        context = {'user_hero': user_hero, 'username': username, 'hero_life': hero_life, 'hero_attack': hero_attack,
                   'hero_defence': hero_defence, 'hero_equip': hero_equip, 'hero_equip_role': hero_equip_role,
                   'hero_equip_stat': hero_equip_stat, 'form': boss_form, 'results': result, 'boss_stats': boss_stats,
                   'boss_equip': boss_equip, 'possible_drop': possible_drop, 'all_boss_equip': all_boss_equip}
        return render(request, 'fight.html', context)


""" In questa view ci si occupa della pagina principale del game developer, la stessa gestisce un form creato in form.py 
che permette di selezionare un boss o un equipaggiamento da modificare  attraverso una json dump che permette di salvare 
un dato e trasferirlo ad un altra view serializzandolo e salvandolo in una sessione """


@login_required(login_url='/login/')
def gamedev_home(request):
    if request.user.usertype == 'USER':
        return redirect('user_home')
    elif request.user.is_staff:
        return HttpResponseRedirect(reverse('admin:index'))
    else:
        bossequipment_form = BossEquipmentForm(request.POST)  # Salviamo il nostro form con la scelta in una variabile

        username = request.user.username                      # Recuperiamo l'username dell'utente per mostralo poi

        # Inizializziamo una query con tutte le associazioni boss-equipaggiamento

        all_boss_equip = BossEquipment.objects.all()
        if request.method == 'POST':

            if bossequipment_form.is_valid():          # Se il form è valido
                equipment_chosen = bossequipment_form.cleaned_data['equipments']  # Salviamo l'equipaggiamento scelto
                boss_chosen = bossequipment_form.cleaned_data['boss']      # Oppure salviamo il boss

                # Controlliamo quale scelta è stata fatta e la carichiamo nella session alternativa passando direttamen-
                # te ad un altra view in base alla stessa scelta

                if equipment_chosen is not None:
                    equips_ser = json.dumps(equipment_chosen, default=serialize)
                    request.session['equipment_chosen'] = equips_ser
                    return redirect('update_equipment')
                elif boss_chosen is not None:
                    bosses_ser = json.dumps(boss_chosen, default=serialize)
                    request.session['boss_chosen'] = bosses_ser
                    return redirect('update_boss')

            else:
                bossequipment_form = BossEquipmentForm()

        context = {'username': username, 'form': bossequipment_form, 'all_boss_equip': all_boss_equip}
        return render(request, 'gamedev_home.html', context)


"""La view update_equipment si occupa di recuperare dalla sessione alternativa il dato passato dalla view gamedev-home
la stessa atrtaverso json laod la deserializza e permette all'utente di poter accedere al form di modifica 
dell'equipaggiamento scelto  """


@login_required(login_url='/login/')
def update_equipment(request):
    if request.user.usertype == 'USER':
        return redirect('user_home')
    elif request.user.is_staff:
        return HttpResponseRedirect(reverse('admin:index'))
    else:
        equipment_chosen = request.session.get('equipment_chosen')  # Recuperiamo la scelta dalla sessione alternativa

        if equipment_chosen is None:            # Se si tenta di accedere da indirizzo quindi saltando la scelta
            return redirect('gamedev_home')     # si viene reindirizzati a compiere la scelta

        equip = json.loads(equipment_chosen)   # De serializziamo la scelta dell'equipaggiamento
        equip_id = None                        # Inizializziamo una variabile per recuperare l'id della scelta

        for key, value in equip.items():      # Cerchiamo l'id all'interno del dizionario (la scelta de serializzata)
            if key == 'id':
                equip_id = value
        equip_chosen = Equipment.objects.get(id=equip_id)  # Recuperiamo l'equipaggiamento scelto come oggetto

        # Passiamo l'equipaggiamento da modificare al form e salviamo il form in una variabile

        update_equipment_form = UpdateEquipmentForm(request.POST, equip_query=equip_chosen)

        # Facciamo una query per avere tutti i boss come id e successivamente una per avere tutti i boss come id che
        # posseggono quel equipaggiamento

        all_boss = Boss.objects.values_list('id', flat=True)
        boss_with_equip = BossEquipment.objects.filter(equip=equip_chosen).values_list('enemy', flat=True)

        boss_without_equip = []   # Inizializziamo la lista per trovare i boss che non hanno l'equipaggiamento scelto

        # Cicliamo la lista di tutti i boss e se tra quelli è presente uno che non ha quell'equipaggiamento e uno che
        # non è gia presente tra quelli rilevati senza quell'equipaggiamento, allora lo aggiungiamo alla lista

        for boss in all_boss:
            if boss not in boss_with_equip and boss not in boss_without_equip:
                boss_without_equip.append(boss)  # Aggiunto alla lista dei boss senza quel possibile equipaggiamento

        if request.method == 'POST':
            if update_equipment_form.is_valid():  # Se il form è valido

                equip_chosen.name = update_equipment_form.cleaned_data['name']  # Recuperiamo il nuovo nome
                equip_chosen.role = update_equipment_form.cleaned_data['role']  # Recuperiamo il nuovo ruolo
                equip_chosen.stat = update_equipment_form.cleaned_data['stat']  # Recuperiamo la nuova statistica
                equip_chosen.save()                                             # Salviamo nel database la modifica

                # Recuperiamo la lista dei boss scelti per aggiungere alla tabella dei boss associati agli
                # equipaggiamenti per aggiungere le nuove righe di associazione al database

                boss_list = update_equipment_form.cleaned_data.get('add_boss')  # Recuperiamo i boss da aggiungere
                for item in boss_list:                          # Per ogni boss nella lista
                    add_enemy = Boss.objects.get(id=item.id)    # Recuperiamo l'id del boss
                    mybossequip = BossEquipment(enemy=add_enemy,            # Creiamo la nuova riga
                                                equip=equip_chosen,
                                                )
                    mybossequip.save()                          # Salviamo la nuova riga

                # Il procedimento si ripete per i boss che possiedono già quell equipaggiamento e che non devono più
                # possederlo

                boss_removed = update_equipment_form.cleaned_data.get('remove_boss')
                for item in boss_removed:
                    remove_enemy = Boss.objects.get(id=item.enemy.id)
                    mybossequip = BossEquipment.objects.filter(equip=equip_chosen, enemy=remove_enemy).get()
                    mybossequip.delete()

                # Se tutto è andato correttamente viene visualizzato un messaggio di successo

                messages.success(request, 'Equipaggiamento modificato correttamente', extra_tags='equip')
                return redirect('gamedev_home')
        else:
            update_equipment_form = UpdateEquipmentForm(equip_query=equip_chosen)

    context = {'form': update_equipment_form, 'boss_without_equip': boss_without_equip, 'equip_chose': equip_chosen}

    return render(request, 'update_equipment.html', context)


""" In questa view si ripetono identiche le stesse righe di codice della view precedente che servono invece a modificare
un entità di tipo Boss, per chiarezza di codice le variabili hanno i nomi dell'entità che vanno a modificare quindi se
nella view precedente una variabile era equip ora la stessa sarà boss"""


@login_required(login_url='/login/')
def update_boss(request):
    if request.user.usertype == 'USER':
        return redirect('user_home')
    elif request.user.is_staff:
        return HttpResponseRedirect(reverse('admin:index'))
    else:
        boss_chosen_first = request.session.get('boss_chosen')

        if boss_chosen_first is None:
            return redirect('gamedev_home')

        boss_to_edit = json.loads(boss_chosen_first)
        boss_id = None

        for key, value in boss_to_edit.items():
            if key == 'id':
                boss_id = value

        boss_chosen = Boss.objects.get(id=boss_id)

        update_boss_form = UpdateBossForm(request.POST, boss_query=boss_chosen)

        all_equip = Equipment.objects.values_list('id', flat=True)
        equip_with_boss = BossEquipment.objects.filter(enemy=boss_chosen).values_list('equip', flat=True)

        equip_without_boss = []

        for equip in all_equip:
            if equip not in equip_with_boss and equip not in equip_without_boss:
                equip_without_boss.append(equip)

        if request.method == 'POST':
            if update_boss_form.is_valid():

                boss_chosen.name = update_boss_form.cleaned_data['name']
                boss_chosen.life = update_boss_form.cleaned_data['life']
                boss_chosen.attack = update_boss_form.cleaned_data['attack']
                boss_chosen.defence = update_boss_form.cleaned_data['defence']
                boss_chosen.place = update_boss_form.cleaned_data['place']
                boss_chosen.save()

                equip_list = update_boss_form.cleaned_data.get('add_equipment')
                for item in equip_list:
                    add_equip = Equipment.objects.get(id=item.id)
                    myequipboss = BossEquipment(enemy=boss_chosen,
                                                equip=add_equip,
                                                )
                    myequipboss.save()

                equip_removed = update_boss_form.cleaned_data.get('remove_equipment')
                for item in equip_removed:
                    remove_equip = Equipment.objects.get(id=item.equip.id)
                    mybossequip = BossEquipment.objects.filter(equip=remove_equip, enemy=boss_chosen).get()
                    mybossequip.delete()

                messages.success(request, 'Boss modificato correttamente', extra_tags='boss')
                return redirect('gamedev_home')
        else:
            update_boss_form = UpdateBossForm(boss_query=boss_chosen)

        return render(request, 'update_boss.html', {'form': update_boss_form, 'equip_without_boss': equip_without_boss,
                                                    'boss_chose': boss_chosen})


"""La view add_equipment gestisce la creazione di un nuovo equipaggiamento mediante un form creato in form.py che 
permette di settare un nuovo equipaggiamento e di salvarlo nel database, gestisce anche le associazioni con i boss
nella tabella con relazione n ad n"""


@login_required(login_url='/login/')
def add_equipment(request):
    if request.user.usertype == 'USER':
        return redirect('user_home')
    elif request.user.is_staff:
        return HttpResponseRedirect(reverse('admin:index'))
    else:
        equipment_form = AddEquipmentForm(request.POST)

        if request.method == 'POST':
            if equipment_form.is_valid():                                    # Prediamo i dati inseriti nel form
                myequip = Equipment(name=equipment_form.cleaned_data['name'],
                                    role=equipment_form.cleaned_data['role'],
                                    stat=equipment_form.cleaned_data['stat'],
                                    )

                myequip.save()                                                # Salviamo il nuovo equipaggimaento

                # Prendiamo le associazioni con i boss e le salviamo in una lista

                boss_list = equipment_form.cleaned_data.get('add_boss')

                for item in boss_list:  # Per ogni boss scelto
                    add_enemy = Boss.objects.get(id=item.id)   # Recuperiamo tramite id il boss
                    mybossequip = BossEquipment(enemy=add_enemy,    # Carichiamo l'associazione nel database
                                                equip=myequip,
                                                )
                    mybossequip.save()                         # Salviamo

                messages.success(request, 'Equipaggiamento creato correttamente.', extra_tags='equip')
                return redirect('gamedev_home')
        else:
            equipment_form = AddEquipmentForm()

    context = {'form': equipment_form}
    return render(request, 'add_equipment.html', context)


"""Questa view è identica alla view precedente si occupa al contrario però di aggiungere un nuovo boss tramite form 
creato in form.py e di caricare l'associazione con l'equipaggiamento nella tabella delle relazioni """


@login_required(login_url='/login/')
def add_boss(request):
    if request.user.usertype == 'USER':
        return redirect('user_home')
    elif request.user.is_staff:
        return HttpResponseRedirect(reverse('admin:index'))
    else:
        boss_form = AddBossForm(request.POST)

        if request.method == 'POST':
            if boss_form.is_valid():
                myboss = Boss(name=boss_form.cleaned_data['name'],
                              life=boss_form.cleaned_data['life'],
                              attack=boss_form.cleaned_data['attack'],
                              defence=boss_form.cleaned_data['defence'],
                              place=boss_form.cleaned_data['place'],
                              )

                myboss.save()

                equip_list = boss_form.cleaned_data.get('add_equipment')

                for item in equip_list:
                    add_equip = Equipment.objects.get(id=item.id)
                    mybossequip = BossEquipment(enemy=myboss,
                                                equip=add_equip,
                                                )
                    mybossequip.save()

                messages.success(request, 'Boss creato correttamente.', extra_tags='boss')
                return redirect('gamedev_home')
        else:
            boss_form = AddBossForm()

    context = {'form': boss_form}
    return render(request, 'add_boss.html', context)


""" Tramite un form in form.py questa view gestisce la rimozione dal database di un equipaggiamento gestendone anche
le associazioni che lo stesso oggetto ha in comune con altre tabelle, tuttavia per la scelta della modalità cascade
dello stesso equipaggiamento viene gestito il solo reset delle qualità dell'eroe in assenza di equipaggiamento"""


@login_required(login_url='/login/')
def remove_equipment(request):
    if request.user.usertype == 'USER':
        return redirect('user_home')
    elif request.user.is_staff:
        return HttpResponseRedirect(reverse('admin:index'))
    else:
        remove_equipment_form = DeleteEquipmentForm(request.POST)

        if request.method == 'POST':
            if remove_equipment_form.is_valid():  # Se il form è valido salviamo l'equipaggiamento da eliminare
                myequip = remove_equipment_form.cleaned_data['remove_equip']

                # Controlliamo e cerchiamo quali eroi posseggono quel equipaggiamento

                hero_with_myequip = Hero.objects.filter(equip=myequip).values_list('id', flat=True)

                if hero_with_myequip is not None:  # Se ne abbiamo trovati
                    for item in hero_with_myequip:
                        hero = Hero.objects.get(id=item)
                        hero.remove_equipment()         # Settiamo le statistiche di ogni eroe
                        hero.save()                     # Salviamo

                myequip.delete()         # Cancelliamo l'equipaggiamento scelto

                messages.success(request, 'Equipaggiamento eliminato correttamente.', extra_tags='equip')
                return redirect('gamedev_home')
        else:
            remove_equipment_form = DeleteEquipmentForm()

    context = {'form': remove_equipment_form}
    return render(request, 'remove_equipment.html', context)


""" Come la precedente questa view tramite un form creato in form.py permette di cancellare un boss dal database per 
la proprietà cascade della sua chiave anche questo sarà eliminato automaticamente in ogni tabella in cui possiede 
una relazione"""


@login_required(login_url='/login/')
def remove_boss(request):
    if request.user.usertype == 'USER':
        return redirect('user_home')
    elif request.user.is_staff:
        return HttpResponseRedirect(reverse('admin:index'))
    else:
        remove_boss_form = DeleteBossForm(request.POST)
        if request.method == 'POST':
            if remove_boss_form.is_valid():  # Se il form è valido recuperiamo la scelta
                myboss = remove_boss_form.cleaned_data['remove_boss']

                myboss.delete()             # Eliminiamo il boss

                messages.success(request, 'Boss eliminato correttamente.', extra_tags='boss')
                return redirect('gamedev_home')
        else:
            remove_boss_form = DeleteBossForm()

        context = {'form': remove_boss_form}
        return render(request, 'remove_boss.html', context)
