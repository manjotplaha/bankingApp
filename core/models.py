import uuid

from django.db import models
from userauths.models import User
from account.models import Account
from shortuuid.django_fields import ShortUUIDField
from django.db.models import UniqueConstraint

TRANSACTION_TYPE = (
    ("transfer", "Transfer"),
    ("recieved", "Recieved"),
    ("withdraw", "withdraw"),
    ("refund", "Refund"),
    ("request", "Payment Request"),
    ("none", "None")
)

TRANSACTION_STATUS = (
    ("failed", "failed"),
    ("completed", "completed"),
    ("pending", "pending"),
    ("processing", "processing"),
    ("request_sent", "request_sent"),
    ("request_settled", "request settled"),
    ("request_processing", "request processing"),

)
CARD_TYPE = (
    ("visa", "visa"),
    ("master", "master"),
    )


class Transaction(models.Model):
    transaction_id = ShortUUIDField(unique=True, length=15, max_length=20, prefix="TRN")

    # the user who initiated the transaction
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="user")
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    description = models.CharField(max_length=1000, null=True, blank=True)

    # the user who recieved the transaction
    reciever = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="reciever")
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="sender")

    reciever_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="reciever_account")
    sender_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="sender_account")

    status = models.CharField(choices=TRANSACTION_STATUS, max_length=100, default="pending")
    transaction_type = models.CharField(choices=TRANSACTION_TYPE, max_length=100, default="none")

    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    def __str__(self):
        try:
            return f"{self.user}"
        except:
            return f"Transaction"


class CreditCard(models.Model):
    user= models.ForeignKey(User,on_delete=models. CASCADE)
    card_id = ShortUUIDField(unique=True,length=5, max_length=20, prefix="CARD", alphabet="1234567890")

    name= models.CharField(max_length=100)

    number = models. IntegerField()
    month = models. IntegerField()
    year = models. IntegerField()
    cvv = models. IntegerField()

    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    card_type = models.CharField(choices=CARD_TYPE, max_length=20, default="master")
    card_status = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}"

class SupportCase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.id:
            # Generate Case ID if not provided
            self.id = uuid.uuid4()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Case ID: {self.id} - Created At:{self.created_at} "

    class Meta:
        ordering = ['created_at']



class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contact_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=13)

    # class Meta:
    #     unique_together =('contact_name', 'account_number')
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'contact_name'],
                name='unique_user_contact_name'
            ),
            UniqueConstraint(
                fields=['user', 'account_number'],
                name='unique_user_account_number'
            ),
        ]

    def delete_contact(self):
        self.delete()

    def __str__(self):
        return self.user
