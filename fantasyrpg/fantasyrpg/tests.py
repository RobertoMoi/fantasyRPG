import unittest
import json

from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login

from fantasyrpg.models import *
from fantasyrpg.forms import UserForm
from django.test import TestCase
from django.urls import reverse


class SignUpTest(TestCase):
    def setUp(self):
        self.signup_url = reverse('signup')

        self.user = {
            'first_name': 'myname',
            'last_name': 'mysurname',
            'username': 'myusername',
            'password': 'mypassword',
            'pass_confirm': 'mypassword',
            'user_type': 'USER'
        }
        self.user_gamedeveloper = {
            'first_name': 'myname',
            'last_name': 'mysurname',
            'username': 'myusername',
            'password': 'mypassword',
            'pass_confirm': 'mypassword',
            'user_type': 'GAMEDEVELOPER'
        }

        self.user_check_password = {
            'first_name': 'myname',
            'last_name': 'mysurname',
            'username': 'myusername',
            'password': 'mypassword',
            'pass_confirm': 'pass_confirm',
            'user_type': 'GAMEDEVELOPER'
        }

        return super().setUp()

    def test_signup_view_uses_correct_template(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')

    def test_user_registration(self):
        response = self.client.post(self.signup_url, self.user, format='text/html')
        self.assertEqual(response.status_code, 302)

    def test_gamedev_registration(self):
        response = self.client.post(self.signup_url, self.user_gamedeveloper, format='text/html')
        self.assertEqual(response.status_code, 302)

    def test_password_confirm(self):
        form = UserForm(self.user_check_password)
        self.assertFalse(form.is_valid())

        # controlla che venga lanciato l'errore quando la conferma della password è diversa dalla password
        with self.assertRaises(ValidationError):
            form.clean_pass_confirm()


class LoginTest(TestCase):
    def setUp(self):
        self.login_url = reverse('loginPage')

        dragon = Hero(name='Dragon',
                      life=65,
                      attack=75,
                      defence=50
                      )
        dragon.save()

        self.user_credentials = {
            'username': 'myusername',
            'password': 'abc',
            'usertype': 'USER'
        }

        self.user_credentials_with_hero = {
            'username': 'randomuser',
            'password': 'abc',
            'usertype': 'USER',
            'protagonist': dragon
        }

        self.gamedev_credentials = {
            'username': 'gamedeveloper',
            'password': 'abc',
            'usertype': 'GAMEDEVELOPER'
        }

        self.user = MyUser.objects.create_user(**self.user_credentials)
        self.user_with_hero = MyUser.objects.create_user(**self.user_credentials_with_hero)
        self.gamedeveloper = MyUser.objects.create_user(**self.gamedev_credentials)

    def test_login_view_uses_correct_template(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_user_success(self):
        user_auth = authenticate(username=self.user.username, password=self.user_credentials['password'])
        self.assertTrue((user_auth is not None) and user_auth.is_authenticated)
        self.assertTrue(self.client.login(username=self.user.username,
                                          password=self.user_credentials['password']))

    def test_wrong_username(self):
        user_auth = authenticate(username='wrong_username', password=self.user_credentials['password'])
        self.assertFalse((user_auth is not None) and user_auth.is_authenticated)

    def test_wrong_password(self):
        user_auth = authenticate(username=self.user.username, password='wrong_password')
        self.assertFalse((user_auth is not None) and user_auth.is_authenticated)

    def test_redirect_user(self):
        response = self.client.post(self.login_url, self.user_credentials, format='text/html')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('first_creation_hero'))

    def test_redirect_user_with_hero(self):
        response = self.client.post(self.login_url, self.user_credentials_with_hero, format='text/html')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('user_home'))

    def test_redirect_gamedeveloper(self):
        response = self.client.post(self.login_url, self.gamedev_credentials, format='text/html')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gamedev_home'))


class LogoutTest(TestCase):
    def setUp(self):
        self.logout_url = reverse('logout')

        self.user_credentials = {
            'username': 'myusername',
            'password': 'abc',
            'usertype': 'USER'
        }

        self.user = MyUser.objects.create_user(**self.user_credentials)

    def test_redirect_user_after_logout(self):
        self.assertTrue(self.client.login(username=self.user.username, password=self.user_credentials['password']))
        response = self.client.post(self.logout_url, self.user_credentials, format='text/html')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('loginPage'))


