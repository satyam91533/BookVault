from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from django.shortcuts import render, redirect
from django.http import FileResponse

from usersystem.models import (
    Buyer,
    Seller,
    Book,
    Purchase,
    Review,
    WithdrawalRequest,
    SupportMessage,
    PaymentSettings,
    SiteSettings
)

# ================= HOME =================

def home(request):

    settings_obj = SiteSettings.objects.first()

    search = request.GET.get(
        'search'
    )

    category = request.GET.get(
        'category'
    )

    books = Book.objects.filter(
        approved=True
    )

    # ================= SEARCH =================

    if search:

        books = books.filter(
            title__icontains=search
        )

    # ================= CATEGORY =================

    if category:

        books = books.filter(
            category=category
        )

    return render(request, 'home.html', {

        'books': books,
        
        'settings_obj': settings_obj,

    })

# ================= BUYER SIGNUP =================

def buyer_signup(request):

    error = ""

    success = False

    if request.method == "POST":

        username = request.POST.get(
            'username'
        )

        if Buyer.objects.filter(
            username=username
        ).exists():

            error = "Username already exists"

        else:

            buyer = Buyer.objects.create(

                full_name=request.POST.get(
                    'full_name'
                ),

                username=username,

                email=request.POST.get(
                    'email'
                ),

                phone=request.POST.get(
                    'phone'
                ),

                password=request.POST.get(
                    'password'
                )

            )

            if request.FILES.get(
                'profile_photo'
            ):

                buyer.profile_photo = request.FILES.get(
                    'profile_photo'
                )

                buyer.save()

            success = True

    return render(request, 'buyer_signup.html', {

        'success': success,

        'error': error

    })


# ================= BUYER LOGIN =================

def login_view(request):

    error = ""

    if request.method == "POST":

        username = request.POST.get('username')

        password = request.POST.get('password')

        try:

            buyer = Buyer.objects.get(
                username=username,
                password=password
            )

            request.session.flush()

            request.session['buyer_id'] = buyer.id

            return redirect('/buyer-profile/')

        except Buyer.DoesNotExist:

            error = "Invalid Username or Password"

    return render(request, 'login.html', {
        'error': error
    })

# ================= LOGOUT =================

def logout_view(request):

    request.session.flush()

    return redirect('/')


# ================= BUYER PROFILE =================

def buyer_profile(request):

    buyer_id = request.session.get('buyer_id')

    if not buyer_id:

        return redirect('/login/')

    buyer = Buyer.objects.get(
        id=buyer_id
    )

    purchases = Purchase.objects.filter(
        buyer=buyer
    )

    approved_count = purchases.filter(
        payment_approved=True
    ).count()

    rejected_count = purchases.filter(
        payment_rejected=True
    ).count()

    pending_count = purchases.filter(
        payment_approved=False,
        payment_rejected=False
    ).count()

    downloaded_count = 0

    for purchase in purchases:

        downloaded_count += purchase.download_count

    return render(request, 'buyer_profile.html', {

        'buyer': buyer,

        'purchases': purchases,

        'approved_count': approved_count,

        'rejected_count': rejected_count,

        'pending_count': pending_count,

        'downloaded_count': downloaded_count

    })


# ================= EDIT BUYER PROFILE =================

def edit_buyer_profile(request):

    buyer_id = request.session.get('buyer_id')

    if not buyer_id:

        return redirect('/login/')

    buyer = Buyer.objects.get(
        id=buyer_id
    )

    if request.method == "POST":

        buyer.full_name = request.POST.get(
            'full_name'
        )

        buyer.phone = request.POST.get(
            'phone'
        )

        if request.FILES.get('profile_photo'):

            buyer.profile_photo = request.FILES.get(
                'profile_photo'
            )

        buyer.save()

        return redirect('/buyer-profile/')

    return render(request, 'edit_buyer_profile.html', {
        'buyer': buyer
    })


# ================= MY PURCHASES =================

def my_purchases(request):

    buyer_id = request.session.get('buyer_id')

    if not buyer_id:

        return redirect('/login/')

    buyer = Buyer.objects.get(
        id=buyer_id
    )

    purchases = Purchase.objects.filter(
        buyer=buyer
    )

    return render(request, 'my_purchases.html', {
        'purchases': purchases
    })


