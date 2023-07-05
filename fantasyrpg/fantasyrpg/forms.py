from fantasyrpg.models import MyUser, Equipment, Boss, BossEquipment
from django import forms

"""La casse UserForm è utilizzata come form d compilazione, presenta gli attributi di un form quali , nome, cognome, 
username, password e conferma password e ancora il tipo di user, sono tutti valori che dialogano con la view signup;
inoltre presenta due funzioni clean che rispettivamente controllano che gli input dati dall'utente siano corretti 
altrimenti poi viene gestito nella view tramite il form is valid il form da ricompilare"""


class UserForm(forms.Form):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome'}),
        label='', max_length=35)
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'surname', 'placeholder': 'Cognome'}),
        label='', max_length=35)
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'uname', 'placeholder': 'Username'}),
        label='', max_length=35)
    password = forms.CharField(
        widget=forms.PasswordInput(render_value=True,
                                   attrs={'class': 'form-control', 'id': 'pwd', 'placeholder': 'Password'}),
        label='', max_length=35)
    pass_confirm = forms.CharField(
        widget=forms.PasswordInput(render_value=True,
                                   attrs={'class': 'form-control', 'id': 'pwd', 'placeholder': 'Conferma Password'}),
        label='', max_length=35)
    user_type = forms.ChoiceField(widget=forms.RadioSelect, required=True, choices=MyUser.USERTYPE_CHOICE,
                                  label='Seleziona il tipo di utente:')

    def clean_pass_confirm(self):  # Se la conferma della password è sbagliata manda l'errore e il messaggio
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get("password")
        pass_confirm = cleaned_data.get("pass_confirm")

        if password != pass_confirm:
            raise forms.ValidationError("La password e la conferma della password non corrispondono")

    def clean_username(self):  # Se lo username è già presente nel database allora manda l'errore e il messaggio
        cleaned_data = super(UserForm, self).clean()
        username = cleaned_data.get('username')

        if MyUser.objects.filter(username=username).exists():
            raise forms.ValidationError("L'username inserito appartiene ad un altro utente")
        else:
            return username


"""La classe HeroForm è utilizzata come un form che è gestito dalla view first_creation_hero tramite gli attributi nome 
ed equipaggiamento permette all'utente di scegliere inserendo in input gli stessi dati del proprio eroe"""


class HeroForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'name',
                                                         'placeholder': 'Hero name'}), label='', max_length=35)
    all_equipment = Equipment.objects.all()
    equipments = forms.ModelChoiceField(widget=forms.RadioSelect, queryset=all_equipment, empty_label=None,
                                        label="Seleziona l'equipaggiamento del tuo eroe:")


"""La classe EquipmentForm è utilizzata come un form gestito nella view change_equipment che permette attraverso
l'attributo equipaggiamenti di selezionare un equipaggiamento tra quelli esistenti all'utente"""


class EquipmentForm(forms.Form):
    all_equipment = Equipment.objects.all().order_by('role', 'name')
    equipments = forms.ModelChoiceField(widget=forms.RadioSelect, label='Equipaggiamenti disponibili:',
                                        queryset=all_equipment, empty_label=None)
    equipments.label_from_instance = lambda equip: f"{equip.name} [{equip.role.lower().capitalize()} +{equip.stat}]"


"""La classe BossForm viene utilizzata come un form che è gestito nella view fight dove attraverso l'attributo boss 
viene permesso all'utente di scegliere uno tra i boss disponibili"""


class BossForm(forms.Form):
    all_boss = Boss.objects.all().order_by('place', 'name')
    boss = forms.ModelChoiceField(widget=forms.RadioSelect, label='Boss Disponibili',
                                  queryset=all_boss, empty_label=None)


"""La classe BossEquipmentForm viene utilizzata come un form e viene gestita nella views gamedev_home dove grazie ai due
attributi equipaggiamento e boss l'utente può scegliere in input uno di loro, nel template attraverso la form action
questo form viene separato in due con due tipi di reindirizzamento rispetto alla scelta fatta """


class BossEquipmentForm(forms.Form):
    all_equipment = Equipment.objects.all().order_by('role', 'name')
    equipments = forms.ModelChoiceField(widget=forms.RadioSelect, label='Equipaggiamenti disponibili:',
                                        queryset=all_equipment, empty_label=None, required=False)
    equipments.label_from_instance = lambda equip: f"{equip.name} [{equip.role.lower().capitalize()} +{equip.stat}]"

    all_boss = Boss.objects.all().order_by('place', 'name')
    boss = forms.ModelChoiceField(widget=forms.RadioSelect, label='Boss Disponibili',
                                  queryset=all_boss, empty_label=None, required=False)
    boss.label_from_instance = lambda boss: f"{boss.name} [L:+{boss.life} A:+{boss.attack} D:+{boss.defence}] " \
                                            f"{boss.place}"


"""La classe UpdateEquipmentForm viene utilizzata come un form gestito nella views update_equipment e tramite gli 
attributi nome, ruolo, statistica che va a modificare, aggiungi boss tra quelli esistenti, rimuovi boss tra quelli 
esistenti, e il metodo ridefinito del costruttore init permette di settare le caratteristiche dell'equipaggiamento 
scelto"""


class UpdateEquipmentForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'name', 'placeholder': 'Nome dell\'Equipaggiamento'}), label='',
        max_length=30)
    role = forms.ChoiceField(widget=forms.RadioSelect, choices=Equipment.ROLE_CHOICE, label='Ruolo:')
    stat = forms.IntegerField(min_value=1, max_value=100, label='Valore equipaggiamento (min 1, max 100):')
    add_boss = forms.ModelMultipleChoiceField \
        (widget=forms.CheckboxSelectMultiple, queryset=Boss.objects.all().order_by('id'),
         label="Aggiungi boss all'equipaggiamento:", required=False)
    remove_boss = forms.ModelMultipleChoiceField \
        (widget=forms.CheckboxSelectMultiple, queryset=BossEquipment.objects.none(),
         label='Rimuovi boss dall\'equipaggiamento:', required=False)

    remove_boss.label_from_instance = lambda boss: f"{boss.enemy.name}"

    def __init__(self, *args, **kwargs):        # Attraverso la query che passiamo in input come kwargs
        equip_query = kwargs.pop('equip_query')     # Recuperiamo la query
        super(UpdateEquipmentForm, self).__init__(*args, **kwargs)  # Settiamo l'attributo di remove boss.queryset

        self.fields["remove_boss"].queryset = BossEquipment.objects.filter(equip=equip_query)  # Con la query passata


"""La classe UpdateBossForm viene utilizzata come un form gestito nella views update_boss quasi identico al precedente 
 form, permette attraverso gli attributi nome, vita, attacco, difesa, luogo del boss, aggiungi equipaggiamento e 
 rimuovi equipaggiamento e il metodo ridefinito init, di settare le caratteristiche di un boss """


class UpdateBossForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'name', 'placeholder': 'Nome del Boss'}), label='',
        max_length=30)
    life = forms.IntegerField(min_value=1, max_value=100, label='Valore Salute (min 1, max 100):')
    attack = forms.IntegerField(min_value=1, max_value=100, label='Valore Attacco (min 1, max 100):')
    defence = forms.IntegerField(min_value=1, max_value=100, label='Valore Difesa (min 1, max 100):')
    place = forms.ChoiceField(widget=forms.RadioSelect, choices=Boss.PLACE_CHOICE, label="Luogo d'incontro:",
                              required=True)
    add_equipment = forms.ModelMultipleChoiceField \
        (widget=forms.CheckboxSelectMultiple, queryset=Equipment.objects.all().order_by('id'),
         label="Aggiungi equipaggiamenti al boss:", required=False)
    remove_equipment = forms.ModelMultipleChoiceField \
        (widget=forms.CheckboxSelectMultiple, queryset=BossEquipment.objects.none(),
         label="Rimuovi equipaggiamenti dal boss:", required=False)

    def __init__(self, *args, **kwargs):
        boss_query = kwargs.pop('boss_query')
        super(UpdateBossForm, self).__init__(*args, **kwargs)

        self.fields["remove_equipment"].queryset = BossEquipment.objects.filter(enemy=boss_query)


"""La classe AddEquipmentForm viene utilizzata come un form gestito nella views add_equipment che attraverso gli 
attributi nome, ruolo, statistica che va a modificare e aggiungi boss, di creare un nuovo equipaggiamento """


class AddEquipmentForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'name', 'placeholder': 'Nome dell\'Equipaggiamento'}), label='',
        max_length=30)
    role = forms.ChoiceField(widget=forms.RadioSelect, choices=Equipment.ROLE_CHOICE, label='Ruolo:')
    stat = forms.IntegerField(min_value=1, max_value=100, label='Valore equipaggiamento (min 1, max 100):')
    add_boss = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                              queryset=Boss.objects.all().order_by('id'),
                                              label="Scegli i boss che potranno equipaggiare questo oggetto:",
                                              required=False)


"""La classe AddBossForm viene utilizzata come un form gestito nella views add_boss che attraverso gli 
attributi nome, vita, attacco, difesa, luogo del boss e aggiungi equipaggiamento, di creare un nuovo boss """


class AddBossForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'name', 'placeholder': 'Nome del Boss'}), label='',
        max_length=30)
    life = forms.IntegerField(min_value=1, max_value=100, label='Valore Salute (min 1, max 100):')
    attack = forms.IntegerField(min_value=1, max_value=100, label='Valore Attacco (min 1, max 100):')
    defence = forms.IntegerField(min_value=1, max_value=100, label='Valore Difesa (min 1, max 100):')
    place = forms.ChoiceField(widget=forms.RadioSelect, choices=Boss.PLACE_CHOICE, label="Luogo d'incontro:",
                              required=True)
    add_equipment = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, queryset=Equipment.objects.all().order_by('id'),
        label="Aggiungi equipaggiamento al boss:", required=False)


"""La classe DeleteEquipmentForm viene utilizzata come un form gestito nella views delete_equipment che attraverso 
l'attributo rimuovi equipaggiamento permette di scegliere un equipaggiamento ed eliminarlo dal database"""


class DeleteEquipmentForm(forms.Form):
    remove_equip = forms.ModelChoiceField(
        widget=forms.RadioSelect, queryset=Equipment.objects.all().order_by('id'),
        label="Scegli l'equipaggiamento da eliminare:", empty_label=None)


"""La classe DeleteBossForm viene utilizzata come un form gestito nella views delete_boss che attraverso 
l'attributo rimuovi boss permette di scegliere un boss ed eliminarlo dal database"""


class DeleteBossForm(forms.Form):
    remove_boss = forms.ModelChoiceField(
        widget=forms.RadioSelect, queryset=Boss.objects.all().order_by('id'),
        label="Scegli il boss da eliminare:", empty_label=None)