class FirstCreationHeroTest(TestCase):
    def setUp(self):
        self.first_creation_hero_url = reverse('first_creation_hero')

        self.user_data = {
            'username': '65750',
            'password': 'abc',
            'usertype': 'USER'
        }

        self.first_user = MyUser.objects.create_user(**self.user_data)

        self.client.login(username=self.first_user.username, password='abc')

    def test_first_creation_hero_view_url_exists_at_desired_location(self):
        response = self.client.get(self.first_creation_hero_url)
        self.assertEqual(response.status_code, 200)

    def test_first_creation_hero_view_uses_correct_template(self):
        response = self.client.post(self.first_creation_hero_url, self.user_data, format='text/html')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(self.client.get(self.first_creation_hero_url), 'first_creation_hero.html')


class UserHomeTest(TestCase):
    def setUp(self):
        self.user_home_url = reverse('user_home')

        dragon = Hero(name='Dragon',
                      life=65,
                      attack=75,
                      defence=50
                      )
        dragon.save()

        self.first_user = MyUser.objects.create_user(username='65750', password='abc', usertype='USER',
                                                     protagonist=dragon)
        self.gamedeveloper = MyUser.objects.create_user(username='65850', password='abc', usertype='GAMEDEVELOPER')

        self.user_data = {
            'username': '65750',
            'password': 'abc',
            'user_type': 'USER'
        }

        self.gamedev_data = {
            'username': '65850',
            'password': 'abc',
            'user_type': 'GAMEDEVELOPER'
        }

        self.client.login(username=self.first_user.username, password='abc')

    def test_user_home_view_uses_correct_template(self):
        response = self.client.get(self.user_home_url)
        self.assertEqual(response.status_code, 200)

    def test_user_home_page_displayed_correctly(self):
        response = self.client.post(self.user_home_url, self.user_data, format='text/html')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(self.client.get(self.user_home_url), 'user_home.html')

    def test_user_home_redirect_if_user_is_gamedeveloper(self):
        self.assertTrue(self.client.login(username=self.gamedeveloper.username, password='abc'))
        response = self.client.post(self.user_home_url, self.gamedev_data, format='text/html')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gamedev_home'))


class ChangeEquipmentTest(TestCase):
    def setUp(self):
        self.change_equipment_url = reverse('change_equipment')

        dragon = Hero(name='Drago',
                      life=65,
                      attack=75,
                      defence=50
                      )
        dragon.save()

        self.first_user = MyUser.objects.create_user(username='65750', password='abc', usertype='USER',
                                                     protagonist=dragon)

        self.user_data = {
            'username': '65750',
            'password': 'abc',
            'user_type': 'USER'
        }

        self.client.login(username=self.first_user.username, password='abc')

    def test_change_equipment_view_url_exists_at_desired_location(self):
        response = self.client.get(self.change_equipment_url)
        self.assertEqual(response.status_code, 200)

    def test_change_equipment_view_uses_correct_template(self):
        response = self.client.post(self.change_equipment_url, self.user_data, format='text/html')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(self.client.get(self.change_equipment_url), 'change_equipment.html')


class FightTest(TestCase):
    def setUp(self):
        self.fight_url = reverse('fight')
        sword = Equipment(name='Sword',
                          role='Attack',
                          stat=15
                          )
        sword.save()

        dragon = Hero(name='Dragon',
                      life=65,
                      attack=75,
                      defence=50,
                      equip=sword
                      )
        dragon.save()

        self.first_user = MyUser.objects.create_user(username='65750', password='abc', usertype='USER',
                                                     protagonist=dragon)

        self.user_data = {
            'username': '65750',
            'password': 'abc',
            'user_type': 'USER'
        }

        self.client.login(username=self.first_user.username, password='abc')

    def test_change_equipment_view_url_exists_at_desired_location(self):
        response = self.client.get(self.fight_url)
        self.assertEqual(response.status_code, 200)

    def test_fight_view_uses_correct_template(self):
        response = self.client.post(self.fight_url, self.user_data, format='text/html')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(self.client.get(self.fight_url), 'fight.html')


class GameDevHomeViewTest(TestCase):
    def setUp(self):
        self.gamedev_home_url = reverse('gamedev_home')

        dragon = Hero(name='Dragon',
                      life=65,
                      attack=75,
                      defence=50,
                      )
        dragon.save()

        self.gamedev_data = {
            'username': '65750',
            'password': 'abc',
            'usertype': 'GAMEDEVELOPER'
        }

        self.user_data = {
            'username': '65850',
            'password': 'abc',
            'usertype': 'USER',
            'protagonist': dragon
        }

        self.gamedeveloper = MyUser.objects.create_user(**self.gamedev_data)
        self.user = MyUser.objects.create_user(**self.user_data)

        self.client.login(username=self.gamedeveloper.username, password='abc')

    def test_gamedev_home_view_url_exists_at_desired_location(self):
        response = self.client.get(self.gamedev_home_url)
        self.assertEqual(response.status_code, 200)

    def test_gamedev_view_uses_correct_template(self):
        response = self.client.post(self.gamedev_home_url, self.gamedev_data, format='text/html')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(self.client.get(self.gamedev_home_url), 'gamedev_home.html')

    def test_gamedev_home_redirect_if_user_is_player(self):
        self.assertTrue(self.client.login(username=self.user.username, password='abc'))
        response = self.client.post(self.gamedev_home_url, self.user_data, format='text/html')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('user_home'))


