# -*- encoding: utf-8 -*-

from models import User, Group, GroupList

from django.contrib import admin
from django import forms

class UserAdminForm(forms.ModelForm):
    """formulaire de gestion d'un abonné, avec gestion du champ 'password' spécifique"""

    class Meta:
        model = User

    # on veut que le champ "password" ne soit pas affiché en clair
    password = forms.CharField( widget=forms.PasswordInput(), label="Mot de passe" )
    # et on veut qu'il soit doublé d'un champ de vérifiation
    password_confirm = forms.CharField( widget=forms.PasswordInput(),
        label="Mot de passe (confirmation)",
	help_text="A utiliser en cas de nouveau mot de passe, ou de changement de mot de passe",
        required=False )

    def clean_password_confirm(self):
        # si le mot de passe a été modifié (c'est-à-dire est déjà crypté) alors
        # les deux mots de passe nouvellement fournis doivent être identiques
        password = self.cleaned_data.get('password','x')
        password_confirm = self.cleaned_data.get('password_confirm','x')
        if password == password_confirm or \
            ( ( password[0:3] == '$1$' or password == "x" ) and password_confirm == "" ):
            return None
        raise forms.ValidationError('Les deux mots de passe doivent être identiques.')

    def clean_username(self):
        """Vérification du format du username : lettres ASCII minuscules, chiffres, - . et _"""
        username_ok = 'abcdefghijklmnopqrstuvwxyz0123456789-._'
        username = self.cleaned_data['username']
        for c in username:
            if c not in username_ok:
                raise forms.ValidationError("Le nom d'utilisateur ne doit contenir que des lettres minuscules (sans accent), des chiffres et les caractères - _ et .")
        if not username[0].isalpha():
            raise forms.ValidationError("Le nom d'utilisateur doit commencer par une lettre")
        return username

    def clean_gecos(self):
        """Vérification du format du gecos : espace, lettres ASCII, chiffres, - . et _"""
        gecos_ok = ' abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._'
        gecos = self.cleaned_data['gecos']
        for c in gecos:
            if c not in gecos_ok:
                raise forms.ValidationError("Les informations GECOS ne doivent contenir que des lettres (sans accent), des chiffres et les caractères - _ et .")
        return gecos


class GroupListInline(admin.TabularInline):
    model = GroupList
    extra = 2
    verbose_name = "Groupes systèmes secondaires"
    verbose_name_plural = "Groupes systèmes secondaires"


class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm
    list_display = ( 'active', 'username' , 'gecos', 'colored_expire', 'uid', 'source', 'creation', 'modification')
    list_display_links = ( 'username' , 'gecos', 'uid', )
    list_filter = ( 'source', 'creation', 'modification' )
    search_fields = [ 'username', 'gecos', ]
    fieldsets = (
        ( None, 
            { 'fields': ( 'username' ,
                          ('password', 'password_confirm',),
                          'expire', 'gecos', ), }
        ),
        ( "Données destinées au système", 
            { 'fields': ( 'homedir', 'shell', 'uid', 'gid', ),
              'classes': ( 'collapse', ), }
        ),
        ( "Données de gestion", 
            { 'fields': ( 'source', ),
              'classes': ( 'collapse', ), }
        ),
    )
    ordering = ( '-modification', )
    inlines = [GroupListInline]
    # on conserve l'agent qui a rempli le formulaire web dans user.agent
    # voir http://docs.djangoproject.com/en/1.0/ref/contrib/admin/#modeladmin-methods
    def save_model(self, request, user, form, change):
        user.agent = request.user
        user.save()
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.agent = request.user
            instance.save()
        formset.save_m2m()


admin.site.register(User, UserAdmin)
admin.site.register(Group)