# ================= BOOK DETAILS =================

def book_details(request, id):

    book = Book.objects.get(
        id=id,
        approved=True
    )

    reviews = Review.objects.filter(
        book=book
    ).order_by('-created_at')

    buyer_id = request.session.get(
        'buyer_id'
    )

    purchased = False

    already_reviewed = False

    if buyer_id:

        buyer = Buyer.objects.get(
            id=buyer_id
        )

        # ================= PURCHASE CHECK =================

        purchased = Purchase.objects.filter(
            buyer=buyer,
            book=book
        ).exists()

        # ================= REVIEW CHECK =================

        already_reviewed = Review.objects.filter(
            buyer=buyer,
            book=book
        ).exists()

        # ================= ADD REVIEW =================

        if (
            request.method == "POST"
            and purchased
            and not already_reviewed
        ):

            rating = request.POST.get(
                'rating'
            )

            comment = request.POST.get(
                'comment'
            )

            Review.objects.create(

                book=book,

                buyer=buyer,

                rating=int(rating),

                comment=comment

            )

            return redirect(
                f'/book-details/{book.id}/'
            )

    return render(request, 'book_details.html', {

        'book': book,

        'reviews': reviews,

        'purchased': purchased,

        'already_reviewed': already_reviewed

    })
# ================= BUY BOOK =================

def buy_book(request, id):

    buyer_id = request.session.get(
        'buyer_id'
    )

    if not buyer_id:

        return redirect('/login/')

    book = Book.objects.get(
        id=id
    )

    # ================= GET ADMIN UPI =================

    payment_settings = PaymentSettings.objects.first()

    admin_upi = payment_settings.admin_upi

    # ================= QR DATA =================

    qr_data = f"""
upi://pay?pa={admin_upi}&pn=BookVault&am={book.price}&cu=INR
"""

    return render(request, 'payment.html', {

        'book': book,

        'admin_upi': admin_upi,

        'qr_data': qr_data

    })


# ================= PAYMENT SUCCESS =================

def payment_success(request, book_id):

    if request.method == 'POST':

        buyer_id = request.session.get(
            'buyer_id'
        )

        if not buyer_id:

            return redirect('/login/')

        buyer = Buyer.objects.get(
            id=buyer_id
        )

        book = Book.objects.get(
            id=book_id
        )

        utr_number = request.POST.get(
            'utr_number'
        )

        payment_screenshot = request.FILES.get(
            'payment_screenshot'
        )

        Purchase.objects.create(

            buyer=buyer,

            book=book,

            utr_number=utr_number,

            payment_screenshot=payment_screenshot,

            payment_approved=False

        )

        return render(
            request,
            'payment_pending.html'
        )

    return redirect('/')
# ================= DOWNLOAD BOOK =================

def download_book(request, id):

    buyer_id = request.session.get(
        'buyer_id'
    )

    if not buyer_id:

        return redirect('/login/')

    purchase = Purchase.objects.get(
        id=id
    )

    if not purchase.payment_approved:

        return render(
            request,
            'payment_pending.html'
        )

    if purchase.download_count >= 3:

        return render(
            request,
            'download_limit.html'
        )

    purchase.download_count += 1

    purchase.save()

    # REDIRECT TO MEGA PDF LINK

    return redirect(
        purchase.book.pdf_file
    )

# ================= SELLER SIGNUP =================

def seller_signup(request):

    success = False

    error = ""

    if request.method == "POST":

        username = request.POST.get('username')

        if Seller.objects.filter(
            username=username
        ).exists():

            error = "Username already exists"

        else:

            seller = Seller.objects.create(

                full_name=request.POST.get(
                    'full_name'
                ),

                email=request.POST.get(
                    'email'
                ),

                phone=request.POST.get(
                    'phone'
                ),

                aadhaar=request.POST.get(
                    'aadhaar'
                ),

                address=request.POST.get(
                    'address'
                ),

                username=username,

                password=request.POST.get(
                    'password'
                ),

                upi_id=request.POST.get(
                    'upi_id'
                )

            )

            if request.FILES.get(
                'profile_photo'
            ):

                seller.profile_photo = request.FILES.get(
                    'profile_photo'
                )

                seller.save()

            success = True

    return render(request, 'seller_signup.html', {
        'success': success,
        'error': error
    })