class AddEquipmentViewTest(TestCase):
    def setUp(self):
        self.add_equipment_url = reverse('add_equipment')

        self.gamedev_data = {
            'username': '65750',
            'password': 'abc',
            'usertype': 'GAMEDEVELOPER'
        }

        self.gamedeveloper = MyUser.objects.create_user(**self.gamedev_data)

        self.client.login(username=self.gamedeveloper.username, password=self.gamedev_data['password'])

    def test_add_equipment_view_url_exists_at_desired_location(self):
        response = self.client.get(self.add_equipment_url)
        self.assertEqual(response.status_code, 200)

    def test_add_equipment_view_uses_correct_template(self):
        response = self.client.post(self.add_equipment_url, self.gamedev_data, format='text/html')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(self.client.get(self.add_equipment_url), 'add_equipment.html')


class AddBossViewTest(TestCase):
    def setUp(self):
        self.add_boss_url = reverse('add_boss')

        self.gamedev_data = {
            'username': '65750',
            'password': 'abc',
            'usertype': 'GAMEDEVELOPER'
        }

        self.gamedeveloper = MyUser.objects.create_user(**self.gamedev_data)

        self.client.login(username=self.gamedeveloper.username, password=self.gamedev_data['password'])

    def test_add_boss_view_url_exists_at_desired_location(self):
        response = self.client.get(self.add_boss_url)
        self.assertEqual(response.status_code, 200)

    def test_add_boss_page_view_uses_correct_template(self):
        response = self.client.post(self.add_boss_url, self.gamedev_data, format='text/html')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(self.client.get(self.add_boss_url), 'add_boss.html')


class RemoveEquipmentViewTest(TestCase):
    def setUp(self):
        self.remove_equipment_url = reverse('remove_equipment')

        self.gamedev_data = {
            'username': '65750',
            'password': 'abc',
            'usertype': 'GAMEDEVELOPER'
        }

        self.gamedeveloper = MyUser.objects.create_user(**self.gamedev_data)

        self.client.login(username=self.gamedeveloper.username, password=self.gamedev_data['password'])

    def test_remove_equipment_view_url_exists_at_desired_location(self):
        response = self.client.get(self.remove_equipment_url)
        self.assertEqual(response.status_code, 200)

    def test_remove_equipment_view_uses_correct_template(self):
        response = self.client.post(self.remove_equipment_url, self.gamedev_data, format='text/html')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(self.client.get(self.remove_equipment_url), 'remove_equipment.html')


class RemoveBossViewTest(TestCase):
    def setUp(self):
        self.remove_boss_url = reverse('remove_boss')

        self.gamedev_data = {
            'username': '65750',
            'password': 'abc',
            'usertype': 'GAMEDEVELOPER'
        }

        self.gamedeveloper = MyUser.objects.create_user(**self.gamedev_data)

        self.client.login(username=self.gamedeveloper.username, password=self.gamedev_data['password'])

    def test_remove_boss_view_url_exists_at_desired_location(self):
        response = self.client.get(self.remove_boss_url)
        self.assertEqual(response.status_code, 200)

    def test_remove_boss_view_uses_correct_template(self):
        response = self.client.post(self.remove_boss_url, self.gamedev_data, format='text/html')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(self.client.get(self.remove_boss_url), 'remove_boss.html')


