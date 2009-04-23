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
            { 'fields': ( 'homedir', 'shell', 'gid', ),
              'classes': ( 'collapse', ), }
        ),
        ( "Données de gestion", 
            { 'fields': ( 'source', ),
              'classes': ( 'collapse', ), }
        ),
    )
    ordering = ( '-modification', )
    inlines = [GroupListInline]


admin.site.register(User, UserAdmin)
admin.site.register(Group)