# ================= SELLER LOGIN =================

def seller_login(request):

    error = ""

    if request.method == "POST":

        username = request.POST.get('username')

        password = request.POST.get('password')

        try:

            seller = Seller.objects.get(
                username=username,
                password=password
            )

            if not seller.approved:

                error = "Seller account not approved"

            else:

                request.session.flush()

                request.session['seller_id'] = seller.id

                return redirect('/seller-dashboard/')

        except:

            error = "Invalid Username or Password"

    return render(request, 'seller_login.html', {
        'error': error
    })


# ================= SELLER DASHBOARD =================

import requests
import base64
from django.conf import settings


def seller_dashboard(request):

    seller_id = request.session.get('seller_id')

    if not seller_id:

        return redirect('/seller-login/')

    seller = Seller.objects.get(
        id=seller_id
    )

    seller_books = Book.objects.filter(
        seller=seller
    )

    seller_purchases = Purchase.objects.filter(
        book__seller=seller,
        payment_approved=True
    )

    total_books = seller_books.count()

    total_sales = seller_purchases.count()

    earnings = seller.wallet_balance

    withdrawals = WithdrawalRequest.objects.filter(
        seller=seller
    ).order_by('-request_date')

    error = ""

    # ================= POST ACTIONS =================

    if request.method == "POST":

        # ================= BOOK UPLOAD =================

        if request.POST.get('upload_book'):

            title = request.POST.get('title')

            category = request.POST.get('category')

            price = request.POST.get('price')

            description = request.POST.get('description')

            # MEGA LINK

            pdf_file = request.POST.get('pdf_file')

            # IMAGE FILE

            cover_image = request.FILES.get('cover_image')

            # ================= IMAGE SIZE LIMIT =================

            if (
                cover_image and
                cover_image.size > 10 * 1024 * 1024
            ):

                error = "Image size must be under 10 MB"

            elif (
                title and
                category and
                price and
                description and
                pdf_file and
                cover_image
            ):

                # ================= IMGBB UPLOAD =================

                image_data = base64.b64encode(
                    cover_image.read()
                )

                response = requests.post(

                    "https://api.imgbb.com/1/upload",

                    data={

                        "key": settings.IMGBB_API_KEY,

                        "image": image_data

                    }

                )

                result = response.json()

                image_url = result['data']['url']

                # ================= SAVE BOOK =================

                Book.objects.create(

                    title=title,

                    category=category,

                    price=int(price),

                    description=description,

                    pdf_file=pdf_file,

                    cover_image=image_url,

                    seller=seller,

                    approved=False

                )

                return redirect('/seller-dashboard/')

        # ================= WITHDRAW REQUEST =================

        withdraw_amount = request.POST.get(
            'withdraw_amount'
        )

        if withdraw_amount:

            withdraw_amount = int(
                withdraw_amount
            )

            # ================= CHECK BALANCE =================

            if withdraw_amount > seller.wallet_balance:

                error = "Insufficient wallet balance"

            else:

                WithdrawalRequest.objects.create(

                    seller=seller,

                    amount=withdraw_amount,

                    upi_id=seller.upi_id

                )

                # ================= DEDUCT WALLET =================

                seller.wallet_balance -= withdraw_amount

                seller.save()

                return redirect('/seller-dashboard/')

        # ================= SAVE UPI =================

        upi_id = request.POST.get('upi_id')

        if upi_id:

            seller.upi_id = upi_id

            seller.save()

            return redirect('/seller-dashboard/')

    return render(request, 'seller_dashboard.html', {

        'seller': seller,

        'total_books': total_books,

        'total_sales': total_sales,

        'earnings': earnings,

        'seller_books': seller_books,

        'seller_purchases': seller_purchases,

        'withdrawals': withdrawals,

        'error': error

    })


# ================= EDIT BOOK =================