class ModelTest(TestCase):
    def setUp(self):
        # inizializzazione istanze del modello MyUser
        first_user = MyUser(first_name='Roberto',
                            last_name='Moi',
                            username='65750',
                            password='abc123',
                            usertype='USER'
                            )
        first_user.save()

        second_user = MyUser(first_name='Simone',
                             last_name='Perria',
                             username='65733',
                             password='cde123',
                             usertype='GAMEDEVELOPER'
                             )
        second_user.save()

        third_user = MyUser(first_name='Francesco',
                            last_name='Simbola',
                            username='65697',
                            password='def123',
                            usertype='GAMEDEVELOPER')
        third_user.save()

        # inizializzazione istanze del modello Hero
        dragon = Hero(name='Dragon',
                      life=65,
                      attack=75,
                      defence=50
                      )
        dragon.save()

        knight = Hero(name='Knight',
                      life=50,
                      attack=80,
                      defence=55
                      )
        knight.save()

        archer = Hero(name='Archer',
                      life=70,
                      attack=75,
                      defence=45
                      )
        archer.save()

        # inizializzazione istanze del modello Equipment
        sword = Equipment(name='Sword',
                          role='Attack',
                          stat=15
                          )
        sword.save()

        arch = Equipment(name='Arch',
                         role='Attack',
                         stat=12
                         )
        arch.save()

        potion = Equipment(name='Potion',
                           role='Life',
                           stat=15
                           )
        potion.save()

        shield = Equipment(name='Shield',
                           role='Defence',
                           stat=20
                           )
        shield.save()

        # inizializzazione istanze del modello Boss
        elf = Boss(name='Elf',
                   life=65,
                   attack=45,
                   defence=70,
                   place='VALLE'
                   )
        elf.save()

        centaur = Boss(name='Centaur',
                       life=60,
                       attack=75,
                       defence=50,
                       place='GIUNGLA'
                       )
        centaur.save()

        hunter = Boss(name='Hunter',
                      life=80,
                      attack=67,
                      defence=60,
                      place='GIUNGLA'
                      )
        hunter.save()

        # inizializzazione istanze del modello BossEquipment
        hunter_potion = BossEquipment(enemy=hunter,
                                      equip=potion
                                      )
        hunter_potion.save()

        elf_shield = BossEquipment(enemy=elf,
                                   equip=shield
                                   )
        elf_shield.save()

        centaur_arch = BossEquipment(enemy=centaur,
                                     equip=arch
                                     )
        centaur_arch.save()

        # dotazione equipaggiamenti agli eroi
        dragon.equip = potion
        dragon.build_in_equipment()
        dragon.save()

        archer.equip = arch
        archer.build_in_equipment()
        archer.save()

        knight.equip = shield
        knight.build_in_equipment()
        knight.save()

    def test_myuser_model(self):
        self.assertEqual(len(MyUser.objects.all()), 3)

    def test_myuser_usertype(self):
        first_user = MyUser.objects.get(username='65750')
        # verifica che l'utente sia di tipo 'USER' e non 'GAMEDEVELOPER'
        self.assertNotEqual(first_user.usertype, 'GAMEDEVELOPER')
        self.assertEqual(first_user.usertype, 'USER')

    def test_hero_model(self):
        self.assertEqual(len(Hero.objects.all()), 3)

    def test_hero_build_equipment_model(self):
        # verifica se i valori dell'Eroe sono stati aggiornati correttamente dopo l'inserimento dell'equipaggiamento
        self.assertEqual(Hero.objects.get(name='Dragon').life, 80)
        self.assertEqual(Hero.objects.get(name='Archer').attack, 87)
        self.assertEqual(Hero.objects.get(name='Knight').defence, 75)

    def test_hero_remove_equipment_model(self):
        # rimozione equipaggiamento
        knight = Hero.objects.get(name='Knight')
        knight.remove_equipment()
        knight.equip = None
        knight.save()

        # verifica se i valori dell'Eroe sono stati aggiornati correttamente dopo la rimozione dell'equipaggiamento
        self.assertEqual(Hero.objects.get(name='Knight').defence, 55)

    def test_hero_battle(self):
        archer = Hero.objects.get(name='Archer')
        elf = Boss.objects.get(name='Elf')

        battle = archer.fight(elf)
        # se la battaglia va a buon fine la funzione restituirà "YOU WIN" se l'eroe vince o "YOU LOSE" se perde
        self.assertTrue(battle == 'YOU WIN' or battle == 'YOU LOSE')

    def test_equipment_model(self):
        self.assertEqual(len(Equipment.objects.all()), 4)

    def test_boss_model(self):
        self.assertEqual(len(Boss.objects.all()), 3)

    def test_boss_build_equipment(self):
        hunter = Boss.objects.get(name='Hunter')
        potion = Equipment.objects.get(name='Potion')
        hunter.build_equip(potion)
        hunter.save()
        # verifica se i valori del Boss sono stati aggiornati correttamente dopo l'inserimento dell'equipaggiamento
        self.assertEqual(hunter.life, 95)

    def test_bossequipment_model(self):
        self.assertEqual(len(BossEquipment.objects.all()), 3)
