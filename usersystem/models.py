from django.db import models


class Buyer(models.Model):

    full_name = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    username = models.CharField(
        max_length=100,
        unique=True
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    profile_photo = models.ImageField(
        upload_to='buyer_profiles/',
        blank=True,
        null=True
    )

    password = models.CharField(
        max_length=100
    )

    joined_date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.username


class Seller(models.Model):

    full_name = models.CharField(
        max_length=200
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=20
    )

    aadhaar = models.CharField(
        max_length=20
    )

    address = models.TextField()

    username = models.CharField(
        max_length=100,
        unique=True
    )

    password = models.CharField(
        max_length=100
    )

    approved = models.BooleanField(
        default=False
    )

    profile_photo = models.ImageField(
        upload_to='seller_profiles/',
        blank=True,
        null=True
    )

    upi_id = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    wallet_balance = models.IntegerField(
        default=0
    )

    def __str__(self):

        return self.full_name


class Book(models.Model):

    title = models.CharField(
        max_length=200
    )

    category = models.CharField(
        max_length=100
    )

    price = models.IntegerField()

    description = models.TextField()

    # PDF LINK (MEGA LINK)

    pdf_file = models.URLField()

    # COVER IMAGE URL (ImgBB)

    cover_image = models.URLField(
        blank=True,
        null=True
    )

    seller = models.ForeignKey(
        Seller,
        on_delete=models.CASCADE
    )

    approved = models.BooleanField(
        default=False
    )

    rejected = models.BooleanField(
        default=False
    )

    reject_reason = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):

        return self.title


class Purchase(models.Model):

    buyer = models.ForeignKey(
        Buyer,
        on_delete=models.CASCADE
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE
    )

    purchase_date = models.DateTimeField(
        auto_now_add=True
    )

    payment_approved = models.BooleanField(
        default=False
    )

    payment_rejected = models.BooleanField(
        default=False
    )

    utr_number = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    payment_screenshot = models.URLField(
    blank=True,
    null=True
    )

    reject_reason = models.TextField(
        blank=True,
        null=True
    )

    download_count = models.IntegerField(
        default=0
    )

    def __str__(self):

        return self.buyer.username


class Review(models.Model):

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE
    )

    buyer = models.ForeignKey(
        Buyer,
        on_delete=models.CASCADE
    )

    rating = models.IntegerField()

    comment = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.book.title


class WithdrawalRequest(models.Model):

    seller = models.ForeignKey(
        Seller,
        on_delete=models.CASCADE
    )

    amount = models.IntegerField()

    upi_id = models.CharField(
        max_length=200
    )

    approved = models.BooleanField(
        default=False
    )

    rejected = models.BooleanField(
        default=False
    )

    request_date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.seller.full_name


class SupportMessage(models.Model):

    USER_TYPE = (
        ('Buyer', 'Buyer'),
        ('Seller', 'Seller'),
    )

    name = models.CharField(
        max_length=200
    )

    email = models.EmailField()

    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE
    )

    subject = models.CharField(
        max_length=300
    )

    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.subject


# ================= PAYMENT SETTINGS =================

class PaymentSettings(models.Model):

    admin_upi = models.CharField(
        max_length=200
    )

    def __str__(self):

        return self.admin_upi


# ================= SITE SETTINGS =================

class SiteSettings(models.Model):

    site_logo = models.ImageField(
        upload_to='logos/',
        blank=True,
        null=True
    )

    def __str__(self):

        return "Site Settings"