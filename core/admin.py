from django.contrib import admin
from core.models import Transaction,CreditCard, SupportCase,Contact

class TransactionAdmin(admin.ModelAdmin):
    list_editable = ['amount', 'status', 'transaction_type', 'reciever', 'sender']
    list_display = ['user', 'amount', 'status', 'transaction_type', 'reciever', 'sender']

class CreditCardAdmin(admin.ModelAdmin):
    list_editable = ['amount', 'card_type']
    list_display = ['user', 'amount', 'card_type']

class SupportCaseAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'created_at']

class ContactAdmin(admin.ModelAdmin):
    list_display = ['user', 'contact_name', 'account_number']
    list_filter = ['user']


# Register your models here.
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(CreditCard,CreditCardAdmin)
admin.site.register(SupportCase, SupportCaseAdmin)
admin.site.register(Contact,ContactAdmin)