from django.db import models
from django.contrib.auth.models import AbstractUser
import random


"""La classe boss contiene gli attributi e i metodi che il boss possiede, ovvero:  Terreno di gioco di appartenenza,
Nome, Cognome, Vita, Attacco, Difesa e metodi: Indossa equipaggiamento, e Ridefinisci la string """


class Boss(models.Model):
    PLACE_CHOICE = (
        ("VULCANO", "vulcano"),
        ("VALLE", "valle"),
        ("GIUNGLA", "giungla"),
        ("DESERTO", "deserto"),
        ("OCEANO", "oceano"),
    )

    objects = models.Manager()
    name = models.CharField(max_length=30)
    life = models.IntegerField()
    attack = models.IntegerField()
    defence = models.IntegerField()
    place = models.CharField(max_length=30, choices=PLACE_CHOICE)

    def build_equip(self, equipment):  # Dato un equipaggiamento setta tutte le statistiche di battaglia del boss

        if equipment.role == "Life":
            self.life += equipment.stat
        elif equipment.role == "Attack":
            self.attack += equipment.stat
        elif equipment.role == "Defence":
            self.defence += equipment.stat

    def __str__(self):  # Serve per Mostrare nel database il nome del boss piuttosto che l'id
        return self.name


""" La classe Equipment contiene gli attributi di un equipaggiamento nome, ruolo e statistica che aumenta in più 
contiene una chiave esterna di boss per un associazione molti a molti"""


class Equipment(models.Model):
    ROLE_CHOICE = (
        ("Life", "life"),
        ("Attack", "attack"),
        ("Defence", "defence"),
    )
    objects = models.Manager()
    name = models.CharField(max_length=30)
    role = models.CharField(max_length=30, choices=ROLE_CHOICE)
    stat = models.IntegerField()
    enemy = models.ManyToManyField(Boss, through='BossEquipment')

    def __str__(self):
        return self.name


"""La classe Boss Equipment è una tabella di convenienza nonostante gia di suo django la crei per le manytomanyfield
noi avevamo bisogno di lavorare su una tabella con doppio accesso sia da boss che da equipaggiamento, per cui contiene
solo due chiavi esterne per permettere le associazioni tra le due entità boss ed equipaggiamento """


class BossEquipment(models.Model):
    objects = models.Manager()
    enemy = models.ForeignKey(Boss, on_delete=models.CASCADE)
    equip = models.ForeignKey(Equipment, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.enemy.name} {self.equip.name}"


"""La classe Hero contiene gli attributi dell'eroe come: nome, vita, attacco, difesa; contiene la chiave esterna di 
equipaggiamento per l'associazione con lo stesso e contiene i metodi Combatti, rimuovi equipaggiamento e aggiungi 
equipaggiamento"""


class Hero(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length=30)
    life = models.IntegerField()
    attack = models.IntegerField()
    defence = models.IntegerField()
    equip = models.ForeignKey(Equipment, null=True, on_delete=models.SET_NULL)

    # noinspection DuplicatedCode
    def fight(self, boss):

        """La logica di questo metodo è molto semplice dati due array di 0 e 1 rispettivamente riempiti inversamente
        che rappresentano la probabilità di vincita dei contendenti si fa un controllo sugli stessi contendenti
        rispettivamente le proprie statistica in base alla differenza o differenze di questi tra attacco, vita e
        difesa, allora nell'array di uno verrà aggiunto un 1 se la statistica è maggiore e verrà tolto 1 all'altro
        se la statistica è minore infine si estrae un numero casuale tra 1 e la chance che sarà rispettivamente la
        posizione casuale di un array e chi avrà l'1 in quella posizione allora avrà vinto la sfida"""

        chance = 10
        hero_chance = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]
        boss_chance = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]

        if boss.life != self.life:
            if boss.life < self.life:
                hero_chance.insert(6, 1)
                boss_chance.insert(6, 0)
            elif boss.life > self.life:
                hero_chance.insert(5, 0)
                boss_chance.insert(5, 1)
        if boss.attack != self.attack:
            if boss.attack < self.attack:
                hero_chance.insert(6, 1)
                boss_chance.insert(6, 0)
            elif boss.attack > self.attack:
                hero_chance.insert(5, 0)
                boss_chance.insert(5, 1)
        if boss.defence != self.defence:
            if boss.defence < self.defence:
                hero_chance.insert(6, 1)
                boss_chance.insert(6, 0)
            elif boss.defence > self.defence:
                hero_chance.insert(5, 0)
                boss_chance.insert(5, 1)

        great_fight = random.randint(1, chance)

        if boss_chance[great_fight] == 1:   # In base al controllo viene restituito il risultato
            result = 'YOU LOSE'
            return result
        elif hero_chance[great_fight] == 1:
            result = 'YOU WIN'
            return result

    def remove_equipment(self):    # Il metodo controlla rispetto se l'eroe ha un equipaggiamento e se viene eliminato
        if self.equip is not None:          # Elimina la aggiunta della statistica che l'equipaggiamento modificava
            if self.equip.role == "Life":
                self.life -= self.equip.stat
            elif self.equip.role == "Attack":
                self.attack -= self.equip.stat
            elif self.equip.role == "Defence":
                self.defence -= self.equip.stat

    def build_in_equipment(self):   # Come il metodo precedente questo una volta assegnato l'equipaggiamento all'eroe
        if self.equip.role == "Life":    # Controlla quale statistica l'equipaggiamento modifica e la aggiunge
            self.life += self.equip.stat
        elif self.equip.role == "Attack":
            self.attack += self.equip.stat
        elif self.equip.role == "Defence":
            self.defence += self.equip.stat

    def __str__(self):
        return self.name


"""La classe MyUser è una classe astratta che ci permette di utilizzare le stesse caratteristiche dello user di django
ma spostandolo dalla parte di database appartenente direttamente a fantasyrpg e quindi ci permette allo stesso tempo di 
utilizzare una tabella all'interno del database del nostro gioco pur utilizzando i metodi e alcuni attributi della
classe non astratta, in aggiunta il nostro user ha il tipo di user che è, e la chiave esterna dell'eroe per collegare 
direttamente lo stesso con l'utente"""


class MyUser(AbstractUser):
    USERTYPE_CHOICE = (
        ("USER", "User"),
        ("GAMEDEVELOPER", "Game Developer"),
    )

    usertype = models.CharField(max_length=15, choices=USERTYPE_CHOICE, blank=True)
    protagonist = models.OneToOneField(Hero, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.username