def edit_book(request, id):

    seller_id = request.session.get(
        'seller_id'
    )

    if not seller_id:

        return redirect('/seller-login/')

    seller = Seller.objects.get(
        id=seller_id
    )

    book = Book.objects.get(
        id=id,
        seller=seller
    )

    error = ""

    if request.method == "POST":

        book.title = request.POST.get('title')

        book.category = request.POST.get('category')

        book.price = request.POST.get('price')

        book.description = request.POST.get('description')

        # MEGA LINK

        book.pdf_file = request.POST.get(
            'pdf_file'
        )

        # NEW IMAGE

        if request.FILES.get('cover_image'):

            cover_image = request.FILES.get(
                'cover_image'
            )

            if (
                cover_image.size >
                10 * 1024 * 1024
            ):

                error = "Image size must be under 10 MB"

            else:

                image_data = base64.b64encode(
                    cover_image.read()
                )

                response = requests.post(

                    "https://api.imgbb.com/1/upload",

                    data={

                        "key": settings.IMGBB_API_KEY,

                        "image": image_data

                    }

                )

                result = response.json()

                image_url = result['data']['url']

                book.cover_image = image_url

        book.approved = False

        book.rejected = False

        book.reject_reason = ""

        book.save()

        return redirect('/seller-dashboard/')

    return render(request, 'edit_book.html', {

        'book': book,

        'error': error

    })

# ================= DELETE BOOK =================

def delete_book(request, id):

    seller_id = request.session.get(
        'seller_id'
    )

    if not seller_id:

        return redirect('/seller-login/')

    seller = Seller.objects.get(
        id=seller_id
    )

    book = Book.objects.get(
        id=id,
        seller=seller
    )

    book.delete()

    return redirect('/seller-dashboard/')
# ================= ADMIN LOGO UPLOAD =================

def upload_site_logo(request):

    if not request.user.is_superuser:

        return redirect('/admin/login/')

    settings_obj, created = SiteSettings.objects.get_or_create(
        id=1
    )

    if request.method == "POST":

        logo = request.FILES.get(
            'site_logo'
        )

        if logo:

            image_data = base64.b64encode(
                logo.read()
            )

            response = requests.post(

                "https://api.imgbb.com/1/upload",

                data={

                    "key": settings.IMGBB_API_KEY,

                    "image": image_data

                }

            )

            result = response.json()

            image_url = result['data']['url']

            settings_obj.site_logo = image_url

            settings_obj.save()

    return render(request, 'upload_logo.html', {

        'settings_obj': settings_obj

    })


# ================= PRIVACY POLICY =================

def privacy_policy(request):

    return render(
        request,
        'privacy_policy.html'
    )


# ================= TERMS =================

def terms_conditions(request):

    return render(
        request,
        'terms_conditions.html'
    )


# ================= SUPPORT =================

def support(request):

    success = False

    if request.method == "POST":

        SupportMessage.objects.create(

            name=request.POST.get('name'),

            email=request.POST.get('email'),

            user_type=request.POST.get('user_type'),

            subject=request.POST.get('subject'),

            message=request.POST.get('message')

        )

        success = True

    return render(request, 'support.html', {
        'success': success
    })


# ================= URLS =================

urlpatterns = [

    path(
        'admin/upload-logo/',
        upload_site_logo
    ),

    path('admin/', admin.site.urls),

    path('', home),

    path(
        'buyer-signup/',
        buyer_signup
    ),

    path('login/', login_view),

    path('logout/', logout_view),

    path('buyer-profile/', buyer_profile),

    path(
        'edit-buyer-profile/',
        edit_buyer_profile
    ),

    path(
        'my-purchases/',
        my_purchases
    ),

    path(
        'book-details/<int:id>/',
        book_details
    ),

    path(
        'buy-book/<int:id>/',
        buy_book
    ),

    path(
        'payment-success/<int:book_id>/',
        payment_success
    ),

    path(
        'download-book/<int:id>/',
        download_book
    ),

    path(
        'become-seller/',
        seller_signup
    ),

    path(
        'seller-login/',
        seller_login
    ),

    path(
        'seller-dashboard/',
        seller_dashboard
    ),

    path(
        'edit-book/<int:id>/',
        edit_book
    ),

    path(
        'delete-book/<int:id>/',
        delete_book
    ),

    path(
        'privacy-policy/',
        privacy_policy
    ),

    path(
        'terms-conditions/',
        terms_conditions
    ),

    path(
        'support/',
        support
    ),

]

# ================= MEDIA =================

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )