from django.contrib import admin

from .models import (
    Buyer,
    Seller,
    Book,
    Purchase,
    Review,
    WithdrawalRequest,
    SupportMessage,
    PaymentSettings
)


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):

    list_display = (
        'full_name',
        'email',
        'username',
        'approved',
        'wallet_balance',
        'profile_photo'
    )

    list_editable = (
        'approved',
    )

    list_filter = (
        'approved',
    )

    search_fields = (
        'full_name',
        'email',
        'username'
    )

    fields = (
        'full_name',
        'email',
        'phone',
        'aadhaar',
        'address',
        'username',
        'password',
        'approved',
        'wallet_balance',
        'upi_id',
        'profile_photo'
    )


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):

    list_display = (
        'buyer',
        'book',
        'purchase_date',
        'payment_approved',
        'payment_rejected',
        'download_count'
    )

    list_editable = (
        'payment_approved',
        'payment_rejected'
    )

    list_filter = (
        'payment_approved',
        'payment_rejected'
    )

    search_fields = (
        'buyer__username',
        'book__title'
    )

    fields = (
        'buyer',
        'book',
        'payment_approved',
        'payment_rejected',
        'reject_reason',
        'download_count'
    )

    def save_model(
        self,
        request,
        obj,
        form,
        change
    ):

        old_obj = None

        if obj.pk:

            old_obj = Purchase.objects.get(
                pk=obj.pk
            )

        if (
            obj.payment_approved and
            (
                not old_obj or
                not old_obj.payment_approved
            )
        ):

            seller = obj.book.seller

            seller.wallet_balance += obj.book.price

            seller.save()

        super().save_model(
            request,
            obj,
            form,
            change
        )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'category',
        'price',
        'seller',
        'approved',
        'rejected'
    )

    list_editable = (
        'approved',
        'rejected'
    )

    list_filter = (
        'approved',
        'rejected',
        'category'
    )

    search_fields = (
        'title',
        'category',
        'seller__full_name'
    )

    fields = (
        'title',
        'category',
        'price',
        'description',
        'pdf_file',
        'cover_image',
        'seller',
        'approved',
        'rejected',
        'reject_reason'
    )


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):

    list_display = (
        'username',
        'email'
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        'book',
        'buyer',
        'rating',
        'created_at'
    )


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):

    list_display = (
        'seller',
        'amount',
        'upi_id',
        'approved',
        'rejected',
        'request_date'
    )

    list_editable = (
        'approved',
        'rejected'
    )

    list_filter = (
        'approved',
        'rejected'
    )

    search_fields = (
        'seller__full_name',
        'upi_id'
    )


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'email',
        'user_type',
        'subject',
        'created_at'
    )

    search_fields = (
        'name',
        'email',
        'subject'
    )

    list_filter = (
        'user_type',
    )


# ================= PAYMENT SETTINGS =================

@admin.register(PaymentSettings)
class PaymentSettingsAdmin(admin.ModelAdmin):

    list_display = (
        'admin_upi',
    )