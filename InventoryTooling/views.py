from django.conf import settings
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DetailView, TemplateView, DeleteView, FormView
from .models import ModelProduct, ModelLocation, ModelTempProdLoc, ModelTransaction, ModelUserUID
from django.urls import reverse, reverse_lazy
from django.db.models import Q, Sum, Count, Case, When, Min, Max, F
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.forms import formset_factory, ModelForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime, date
from django.utils import timezone
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from .forms import CustomUserCreationForm, UpdatePasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm

location = ModelLocation.objects.all()
produk = ModelProduct.objects.all()
temporary = ModelTempProdLoc.objects.all()
transaksi = ModelTransaction.objects.all()
user_uid = ModelUserUID.objects.all()
user_django = User.objects.all() # Model user dari default django
title = "Tooling - "


# Templateview, CreateView, UpdateView pakai get_context_data, listview pakai get_queryset
# Create your views here.

# view as superuser
class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


# view as staff or superuser
class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class PageTitleViewMixin:
    # title = ""

    def get_title(self):
        # title = "Tooling"
        return self.title

    def get_header(self):
        # title = "Tooling"
        return self.header

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.get_title()
        context['header'] = self.get_header()
        return context

# register & login logout sign up
class SignupPageView(SuperuserRequiredMixin, PageTitleViewMixin, CreateView):
    form_class = CustomUserCreationForm
    #  success_url = reverse_lazy("LoginPageView")
    template_name = "registration/signup_view.html"
    title = title + 'Sign Up'
    header = title

    def get_success_url(self, **kwargs):
        messages.add_message(self.request, messages.SUCCESS, "User added successfully.")
        return reverse_lazy("ViewUser")


class LoginPageView(PageTitleViewMixin, LoginView):
    template_name = 'registration/signin_view.html'
    title = title + 'Sign In'
    header = title
    redirect_authenticated_user = True

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            username = request.POST.get('usernm')
            password = request.POST.get('passwd')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('MainMenu')
                else:
                    messages.add_message(self.request, messages.ERROR, "Inactive user.")
                    return HttpResponseRedirect(reverse('LoginPageView'))
            else:
                messages.add_message(self.request, messages.ERROR, "Invalid credentials.")
                return HttpResponseRedirect(reverse('LoginPageView'))

        return redirect('Dashboard')


class LogoutPageView(LogoutView):
    def get(self, request):
        logout(request)
        # return render(request, "your logout page");
        return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)


class ChangePassPageView(StaffRequiredMixin, PageTitleViewMixin, FormView):
    form_class = UpdatePasswordForm
    title = title + 'Profile'
    header = title + ' / ' + 'Change Password'
    template_name = 'registration/pass_change.html'
    model = User

    def get_form_kwargs(self):
        kwargs = super(ChangePassPageView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        if self.request.method == 'POST':
            kwargs['data'] = self.request.POST
        return kwargs

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "Please correct the error below.")
        return super(ChangePassPageView, self).form_invalid(form)

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        # return super(ChangePassPageView, self).form_valid(form)
        messages.add_message(self.request, messages.SUCCESS, "Your password was successfully updated!.")
        return redirect(reverse('LogoutPageView'))


class ResetPassPageView(PageTitleViewMixin, UpdateView):
    template_name = 'registration/pass_reset.html'
    title = title + 'User'
    header = title + ' / ' + 'Reset password'
    context_object_name = 'data'
    model = User
    fields = ['username']

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            username = request.POST.get('usernm')
            password1 = request.POST.get('passwd1')
            password2 = request.POST.get('passwd2')
            if password1 == password2:
                this_user = User.objects.get(username=username)
                this_user.set_password(password2)
                this_user.save()
                messages.add_message(self.request, messages.SUCCESS, "Your password was successfully updated!.")
                return redirect(reverse('PageView'))


class ViewUser(SuperuserRequiredMixin, PageTitleViewMixin, ListView):
    template_name = 'registration/user_list.html'
    title = title + 'User'
    header = title + ' / ' + 'Accounts list'
    context_object_name = 'object_list'
    model = User
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total = user_django
        active = user_django.filter(is_active=True)
        blocked = user_django.all().filter(is_active=False)

        if total:
            context['total'] = total.count()
            context['active'] = active.count()
            context['blocked'] = blocked.count()
            context['data_uid'] = user_uid
        return context


class ResultUser(PageTitleViewMixin, ListView):
    template_name = 'registration/user_list.html'
    title = title + 'User'
    header = title + ' / ' + 'Accounts list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total = user_django
        active = user_django.filter(is_active=True)
        blocked = user_django.filter(is_active=False)
        if total:
            context['total'] = total.count()
            context['active'] = active.count()
            context['blocked'] = blocked.count()
        return context

    def get_queryset(self):  # http://shopnilsazal.github.io/django-pagination-with-basic-search/
        posts_list = user_django
        a = self.request.GET.get('name')
        b = self.request.GET.get('username')
        c = self.request.GET.get('level')
        d = self.request.GET.get('status')

        if a:
            posts_list = user_django.filter(first_name__icontains=a)
        elif b:
            posts_list = user_django.filter(username__icontains=b)
        elif c == "SUP":
            posts_list = user_django.filter(is_superuser=True, is_staff=False)
        elif c == "ADM":
            posts_list = user_django.filter(is_superuser=False, is_staff=True)
        elif c == "STD":
            posts_list = user_django.filter(is_superuser=False, is_staff=False)
        elif d:
            posts_list = user_django.filter(is_active=d)

        #
        elif c == "SUP" and d:
            posts_list = user_django.filter(is_superuser=True, is_staff=True, is_active=d)
        elif c == "ADM" and d:
            posts_list = user_django.filter(is_superuser=False, is_staff=True, is_active=d)
        elif c == "STD" and d:
            posts_list = user_django.filter(is_superuser=False, is_staff=False, is_active=d)

        paginator = Paginator(posts_list, 5)  # 5 posts per page
        page = self.request.GET.get('page')

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        return page_obj


'''class EditUser(SuperuserRequiredMixin, UpdateView):
    template_name = 'user_edit.html'
    model = ModelUser
    fields = ['qty_adj', 'status_adj', 'qty']
    context_object_name = 'data'''''


class EditUser(SuperuserRequiredMixin, PageTitleViewMixin, UpdateView):
    template_name = 'registration/user_edit.html'
    title = title + 'User'
    header = title + ' / ' + 'Update account'
    model = User
    # form_class = CustomUserCreationForm
    fields = ['first_name', 'username', 'is_superuser', 'is_staff', 'is_active']
    context_object_name = 'data'
    success_url = reverse_lazy('ViewUser')


class DeleteUser(SuperuserRequiredMixin, DeleteView):
    model = User
    success_url = reverse_lazy('ViewUser')

# sampai sini ya view user account & registration


# rfid uid
class ViewUserUID(SuperuserRequiredMixin, PageTitleViewMixin, ListView):
    template_name = 'registration/user_uid/uid_user_list.html'
    title = title + 'User UID'
    header = title + ' / ' + 'UID users list'
    context_object_name = 'object_list'
    model = ModelUserUID
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total = user_uid.filter(usernm__isnull=False)
        active = user_uid.filter(status=True)
        blocked = user_uid.filter(status=False)
        if total:
            context['total'] = total.count()
            context['active'] = active.count()
            context['blocked'] = blocked.count()
        return context


class AddUserUID(SuperuserRequiredMixin, PageTitleViewMixin, CreateView):
    template_name = 'registration/user_uid/uid_user_add.html'
    title = title + 'User UID'
    header = title + ' / ' + 'Create UID user'
    model = ModelUserUID
    context_object_name = 'data'
    fields = ['nik', 'nm_krywn', 'usernm', 'dept', 'level', 'uid']
    success_url = reverse_lazy('ViewUserUID')


'''class AddUserUID(SuperuserRequiredMixin, CreateView):
    template_name = 'uid_user_add.html'
    model = ModelUserUID
    context_object_name = 'data'
    fields = ['no_card', 'nik', 'nm_krywn', 'dept', 'usernm', 'passwd', 'level']
    success_url = reverse_lazy('ViewUser')'''


class EditUserUID(SuperuserRequiredMixin, UpdateView):
    template_name = 'uid_user_edit.html'
    model = ModelUserUID
    fields = ['nik', 'nm_krywn', 'usernm', 'dept', 'level', 'uid']
    context_object_name = 'data'
    success_url = reverse_lazy('ViewUserUID')


class DeleteUserUID(SuperuserRequiredMixin, DeleteView):
    model = ModelUserUID
    success_url = reverse_lazy('ViewUserUID')


class Dashboard(PageTitleViewMixin, ListView):
    template_name = 'dashboard.html'
    title = title + 'Dashboard'
    header = title
    context_object_name = 'data'
    model = ModelTempProdLoc

    def get_queryset(self):
        object_list = temporary.values('prod_code', 'prod_code__prod_desc', 'prod_code__stock_min',
                                       'prod_code__stock_max').annotate(sum=Sum('qty')).order_by('prod_code')
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context['chart_free'] = location.filter(status='FL').count()
            context['chart_used'] = location.filter(Q(status='UL') | Q(status='HU')).count()
            # context['chart_held'] = location.filter(status='HU').count()

            #  by step
            # a = temporary.annotate(total=Sum('qty')) # ini menampilkan  <QuerySet [<ModelTempProdLoc: ModelTempProdLoc object (09613201123)>, dst
            # a = temporary.values('prod_code').annotate(total=Sum('qty')) # ini menampilkan <QuerySet [{'prod_code': 'NI-EX-F02', 'total': 6}, dst sort by prod_code

            # a = temporary.values('prod_code', 'prod_code__stock_min').annotate(all_sum=Sum('qty')).aggregate(level_min=Count('all_sum'))
            # a = temporary.aggregate(Sum('qty')).get('qty__sum', 0.00) # menampilkan sum aja tanpa ket

            # a = temporary.values('prod_code').annotate(total=Sum('qty')).aggregate(level=Count('total')).get('level', 0.00)
            # crit = temporary.filter(qty__lte=F('prod_code__stock_min')).count # stok sama dengan / dibawah min
            # safe = temporary.filter(qty__gt=F('prod_code__stock_min'), qty__lte=F('prod_code__stock_max')).count
            # surp = temporary.filter(qty__gt=F('prod_code__stock_max')).count
            surp = temporary.values('prod_code').annotate(
                total=Sum('qty')).filter(prod_code__status="ACTIVE", total__gt=F('prod_code__stock_max')).count()

            safe = temporary.values('prod_code').annotate(
                total=Sum('qty')).filter(prod_code__status="ACTIVE", total__gt=F('prod_code__stock_min'),
                                         total__lte=F('prod_code__stock_max')).count()

            crit = temporary.values('prod_code').annotate(
                total=Sum('qty')).filter(prod_code__status="ACTIVE", total__gt=0,
                                         total__lte=F('prod_code__stock_min')).count()  # stok sama dengan / dibawah min
            # x = a.aggregate(level_min=Count('qty_sum'))  # hitung total sum kurang dari prod_code__stock_min
            # context['coba'] = a

            context['chart_surp'] = surp
            context['chart_safe'] = safe
            context['chart_crit'] = crit

            # Display lokasi free / used reserve & primary
            tot_pri = location.filter(assign='P').count()
            tot_rsv = location.filter(assign='R').count()

            # primary free
            context['chart_pri_fl'] = location.filter(assign='P', status='FL').count()
            context['pri_fl_cent'] = 100 * location.filter(assign='P', status='FL').count() / tot_pri

            # primary used
            context['chart_pri_ul'] = location.filter(assign='P', status='UL').count()
            context['pri_ul_cent'] = 100 * location.filter(assign='P', status='UL').count() / tot_pri

            # reserve free
            context['chart_rsv_fl'] = location.filter(assign='R', status='FL').count()
            context['rsv_fl_cent'] = 100 * location.filter(assign='R', status='FL').count() / tot_rsv

            # reserve used
            context['chart_rsv_ul'] = location.filter(Q(status='UL') | Q(status='HU'), assign='R').count()
            context['rsv_ul_cent'] = 100 * location.filter(Q(status='UL') | Q(status='HU'),
                                                           assign='R', ).count() / tot_rsv

            # Display demand (pengambilan part) by PCK AO
            demand = transaksi.values('prod_code').annotate(total=Count('prod_code')).filter(trans_type="PCK",
                                                                                             adj_type="AO").order_by(
                '-total')
            page_dem = self.request.GET.get('page')
            context['chart_dem'] = Paginator(demand, 5).get_page(page_dem)

            # Display last picked
            picked = transaksi.filter(trans_type='PCK', adj_type='AO').order_by('-date_created')
            page_pic = self.request.GET.get('page')
            context['chart_pic'] = Paginator(picked, 5).get_page(page_pic)

            # Display last recerived

            #  transaksi.values('prod_code').annotate(total=Count('prod_code'))
            # received = transaksi.filter(Q(ttb_stat='OR') | Q(ttb_stat='RE'), trans_type='TTB', adj_type='AI').order_by('-date_created')
            # max_year = transaksi.latest('date_created').date_created.month

            # expos = transaksi.filter(date__year=max_year)
            # received = transaksi.values('no_ttb').annotate(total=Count('no_ttb', filter=Q(date_created__date=now().date()))).filter(no_ttb__isnull=False)

            # sample Filtering on annotations¶
            # received = transaksi.values('no_ttb').annotate(total=Count('no_ttb', filter=Q(book__rating__gte=7))).filter(no_ttb__isnull=False).order_by('-id')

            received = transaksi.values('no_ttb').annotate(total=Count('no_ttb')).filter(no_ttb__isnull=False).order_by(
                '-total')
            page_rcvd = self.request.GET.get('page')
            context['chart_rcvd'] = Paginator(received, 5).get_page(page_rcvd)

            # Display lokasi sto checked & pending
            chk = location.filter(sto_check='CHK').count()
            pnd = location.filter(sto_check='PND').count()

            context['chart_chk'] = chk
            context['chart_pnd'] = pnd
            context['cent_sto'] = (100 * (chk + pnd)) / location.count()
            context['sdh_cek'] = location.filter(sto_check__isnull=False).count()
            context['of_loc'] = location.count()

            latest_sto = transaksi.filter(trans_type='STO').order_by('-date_created').first()
            context['last_sto'] = latest_sto

            # Display Active / Block Status
            block = produk.filter(status='BLOCK').count()
            active = produk.filter(status='ACTIVE').count()

            context['chart_blok'] = block
            context['chart_actv'] = active
            context['blok_cent'] = 100 * produk.filter(status='BLOCK').count() / produk.count()
            context['actv_cent'] = 100 * produk.filter(status='ACTIVE').count() / produk.count()

            return context

        except ZeroDivisionError:
            return context


class MainMenu(StaffRequiredMixin, TemplateView):
    template_name = 'main_menu.html'


class ViewLabel(StaffRequiredMixin, PageTitleViewMixin, TemplateView):
    template_name = 'label_view.html'
    title = title + 'Report'
    header = title + ' / ' + 'Create label location'


class ResultLabel(StaffRequiredMixin, PageTitleViewMixin, ListView):
    template_name = 'label_result.html'
    title = title + 'Report'
    header = title + ' / ' + 'Create label location'

    def get_queryset(self):  # http://shopnilsazal.github.io/django-pagination-with-basic-search/
        a = self.request.GET.get('from_loc')
        b = self.request.GET.get('to_loc')
        c = self.request.GET.get('assign')

        if c == "":
            object_list = location.filter(no_loc__gte=a, no_loc__lte=b)
        else:
            object_list = location.filter(no_loc__gte=a, no_loc__lte=b, assign=c)
        '''if query:
            posts_list = location.filter(
                Q(no_loc=query) | Q(assign=query) | Q(storage=query) | Q(status=query) | Q(area=query))
        paginator = Paginator(posts_list, 10)  # 10 posts per page
        page = self.request.GET.get('page')

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        return page_obj'''
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tb_temp'] = temporary.filter(no_loc_id__isnull=False)
        return context


# sampai sini ya view label

# location
class ViewLocation(StaffRequiredMixin, PageTitleViewMixin, ListView):
    template_name = 'loc_list.html'
    title = title + 'Location'
    header = title + ' / ' + 'Locations list'
    paginate_by = 10

    # model = User, Competition contoh multiple model

    def get_queryset(self):
        object_list = location.filter(Q(status="FL") | Q(status="UL") | Q(status="HU"))
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total = location.filter(Q(status="FL") | Q(status="UL") | Q(status="HU")).count()
        free = location.filter(status="FL").count()
        used = location.filter(status="UL").count()
        held = location.filter(status="HU").count()
        if total:
            context['total'] = total
            context['free'] = free
            context['free_cent'] = 100 * free / total
            context['used'] = used
            context['used_cent'] = 100 * used / total
            context['held'] = held
            context['held_cent'] = 100 * held / total
        return context


class ResultLocation(StaffRequiredMixin, PageTitleViewMixin, ListView):
    template_name = 'loc_list.html'
    title = title + 'Location'
    header = title + ' / ' + 'Locations list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total = location.filter(Q(status="FL") | Q(status="UL") | Q(status="HU")).count()
        free = location.filter(status="FL").count()
        used = location.filter(status="UL").count()
        held = location.filter(status="HU").count()
        if total:
            context['total'] = total
            context['free'] = free
            context['free_cent'] = 100 * free / total
            context['used'] = used
            context['used_cent'] = 100 * used / total
            context['held'] = held
            context['held_cent'] = 100 * held / total
        return context

    def get_queryset(self):  # http://shopnilsazal.github.io/django-pagination-with-basic-search/
        posts_list = location
        a = self.request.GET.get('no_loc')
        b = self.request.GET.get('assign')  # u/ filter tanpa "no_loc", "assign" wajib diisi
        c = self.request.GET.get('storage')
        d = self.request.GET.get('area')
        e = self.request.GET.get('status')

        if a:
            posts_list = location.filter(Q(no_loc__icontains=a) | Q(status=a))  # u/ filter lokasi delete ketik "DL"

        elif b and c and d and e:
            posts_list = location.filter(assign=b, storage=c, area=d, status=e)

        elif b and c and d or b and c and e:
            posts_list = location.filter(assign=b, storage=c, area=d) or location.filter(assign=b, storage=c, status=e)

        elif b and c or b and d or b and e:
            posts_list = location.filter(assign=b, storage=c) or location.filter(assign=b, area=d) or location.filter(
                assign=b, status=e)
        elif b:
            posts_list = location.filter(Q(status="FL") | Q(status="UL") | Q(status="HU"),
                                         assign=b)  # tampilkan status lokasi, kecuali status lokasi "DL"

        paginator = Paginator(posts_list, 10)  # 10 posts per page
        page = self.request.GET.get('page')

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        return page_obj


class AddLocation(StaffRequiredMixin, PageTitleViewMixin, CreateView):
    template_name = 'loc_add.html'
    title = title + 'Location'
    header = title + ' / ' + 'Create a new location'

    model = ModelLocation
    fields = ['no_loc', 'assign', 'storage', 'area']

    # success_url = reverse_lazy('ViewLocation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get('page')
        context['object_list'] = Paginator(location.order_by('-date_created'), 5).get_page(page)
        return context

    def form_invalid(self, form):
        messages.add_message(self.request, messages.WARNING, "Location already exists.")
        return redirect('AddLocation')

    def form_valid(self, form):
        self.object = form.save()
        messages.add_message(self.request, messages.SUCCESS, "Location added successfully.")
        return redirect('AddLocation')


class EditLocation(StaffRequiredMixin, PageTitleViewMixin, UpdateView):
    template_name = 'loc_edit.html'
    title = title + 'Location'
    header = title + ' / ' + 'Update location'
    model = ModelLocation
    fields = ['assign', 'storage', 'status', 'area']
    context_object_name = 'data'

    # success_url = reverse_lazy('ViewLocation')

    def form_valid(self, form):
        self.object = form.save()
        messages.add_message(self.request, messages.SUCCESS, "Location updated successfully.")
        return redirect('ViewLocation')


class DeleteLocation(StaffRequiredMixin, UpdateView):
    model = ModelLocation
    fields = ['status']

    def form_valid(self, form):
        lok_fre = location.filter(no_loc=self.object.no_loc, status="FL")
        lok_ksg = location.filter(no_loc=self.object.no_loc, status="DL")
        if lok_fre:
            self.object = form.save()
            messages.add_message(self.request, messages.SUCCESS, "Location successfully deleted.")
        elif lok_ksg:
            self.object = form.save()
            messages.add_message(self.request, messages.SUCCESS, "Location successfully restored.")
        else:
            messages.add_message(self.request, messages.WARNING,
                                 "This action is available for free location status ")
        return HttpResponseRedirect(reverse('ViewLocation'))


# sampai sini ya view location

# product
class ViewProduct(StaffRequiredMixin, PageTitleViewMixin, ListView):
    template_name = 'prod_list.html'
    paginate_by = 10
    title = title + 'Product'
    header = title + ' / ' + 'Products list'

    def get_queryset(self):
        # Filter by produk dengan lokasi primary atau produk dengan lokasi null
        object_list = temporary.filter(Q(no_loc_id__assign="P") | Q(no_loc_id__isnull=True)).order_by('prod_code_id')
        # object_list = temporary.filter(prod_code_id__isnull=False)
        # for x in produk:
        # object_list = temporary.filter(prod_code_id=x.prod_code)
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total = produk.count()
        active = produk.filter(status="ACTIVE").count()
        block = produk.filter(status="BLOCK").count()
        if total:
            context['total'] = total
            context['active'] = active
            context['active_cent'] = 100 * active / total
            context['block'] = block
            context['block_cent'] = 100 * block / total
        return context


class ResultProduct(StaffRequiredMixin, PageTitleViewMixin, ListView):
    template_name = 'prod_list.html'
    title = title + 'Product'
    header = title + ' / ' + 'Products list'

    def get_queryset(self):  # http://shopnilsazal.github.io/django-pagination-with-basic-search/
        posts_list = temporary
        a = self.request.GET.get('no_loc')
        b = self.request.GET.get('prod_code')
        c = self.request.GET.get('prod_desc')
        d = self.request.GET.get('status')

        # if a or b or d:
        # post_list = temporary.filter(Q(prod_code_id=b) | Q(prod_code__prod_desc__icontains=b)) or temporary.filter(no_loc=d)

        if a:
            posts_list = temporary.filter(Q(no_loc__no_loc__icontains=a))
        elif b:
            posts_list = temporary.filter(Q(prod_code__prod_code__icontains=b))
        elif c:
            posts_list = temporary.filter(Q(prod_code__prod_desc__icontains=c))
        elif d:
            posts_list = temporary.filter(prod_code__status=d)

        paginator = Paginator(posts_list, 10)  # 10 posts per page
        page = self.request.GET.get('page')

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        return page_obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total = produk.count()
        active = produk.filter(status="ACTIVE").count()
        block = produk.filter(status="BLOCK").count()
        if total:
            context['total'] = total
            context['active'] = active
            context['active_cent'] = 100 * active / total
            context['block'] = block
            context['block_cent'] = 100 * block / total
        return context


class AddProduct(StaffRequiredMixin, PageTitleViewMixin, CreateView):
    template_name = 'prod_add.html'
    title = title + 'Product'
    header = title + ' / ' + ' Create a new product'
    model = ModelProduct
    fields = ['prod_code', 'prod_desc', 'supplier', 'pack_size', 'stock_min', 'stock_max', 'l_time_days']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get('page')
        context['object_list'] = Paginator(produk.order_by('-date_created'), 5).get_page(page)
        return context

    def form_invalid(self, form):
        messages.add_message(self.request, messages.WARNING, "No. Product already exists.")
        return redirect('AddProduct')

    def get_success_url(self, **kwargs):
        # beri value 'new' pada remark bahwa produk harus new line
        temporary.create(prod_code_id=self.object.prod_code, remark="NEW")
        messages.add_message(self.request, messages.SUCCESS, "Product added successfully.")
        return reverse('DetailProduct', kwargs={'pk': self.object.pk})


class EditProduct(StaffRequiredMixin, PageTitleViewMixin, UpdateView):
    template_name = 'prod_edit.html'
    title = title + 'Product'
    header = title + ' / ' + 'Product update'
    model = ModelProduct
    fields = ['prod_desc', 'supplier', 'pack_size', 'stock_min', 'stock_max', 'l_time_days', 'status']
    context_object_name = 'data'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # jika produk tidak memiliki lokasi bisa di block, begitupun sebaliknya
        context['object_list'] = temporary.filter(prod_code_id=self.object.pk, no_loc_id__isnull=True)
        return context

    def form_valid(self, form):
        if self.object.stock_min > self.object.stock_max:
            messages.add_message(self.request, messages.ERROR, "Min value cannot be more than Max value.")
            # return HttpResponseRedirect(reverse('DetailProduct', kwargs={'pk': self.object.pk}))
        else:
            self.object = form.save()
            messages.add_message(self.request, messages.SUCCESS, "Product updated successfully.")
            # return reverse('DetailProduct', kwargs={'pk': self.object.pk})
        return HttpResponseRedirect(reverse('EditProduct', kwargs={'pk': self.object.pk}))

    '''def get_success_url(self, **kwargs):
        if self.object.stock_min > self.object.stock_max:
            messages.add_message(self.request, messages.ERROR, "Min value cannot be more than Max value.")
        else:
            messages.add_message(self.request, messages.SUCCESS, "Product updated successfully.")
        return reverse('DetailProduct', kwargs={'pk': self.object.pk})'''


class DetailProduct(StaffRequiredMixin, PageTitleViewMixin, DetailView):
    template_name = 'prod_detail.html'
    title = title + 'Product'
    header = title + ' / ' + 'Detail product'
    model = ModelProduct
    context_object_name = 'data'


# sampai sini ya view product


# assign location
class ViewNewline(StaffRequiredMixin, PageTitleViewMixin, ListView):
    template_name = 'newline_list.html'
    title = title + 'Assign location'
    header = title
    paginate_by = 10

    def get_queryset(self):
        object_list = temporary.filter(Q(no_loc_id__assign="P") | Q(no_loc_id__isnull=True),
                                       prod_code__status="ACTIVE").order_by('no_loc_id')
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        non_loc = temporary.filter(no_loc_id__isnull=True, prod_code__status="ACTIVE").count()  # produk tanpa lokasi
        wth_loc = temporary.filter(no_loc_id__assign="P", no_loc_id__isnull=False,
                                   prod_code__status="ACTIVE").count()  # produk dengan lokasi primary
        if non_loc or wth_loc:
            context['total'] = int(non_loc) + int(wth_loc)
            context['non_loc'] = non_loc
            context['non_loc_cent'] = 100 * non_loc / (int(non_loc) + int(wth_loc))
            context['wth_loc'] = wth_loc
            context['wth_loc_cent'] = 100 * wth_loc / (int(non_loc) + int(wth_loc))
        return context


class ResultNewline(StaffRequiredMixin, PageTitleViewMixin, ListView):
    template_name = 'newline_list.html'
    title = title + 'Assign location'
    header = title

    def get_queryset(self):
        posts_list = temporary
        a = self.request.GET.get('prod_code')
        b = self.request.GET.get('prod_desc')
        c = self.request.GET.get('no_loc')

        # object_list = temporary.filter(Q(prod_code__prod_code__icontains=query) | Q(no_loc__no_loc__icontains=query), prod_code__status="ACTIVE")
        if a:
            posts_list = temporary.filter(Q(prod_code__prod_code__icontains=a), prod_code__status="ACTIVE")
        elif b:
            posts_list = temporary.filter(Q(prod_code__prod_desc__icontains=b), prod_code__status="ACTIVE")
        elif c:
            posts_list = temporary.filter(Q(no_loc__no_loc__icontains=c), prod_code__status="ACTIVE")

        paginator = Paginator(posts_list, 10)  # 10 posts per page
        page = self.request.GET.get('page')

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        return page_obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        non_loc = temporary.filter(no_loc_id__isnull=True, prod_code__status="ACTIVE").count()  # produk tanpa lokasi
        wth_loc = temporary.filter(no_loc_id__assign="P", no_loc_id__isnull=False,
                                   prod_code__status="ACTIVE").count()  # produk dengan lokasi primary
        if non_loc or wth_loc:
            context['total'] = int(non_loc) + int(wth_loc)
            context['non_loc'] = non_loc
            context['non_loc_cent'] = 100 * non_loc / (int(non_loc) + int(wth_loc))
            context['wth_loc'] = wth_loc
            context['wth_loc_cent'] = 100 * wth_loc / (int(non_loc) + int(wth_loc))
        return context


class EditNewline(StaffRequiredMixin, PageTitleViewMixin, UpdateView):
    template_name = 'newline_add.html'
    title = title + 'New line'
    header = title + ' / ' + 'Add location for product'
    model = ModelTempProdLoc
    fields = ['no_loc']
    context_object_name = 'data'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get('page')
        context['object_list'] = Paginator(location.filter(assign="P", status="FL"), 10).get_page(page)
        context['total'] = location.filter(assign="P", status="FL").count()
        return context

    # jika lokasi belum terecord di database
    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "Location not available.")
        return HttpResponseRedirect(reverse('EditNewline', kwargs={'pk': self.object.pk}))

    def form_valid(self, form):
        # jika ini lokasi reserve yang status null
        # if temporary.filter(no_loc_id=self.object.no_loc_id, prod_code_id__isnull=True).exists():
        # messages.add_message(self.request, messages.WARNING, "Reserve locations cannot be used.")

        # jika ini lokasi reserve
        if location.filter(no_loc=self.object.no_loc_id, assign="R"):
            messages.add_message(self.request, messages.ERROR, "Reserve locations cannot be used.")

        # jika lokasi sudah digunakan produk lain
        elif temporary.filter(no_loc_id=self.object.no_loc_id).exists():
            messages.add_message(self.request, messages.ERROR, "Location is already in use.")

        # jika status lokasi held
        elif location.filter(no_loc=self.object.no_loc_id).filter(status="HU"):
            messages.add_message(self.request, messages.ERROR, "Location is already in held.")

        # jika status lokasi deleted
        elif location.filter(no_loc=self.object.no_loc_id).filter(status="DL"):
            messages.add_message(self.request, messages.ERROR, "Location is already deleted.")

        else:
            self.object = form.save()
            # beri value 'LOC' pada remark bahwa produk sudah memiliki lokasi
            temporary.filter(no_loc_id=self.object.no_loc_id).update(remark="LOC")
            # beri value 'UL' bahwa status lokasi sudah digunakan
            location.filter(no_loc=self.object.no_loc_id).update(status="UL")
            messages.add_message(self.request, messages.SUCCESS, "Location has been successfully added to the product.")
        return HttpResponseRedirect(reverse('EditNewline', kwargs={'pk': self.object.pk}))


class DeleteNewline(StaffRequiredMixin, UpdateView):
    model = ModelTempProdLoc
    fields = ['remark']

    def form_valid(self, form):
        # qty_empty = temporary.filter(id=self.object.pk, no_loc_id__status="UL", qty=0)
        p = temporary.filter(id=self.object.pk)
        if p.filter(no_loc_id__status="UL", qty=0):
            self.object = form.save()
            temporary.filter(id=self.object.pk).update(no_loc_id=None)
            location.filter(no_loc=self.object.no_loc_id).update(status="FL")
            messages.add_message(self.request, messages.SUCCESS, "Location has been deleted.")
        elif p.filter(no_loc_id__status="UL", qty__gt=0):
            messages.add_message(self.request, messages.WARNING, "There is quantity at this location.")
        elif p.filter(no_loc_id__status="HU"):
            messages.add_message(self.request, messages.WARNING, "Status held at this location.")
        # return HttpResponseRedirect(reverse('EditNewline', kwargs={'pk': self.object.pk}))
        return HttpResponseRedirect(reverse('ViewNewline'))


# sampai sini ya view New Line

# transfer / stock move
class ViewTransfer(StaffRequiredMixin, PageTitleViewMixin,
                   TemplateView):  # bug belum nemu cara tampil primary 0 tapi ada reserve
    template_name = 'tf_view.html'
    title = title + 'Stock Transfer'
    header = title

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c = temporary.filter(no_loc__assign='R')
        # d = temporary.filter(no_loc__assign='P', qty=0)
        list = []
        for i in c:
            # page = self.request.GET.get('page')
            prod_code = temporary.filter(prod_code_id=i.prod_code_id, no_loc__assign='P', qty=0)
            # object_list.append(prod_code)
            context['object_list'] = prod_code
            # prod_code = temporary.filter(prod_code_id=a.prod_code_id).order_by('no_loc__assign')
            # context['object_list'] = Paginator(prod_code, 5).get_page(page)
            # context['empt_pri'] = temporary.filter(prod_code_id=a.prod_code_id, no_loc__assign='P', qty=0).count()

        '''combine = min([len(a), len(b), len(c)])
        for i in range(combine):
            # sort by kode produk yang memiliki primary lokasi
            get = temporary.filter(prod_code_id=b[i], no_loc__assign="P")'''
        # context['object_list'] = c
        return context


class ResultTransfer(StaffRequiredMixin, PageTitleViewMixin, ListView):
    template_name = 'tf_view.html'
    title = title + 'Stock Transfer'
    header = title

    '''def get_queryset(self):
        query = self.request.GET.get('prod_code')
        object_list = temporary.filter(prod_code_id=query, remark="LOC")
        if object_list:
            return object_list
        else:
            messages.add_message(self.request, messages.WARNING, "Product not found.")
            return False'''

    def get_queryset(self):  # http://shopnilsazal.github.io/django-pagination-with-basic-search/
        posts_list = temporary
        a = self.request.GET.get('prod_code')
        b = self.request.GET.get('prod_desc')
        c = self.request.GET.get('no_loc')

        if a:
            posts_list = temporary.filter(Q(prod_code__prod_code__icontains=a), remark="LOC").order_by('no_loc__assign',
                                                                                                       'no_loc')
        elif b:
            posts_list = temporary.filter(Q(prod_code__prod_desc__icontains=b), remark="LOC").order_by('no_loc__assign',
                                                                                                       'no_loc')
        elif c:
            posts_list = temporary.filter(Q(no_loc__no_loc__icontains=c), remark="LOC").order_by('no_loc__assign',
                                                                                                 'no_loc')

        paginator = Paginator(posts_list, 10)  # 10 posts per page
        page = self.request.GET.get('page')

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        return page_obj


class UpdateTransfer(StaffRequiredMixin, PageTitleViewMixin, UpdateView):
    template_name = 'tf_update.html'
    title = title + 'Stock Move'
    header = title + ' / ' + 'Transfer stock'
    model = ModelTempProdLoc
    fields = ['remark', 'qty', 'no_loc', 'prod_code']
    context_object_name = 'data'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c = temporary.filter(id=self.object.pk)
        for a in c:
            page = self.request.GET.get('page')
            prod_code = temporary.filter(prod_code_id=a.prod_code_id).order_by('no_loc__assign')
            context['object_list'] = Paginator(prod_code, 5).get_page(page)
            # prod_code = temporary.filter(prod_code_id=a.prod_code_id).ordered_by('-no_loc__assign')
            # context['object_list'] = prod_code
        return context

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            id = request.POST.get('id')
            a = request.POST.get('prod_code')
            b = request.POST.get('no_loc1')
            c = request.POST.get('no_loc2')
            d = request.POST.get('qty')
            get = temporary.filter(id=id)
            # lok1 = location.filter(no_loc=b, assign="P")
            # lok2 = location.filter(no_loc=c, assign="P")
            # lok = temporary.filter(id=id, no_loc__assign=c)
            prim1 = location.filter(no_loc=b, assign="P")
            prim2 = location.filter(no_loc=c, assign="P")
            resv1 = location.filter(no_loc=b, assign="R")
            resv2 = location.filter(no_loc=c, assign="R")

            # reserve dengan lokasi dan produk yang sudah ada di db
            match = temporary.filter(no_loc_id=c, prod_code_id=a)

            # object kosong pada tb temporary
            empt = temporary.filter(remark="EMP", prod_code_id__isnull=True, no_loc_id__isnull=True).count()

            # kondisi lokasi 1 dan lokasi 2 sama-sama primary
            if prim1.filter(status="UL") and prim2.filter(status="FL"):
                for e in get:
                    if int(d) == 0:  # (opsional) di front end inputnya sudah diberi min=1
                        # error qty input = 0
                        messages.add_message(self.request, messages.ERROR, "Enter a minimum quantity of 1.")
                    elif int(d) < int(e.qty) or int(d) > int(e.qty):
                        # qty harus sama tf antar primary
                        messages.add_message(self.request, messages.ERROR,
                                             "Quantity must be the same for transfer between primary location.")
                    elif int(d) == int(e.qty):
                        get.update(no_loc_id=c,
                                   modified=str(timezone.now()))  # update lokasi lama menjadi lokasi baru lokasi 1
                        location.filter(no_loc=b).update(status="FL")  # update status lokasi 1 menjadi free
                        location.filter(no_loc=c).update(status="UL")  # update status lokasi 2 menjadi used
                        messages.add_message(self.request, messages.SUCCESS, "Transfer Successful.")

            # kondisi lokasi 1 primary dan lokasi 2 reserve
            elif prim1.filter(status="UL") and resv2:
                for e in get:
                    x = int(e.qty) - int(d)
                    if int(d) == 0:  # (opsional) di front end inputnya sudah diberi min=1
                        # error qty input = 0
                        messages.add_message(self.request, messages.ERROR, "Enter a minimum quantity of 1.")
                    elif int(d) > int(e.qty):
                        # error pengurangan jika qty tf lebih besar dari qty awal
                        messages.add_message(self.request, messages.ERROR, "Avoid negative values.")
                    elif resv2.filter(status="FL"):
                        get.update(qty=int(x),
                                   modified=str(timezone.now()))  # update qty lama menjadi qty baru lokasi 1
                        location.filter(no_loc=c).update(status="UL")  # update status lokasi 2 menjadi used
                        temporary.create(
                            remark="LOC",
                            qty=int(d),
                            no_loc_id=c,
                            prod_code_id=a
                        )
                        '''for p in empt:
                            empt.update(
                                remark="LOC",
                                qty=int(d),
                                no_loc_id=c,
                                prod_code_id=a
                            )'''
                        messages.add_message(self.request, messages.SUCCESS, "Transfer Successful.")
                    elif resv2.filter(status="UL") and match:
                        for f in match:
                            get.update(qty=int(x),
                                       modified=str(timezone.now()))  # update qty lama menjadi qty baru lokasi 1
                            match.update(qty=int(f.qty) + int(d))  # update qty lama menjadi qty baru lokasi 2
                        messages.add_message(self.request, messages.SUCCESS, "Transfer Successful.")
                    else:
                        messages.add_message(self.request, messages.ERROR, "Location is already used in other product.")

            # kondisi lokasi 1 reserve dan lokasi 2 primary
            elif resv1.filter(status="UL") and prim2.filter(status="UL"):
                for e in get:
                    x = int(e.qty) - int(d)
                    if int(d) == 0:  # (opsional) di front end inputnya sudah diberi min=1
                        # error qty input = 0
                        messages.add_message(self.request, messages.ERROR, "Enter a minimum quantity of 1.")
                    elif int(d) > int(e.qty):
                        # error pengurangan jika qty tf lebih besar dari qty awal
                        messages.add_message(self.request, messages.ERROR, "Avoid negative values.")
                    elif prim2 and match:
                        for f in match:
                            if x == 0:  # jika pengurangan menghasilkan nol
                                # get.update(remark="EMP", qty=int(x), prod_code_id=None, no_loc_id=None)
                                get.delete()  # langsung delete (alternative kodingan) lokasi 1 (lama)
                                match.update(qty=int(f.qty) + int(d))  # update qty lama menjadi qty baru lokasi 2
                                location.filter(no_loc=b).update(status="FL")  # update status lokasi 1 menjadi free
                                messages.add_message(self.request, messages.SUCCESS, "Transfer Successful.")
                                return HttpResponseRedirect(reverse('UpdateTransfer', kwargs={'pk': f.id}))
                            else:
                                get.update(qty=int(x))
                                match.update(qty=int(f.qty) + int(d),
                                             modified=str(timezone.now()))  # update qty lama menjadi qty baru lokasi 2
                            # get.update(qty=int(x))  # update qty lama menjadi qty baru lokasi 1
                            # match.update(qty=int(f.qty) + int(d))  # update qty lama menjadi qty baru lokasi 2
                        messages.add_message(self.request, messages.SUCCESS, "Transfer Successful.")
                    else:
                        messages.add_message(self.request, messages.ERROR, "Location is already used in other product.")

            # kondisi lokasi 1 dan 2 reserve
            elif resv1.filter(status="UL") and resv2:
                for e in get:
                    x = int(e.qty) - int(d)
                    if int(d) == 0:  # (opsional) di front end inputnya sudah diberi min=1
                        # error qty input = 0,
                        messages.add_message(self.request, messages.ERROR, "Enter a minimum quantity of 1.")
                    elif int(d) > int(e.qty):
                        # error pengurangan jika qty tf lebih besar dari qty awal
                        messages.add_message(self.request, messages.ERROR, "Avoid negative values.")
                    elif resv2 and match:
                        for f in match:
                            if x == 0:  # jika pengurangan menghasilkan nol
                                # get.update(remark="EMP", qty=int(x), prod_code_id=None, no_loc_id=None)
                                get.delete()  # langsung delete (alternative kodingan) lokasi 1 (lama)
                                match.update(qty=int(f.qty) + int(d))  # update qty lama menjadi qty baru di lokasi 2
                                location.filter(no_loc=b).update(status="FL")  # update status lokasi 1 menjadi free
                                messages.add_message(self.request, messages.SUCCESS, "Transfer Successful.")
                                return HttpResponseRedirect(reverse('UpdateTransfer', kwargs={'pk': f.id}))
                            else:
                                get.update(qty=int(x), modified=str(timezone.now()))
                                match.update(qty=int(f.qty) + int(d))  # update qty lama menjadi qty baru di lokasi 2
                    elif resv2.filter(status="FL"):
                        location.filter(no_loc=c).update(status="UL")  # update status lokasi 2 menjadi used
                        n = temporary.create(
                            remark="LOC",
                            qty=int(d),
                            no_loc_id=c,
                            prod_code_id=a
                        )
                        if x == 0:  # jika pengurangan menghasilkan nol
                            get.delete()  # langsung delete (alternative kodingan) lokasi 1 (lama)
                            # match.update(qty=int(f.qty) + int(d))  # update qty lama menjadi qty baru di lokasi 2
                            location.filter(no_loc=b).update(status="FL")  # update status lokasi 1 menjadi free
                            messages.add_message(self.request, messages.SUCCESS, "Transfer Successful.")
                            return HttpResponseRedirect(reverse('UpdateTransfer', kwargs={'pk': n.id}))
                        else:
                            get.update(qty=int(x),
                                       modified=str(timezone.now()))  # update qty lama menjadi qty baru lokasi 1
                            messages.add_message(self.request, messages.SUCCESS, "Transfer Successful.")

            elif prim2.filter(status="UL"):  # error jika lokasi 2 primary sudah digunakan di produk lain
                messages.add_message(self.request, messages.ERROR, "Location is already used in other product.")
            elif resv2.filter(status="HU"):  # error jika lokasi 2 reserve lokasi yang di pakai held
                messages.add_message(self.request, messages.ERROR, "Location is already in held.")
            elif resv2.filter(status="DL"):  # error jika lokasi 2 reserve lokasi yang di sudah di delete
                messages.add_message(self.request, messages.ERROR, "Location is already deleted.")

            return HttpResponseRedirect(reverse('UpdateTransfer', kwargs={'pk': id}))


# proses-proses adjustment

# TTB adjustment
class ViewReceiving(StaffRequiredMixin, PageTitleViewMixin, TemplateView):
    template_name = 'receive_list.html'
    title = title + 'Inbound'
    header = title
    # paginate_by = 10

    '''def get_queryset(self):
        # object_list = transaksi.filter(no_ttb__isnull=False).order_by('-date_created')
        object_list = transaksi.filter(Q(ttb_stat="OR") | Q(ttb_stat="RE")).order_by('-date_created')
        # object_list = ModelTransaction.objects.filter(no_ttb__isnull=False).aggregate(prod_code=Sum("qty_adj"))["prod_code"]
        # object_list = ModelTransaction.objects.annotate(sum("qty_adj"))
        return object_list'''


class ResultReceiving(StaffRequiredMixin, PageTitleViewMixin, ListView):
    template_name = 'receive_list.html'
    title = title + 'Inbound'
    header = title

    def get_queryset(self):
        posts_list = transaksi
        a = self.request.GET.get('no_ttb')
        b = self.request.GET.get('prod_code')
        # object_list = transaksi.filter(Q(ttb_stat="OR") | Q(ttb_stat="RE"), no_ttb=query).order_by('-date_created')
        if a and b:
            posts_list = transaksi.filter(Q(ttb_stat="OR") | Q(ttb_stat="RE"), no_ttb=a,
                                          prod_code__prod_code__icontains=b).order_by('-date_created')
        elif a:
            posts_list = transaksi.filter(Q(ttb_stat="OR") | Q(ttb_stat="RE"), no_ttb=a).order_by('-date_created')
        elif b:
            posts_list = transaksi.filter(Q(ttb_stat="OR") | Q(ttb_stat="RE"),
                                          prod_code__prod_code__icontains=b).order_by('-date_created')

        paginator = Paginator(posts_list, 10)  # 10 posts per page
        page = self.request.GET.get('page')

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        return page_obj


class FormTransaction(ModelForm):
    class Meta:
        model = ModelTransaction
        fields = ['no_ttb', 'ttb_stat', 'ttb_qty', 'no_loc', 'trans_type', 'adj_type', 'prod_code', 'qty_bfr',
                  'qty_adj', 'qty_afr']


class AddReceiving(StaffRequiredMixin, PageTitleViewMixin,
                   CreateView):  # bug invalid literal for int() with base 10: '' kalau langsung submit
    # fungsi self.form_valid(...)  adalah save
    template_name = 'receive_add.html'
    title = title + 'Inbound'
    header = title + ' / ' + 'Receive product'
    model = ModelTransaction
    form_class = FormTransaction

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            # https://stackoverflow.com/questions/50313153/how-to-save-multiple-html-inputs-with-the-same-name-in-django
            a = request.POST.getlist('no_ttb')
            b = request.POST.getlist('prod_code')
            c = request.POST.getlist('qty')
            combine = min([len(a), len(b), len(c)])
            for i in range(combine):

                # sort by kode produk yang memiliki primary lokasi
                get = temporary.filter(prod_code_id=b[i], no_loc__assign="P")

                if int(c[i]) == 0:  # (opsional) di front end inputnya sudah diberi min=1
                    # error qty input = 0
                    messages.add_message(self.request, messages.ERROR, "Enter a minimum quantity of 1.")
                # jika no ttb dan kode produk tersedia / sudah ada
                elif transaksi.filter(no_ttb=a[i], prod_code=b[i]).exists():
                    messages.add_message(self.request, messages.ERROR,
                                         "No. TTB with product has been registered.")
                elif temporary.filter(prod_code_id=b[i], no_loc_id__isnull=True):
                    messages.add_message(self.request, messages.ERROR,
                                         "Product " + b[i] + " doesn't have a primary location.")

                elif get.filter(remark="LOC"):
                    for e in get:
                        uom = int(c[i]) * e.prod_code.pack_size
                        formset = self.form_class({
                            'no_ttb': a[i],
                            'ttb_stat': 'OR',  # remark sebagai ttb original belum di edit
                            'ttb_qty': c[i],
                            'no_loc': e.no_loc_id,
                            'trans_type': 'TTB',
                            'adj_type': 'AI',
                            'prod_code': b[i],
                            'qty_bfr': e.qty,
                            'qty_adj': uom,
                            # 'qty_afr': int(e.qty) + int(int(c[i] * int(e.prod_code__pack_size)))
                            'qty_afr': int(e.qty) + uom
                        })
                        # check whether it's valid:
                        if formset.is_valid():
                            # update qty tb_temp
                            get.update(qty=int(e.qty) + uom, modified=str(timezone.now()))
                            formset.save()
                            # notif nya jadi banayak mengikuti jumlah input
                            messages.add_message(self.request, messages.SUCCESS,
                                                 "No. TTB " + a[i] + " with product " + b[i] + " added successfully.")
                else:
                    messages.add_message(self.request, messages.ERROR, "Product doesn't exist.")
            # return HttpResponseRedirect(reverse('AddReceiving'))
            return redirect('AddReceiving')


class UpdateReceiving(StaffRequiredMixin, PageTitleViewMixin, UpdateView):
    template_name = 'receive_update.html'
    title = title + 'Inbound'
    header = title + ' / ' + 'Receipt update'
    model = ModelTransaction
    form_class = FormTransaction

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = transaksi.filter(id=self.object.pk)
        return context

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            id = self.request.POST.get('id')
            a = self.request.POST.get('no_ttb')
            b = self.request.POST.get('ttb_qty')  # qty ttb
            c = self.request.POST.get('prod_code')
            d = self.request.POST.get('qty')
            opsi = self.request.POST.get('adjust')
            # ambil qty dari status lokasi primary
            get = temporary.filter(prod_code_id=c, no_loc__assign="P")

            for e in get:
                uom = int(d) * e.prod_code.pack_size
                if opsi == 'AO':  # adjust. out
                    # jika qty ttb. lebih kecil dari qty adjustment
                    if int(b) < int(d):
                        # error pengurangan jika nilai adj. lebih besar dari qty ttb
                        messages.add_message(self.request, messages.ERROR, "Avoid negative values.")
                        # raise ValueError('Represents a hidden bug, do not catch this')
                        return HttpResponseRedirect(reverse('UpdateReceiving', kwargs={'pk': id}))
                    else:
                        formset = self.form_class({
                            'no_ttb': a,
                            'ttb_stat': 'RE',  # remark sebagai ttb revisi sudah di edit
                            'ttb_qty': int(b) - int(d),
                            'no_loc': e.no_loc_id,
                            'trans_type': 'TTB',
                            'adj_type': 'AO',
                            'prod_code': c,
                            'qty_bfr': e.qty,
                            'qty_adj': str("-") + str(uom),
                            'qty_afr': int(e.qty) - uom
                        })
                        # check whether it's valid:
                        if formset.is_valid():
                            # update qty tb_temp
                            get.update(qty=int(e.qty) - uom, modified=str(timezone.now()))
                            # update ttb_stat NO menyatakan id ini sudah di edit
                            transaksi.filter(id=id).update(ttb_stat="NO")
                            formset.save()

                elif opsi == 'AI':  # adjust. in
                    formset = self.form_class(
                        {
                            'no_ttb': a,
                            'ttb_stat': 'RE',  # remark sebagai ttb revisi sudah di edit
                            'ttb_qty': int(b) + int(d),
                            'no_loc': e.no_loc_id,
                            'trans_type': 'TTB',
                            'adj_type': 'AI',
                            'prod_code': c,
                            'qty_bfr': e.qty,
                            'qty_adj': uom,
                            'qty_afr': int(e.qty) + uom,
                        })
                    # check whether it's valid:
                    if formset.is_valid():
                        # update qty tb_temp
                        get.update(qty=int(e.qty) + uom, modified=str(timezone.now()))
                        # update ttb_stat NO menyatakan id ini sudah di edit
                        transaksi.filter(id=id).update(ttb_stat="NO")
                        formset.save()
                messages.add_message(self.request, messages.SUCCESS, "Stock has been successfully changed.")
                # return HttpResponseRedirect(reverse('ViewReceiving'))
                return redirect(reverse('ResultReceiving') + '?no_ttb=' + a)


# sampai sini ya view receiving


# pick adjustment
# class ViewPicking(PageTitleViewMixin, ListView):
class ViewPicking(PageTitleViewMixin, TemplateView):
    template_name = 'pick_list.html'
    title = title + 'Picking'
    header = title
    paginate_by = 10

    # filter by produk yang memiliki lokasi
    '''def get_queryset(self):
        object_list = temporary.filter(remark="LOC", no_loc__status="UL", no_loc__assign="P").order_by('modified')
        return object_list'''


class ResultPicking(PageTitleViewMixin, ListView):
    template_name = 'pick_list.html'
    title = title + 'Picking'
    header = title

    def get_queryset(self):  # http://shopnilsazal.github.io/django-pagination-with-basic-search/
        posts_list = temporary
        a = self.request.GET.get('prod_code')
        b = self.request.GET.get('prod_desc')
        c = self.request.GET.get('no_loc')
        if a:
            '''posts_list = temporary.filter(
                Q(prod_code_id=query) | Q(prod_code__prod_desc__icontains=query) | Q(no_loc_id=query) | Q(
                    no_loc_id__storage=query) | Q(no_loc_id__area=query), remark="LOC", no_loc__status="UL")'''
            posts_list = temporary.filter(Q(prod_code__prod_code__icontains=a), remark="LOC", no_loc__assign="P",
                                          no_loc__status="UL")
        elif b:
            posts_list = temporary.filter(Q(prod_code__prod_desc__icontains=b), remark="LOC", no_loc__assign="P",
                                          no_loc__status="UL")
        elif c:
            posts_list = temporary.filter(Q(no_loc__no_loc__icontains=c), remark="LOC", no_loc__assign="P",
                                          no_loc__status="UL")

        paginator = Paginator(posts_list, 10)  # 10 posts per page
        page = self.request.GET.get('page')

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        return page_obj

    '''def get_queryset(self):
        query = self.request.GET.get('q')
        # filter by produk yang memiliki lokasi
        object_list = temporary.filter(
            Q(prod_code_id=query) | Q(prod_code__prod_desc__icontains=query) | Q(no_loc_id=query) | Q(
                no_loc_id__storage=query) | Q(no_loc_id__area=query), remark="LOC")
        if object_list:
            return object_list
        else:
            messages.add_message(self.request, messages.WARNING, "Product not found.")
            return False'''


class UpdatePicking(PageTitleViewMixin, UpdateView):
    template_name = 'pick_update.html'
    title = title + 'Picking'
    header = title + ' / ' + 'Picking location'
    model = ModelTempProdLoc
    # fields = ['qty']
    form_class = FormTransaction
    context_object_name = 'data'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get('page')
        # filter by produk yang memiliki dengan transaksi tipe PCK
        context['object_list'] = Paginator(
            transaksi.filter(no_loc=self.object.no_loc_id, trans_type="PCK").order_by('-date_created'), 5).get_page(
            page)
        return context

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            id = self.request.POST.get('id')
            adj_qty = self.request.POST.get('qty')
            opsi = self.request.POST.get('adjust')
            komen = self.request.POST.get('comment')
            auth = self.request.POST.get('auth')
            get = temporary.filter(id=id)
            # getusr = users.filter(card_number=auth)

            if user_uid.filter(uid=auth):
                for e in get:
                    if opsi == 'AO':  # adjust. out
                        if int(adj_qty) == 0:  # (opsional) di front end inputnya sudah diberi min=1
                            # error pengurangan jika qty tf lebih besar dari qty awal
                            messages.add_message(self.request, messages.ERROR, "Enter a minimum quantity of 1.")
                        elif int(adj_qty) > int(e.qty):
                            # error pengurangan jika nilai adj. lebih besar dari qty awal
                            messages.add_message(self.request, messages.ERROR, "Avoid negative values.")
                        else:
                            final = int(e.qty) - int(adj_qty)
                            # update qty tb_temp
                            get.update(qty=final, modified=str(timezone.now()))
                            # buat record di tb_transaction
                            transaksi.create(
                                no_loc=e.no_loc_id,
                                trans_type="PCK",
                                adj_type="AO",
                                prod_code=e.prod_code,
                                qty_bfr=int(e.qty),
                                qty_adj=str("-") + str(int(adj_qty)),
                                qty_afr=final,
                                comment=str(komen),
                                usernm=users.get(no_card=auth)
                            )
                            messages.add_message(self.request, messages.SUCCESS,
                                                 "Adjustment-out has been successfully.")
                    elif opsi == 'AI':  # adjust. in
                        if int(adj_qty) == 0:  # (opsional) di front end inputnya sudah diberi min=1
                            # error pengurangan jika qty tf lebih besar dari qty awal
                            messages.add_message(self.request, messages.ERROR, "Enter a minimum quantity of 1.")
                        else:
                            final = int(e.qty) + int(adj_qty)
                            # update qty tb_temp
                            get.update(qty=final, modified=str(timezone.now()))
                            # buat record di tb_transaction
                            transaksi.create(
                                no_loc=e.no_loc_id,
                                trans_type="PCK",
                                adj_type="AI",
                                prod_code=e.prod_code,
                                qty_bfr=int(e.qty),
                                qty_adj=int(adj_qty),
                                qty_afr=final,
                                comment=str(komen),
                                usernm=users.get(no_card=auth)
                            )
                            messages.add_message(self.request, messages.SUCCESS, "Adjustment-in has been successfully.")
                    return HttpResponseRedirect(reverse('UpdatePicking', kwargs={'pk': id}))
            else:
                messages.add_message(self.request, messages.ERROR, "Access denied.")
                # return HttpResponseRedirect(reverse('UpdatePicking', kwargs={'pk': id}))


# sampai sini ya view picking

# stockopname adjustment
class ViewStockOpname(StaffRequiredMixin, PageTitleViewMixin, ListView):
    template_name = 'sto_list.html'
    title = title + 'STO'
    header = title + ' / ' + 'STO location'
    model = ModelTempProdLoc
    context_object_name = 'data'

    ''''# filter by lokasi yang memiliki status free lokasi dan used lokasi
    def get_queryset(self):
        #object_list = location.filter(Q(status="FL") | Q(status="UL"))
        object_list = temporary.filter(Q(no_loc__status="FL") | Q(no_loc__status="UL"))
        return object_list'''

    # filter by lokasi yang memiliki status free lokasi dan used lokasi
    def get_queryset(self):  # http://shopnilsazal.github.io/django-pagination-with-basic-search/
        # posts_list = location.filter(Q(status="FL") | Q(status="UL")).order_by('no_loc')
        posts_list = location.order_by('no_loc')
        paginator = Paginator(posts_list, 10)  # 10 posts per page
        page = self.request.GET.get('page')

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        return page_obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total = location.filter(Q(status="FL") | Q(status="UL"))
        uncheck = total.filter(sto_check__isnull=True).count()
        checked = total.filter(sto_check="CHK").count()
        pending = total.filter(sto_check="PND").count()
        # held = location.filter(Q(status="HF") | Q(status="HU")).count()
        if total:
            context['total'] = total.count()
            context['uc'] = uncheck
            context['uc_cent'] = 100 * uncheck / total.count()
            context['ch'] = checked
            context['ch_cent'] = 100 * checked / total.count()
            context['pe'] = pending
            context['pe_cent'] = 100 * pending / total.count()
            # context['held'] = held
            # context['held_cent'] = 100 * held / total
        return context


class ResultStockOpname(StaffRequiredMixin, PageTitleViewMixin, ListView):
    template_name = 'sto_update.html'
    title = title + 'STO'
    header = title + ' / ' + 'STO adjustment'

    def get_queryset(self):
        query = self.request.GET.get('q')
        object_list = temporary.filter(no_loc_id=query)
        return object_list


class UpdateStockOpname(StaffRequiredMixin, UpdateView):
    model = ModelTempProdLoc
    fields = ['qty']

    # success_url = reverse_lazy('ViewStockOpname')

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            id = self.request.POST.get('id')
            a = self.request.POST.get('qty')
            # b = self.request.POST.get('prod_code')
            c = self.request.POST.get('no_loc')
            get = temporary.filter(id=id)
            resv = location.filter(no_loc=c, assign="R")
            for e in get:
                if resv and int(a) == 0:  # jika lokasinya reserve dan qty adj 0
                    adj = int(e.qty) - int(a)
                    after = int(e.qty) - int(adj)
                    location.filter(no_loc=c).update(sto_check="CHK", status="FL")  # update status & sto_check lokasi
                    transaksi.create(
                        no_loc=e.no_loc_id,
                        trans_type="STO",
                        adj_type="AO",
                        prod_code=e.prod_code,
                        qty_bfr=int(e.qty),
                        qty_adj=str("-") + str(adj),
                        qty_afr=after
                    )
                    get.delete()  # langsung delete (alternative kodingan)
                    messages.add_message(self.request, messages.SUCCESS, "Adjustment-out has been successfully.")

                elif int(e.qty) > int(a):  # jika nilai adj lebih kecil dari qty before
                    adj = int(e.qty) - int(a)
                    after = int(e.qty) - int(adj)
                    get.update(qty=after, modified=str(timezone.now()))
                    # update status sto_check chk untuk lokasi sudah di sto
                    location.filter(no_loc=e.no_loc_id, ).update(sto_check="CHK")
                    transaksi.create(
                        no_loc=e.no_loc_id,
                        trans_type="STO",
                        adj_type="AO",
                        prod_code=e.prod_code,
                        qty_bfr=int(e.qty),
                        qty_adj=str("-") + str(adj),
                        qty_afr=after
                    )
                    messages.add_message(self.request, messages.SUCCESS, "Adjustment-out has been successfully.")

                elif int(e.qty) < int(a):  # jika nilai adj lebih besar dari qty before
                    adj = int(a) - int(e.qty)
                    after = int(e.qty) + int(adj)
                    get.update(qty=after, modified=str(timezone.now()))
                    # update status sto_check chk untuk lokasi sudah di sto
                    location.filter(no_loc=e.no_loc_id).update(sto_check="CHK")
                    transaksi.create(
                        no_loc=e.no_loc_id,
                        trans_type="STO",
                        adj_type="AI",
                        prod_code=e.prod_code,
                        qty_bfr=int(e.qty),
                        qty_adj=adj,
                        qty_afr=after
                    )
                    messages.add_message(self.request, messages.SUCCESS, "Adjustment-in has been successfully.")

                elif int(e.qty) == int(a):  # jika nilai adj sama dengan qty before
                    adj = int(a) - int(e.qty)
                    after = int(e.qty) + int(adj)
                    get.update(qty=after, modified=str(timezone.now()))
                    # update status sto_check chk untuk lokasi sudah di sto
                    location.filter(no_loc=e.no_loc_id).update(sto_check="CHK")
                    transaksi.create(
                        no_loc=e.no_loc_id,
                        trans_type="STO",
                        adj_type="AI",
                        prod_code=e.prod_code,
                        qty_bfr=int(e.qty),
                        qty_adj=adj,
                        qty_afr=after
                    )
                    messages.add_message(self.request, messages.SUCCESS, "Adjustment has been successfully.")

                return HttpResponseRedirect(reverse('ViewStockOpname'))


# "chk" u/ sudah dicek (checked), "pnd" u/ sudah dicek tapi pending
class ConfirmStockOpname(StaffRequiredMixin, UpdateView):
    model = ModelLocation
    fields = ['sto_check']
    success_url = reverse_lazy('ViewStockOpname')


class AddRsvStockOpname(StaffRequiredMixin, PageTitleViewMixin, UpdateView):  # menambah stok di reserve
    template_name = 'sto_rsv_add.html'
    title = title + 'STO'
    header = title + ' / ' + 'STO reserve location'
    model = ModelLocation
    fields = ['status', 'sto_check']
    context_object_name = 'data'

    # success_url = reverse_lazy('ViewStockOpname')

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            # id = self.request.POST.get('id')
            a = self.request.POST.get('prod_code')
            b = self.request.POST.get('no_loc')

            temporary.create(
                prod_code_id=a,
                no_loc_id=b,
                qty=0,
                remark="LOC"
            )
            location.filter(no_loc=b).update(sto_check="PND", status="UL")  # status pending, qty required

        return redirect(reverse('ResultStockOpname') + '?q=' + b)


class RemoveCheckStockOpname(StaffRequiredMixin, UpdateView):  # menghapus marking yang sudah di cek tabel sto
    def post(self, request, *args, **kwargs):
        if "clear" in request.POST:
            location.update(sto_check=None)
            messages.add_message(self.request, messages.SUCCESS, "Checked mark is cleared.")
        return HttpResponseRedirect(reverse('ViewStockOpname'))


# sampai sini ya view stock opname


# record - record
class ViewAdjustmentRecord(StaffRequiredMixin, PageTitleViewMixin, ListView):
    template_name = 'record_adj.html'
    title = title + 'Report'
    header = title + ' / ' + 'Report movement'
    paginate_by = 10

    def get_queryset(self):
        object_list = transaksi.order_by('-date_created')
        return object_list


class ResultAdjustmentRecord(StaffRequiredMixin, PageTitleViewMixin, ListView):
    template_name = 'record_adj.html'
    title = title + 'Report'
    header = title + ' / ' + 'Report movement'

    '''def get_queryset(self):
        query = self.request.GET.get('q')
        object_list = transaksi.filter(Q(no_loc=query) | Q(prod_code=query))
        if object_list:
            return object_list
        else:
            messages.add_message(self.request, messages.WARNING, "Adjustment record not found.")
            return False'''

    def get_queryset(self):
        a = self.request.GET.get('q')
        b = self.request.GET.get('trans_type')
        c = self.request.GET.get('date_bfr')
        d = self.request.GET.get('date_afr')
        # query = a, b, c, d

        # gte ≥ 'greater than or equal', lte ≤ 'lower than or equal'
        gte = datetime.strptime(str(c).replace("T", " "), '%Y-%m-%d %H:%M')
        lte = datetime.strptime(str(d).replace("T", " "), '%Y-%m-%d %H:%M')

        if a == "" and b == "":
            object_list = transaksi.filter(date_created__gte=gte, date_created__lte=lte)
        elif a == "":
            object_list = transaksi.filter(trans_type=b, date_created__gte=gte, date_created__lte=lte)
        elif b == "":
            object_list = transaksi.filter(Q(no_loc=a) | Q(prod_code=a) | Q(no_ttb=a), date_created__gte=gte,
                                           date_created__lte=lte)
        else:
            object_list = transaksi.filter(Q(no_loc=a) | Q(prod_code=a) | Q(no_ttb=a), trans_type=b,
                                           date_created__gte=gte, date_created__lte=lte)

        paginator = Paginator(object_list, 10)  # 10 posts per page
        page = self.request.GET.get('page')

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        return page_obj
        # return object_list


class ViewLocationProduct(StaffRequiredMixin, PageTitleViewMixin, ListView):
    # class ViewLocationProduct(TemplateView):
    template_name = 'record_loc.html'
    title = title + 'Report'
    header = title + ' / ' + 'Product by location'
    paginate_by = 10

    def get_queryset(self):
        object_list = location.filter(Q(status="HU") | Q(status="FL") | Q(status="UL"))
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tb_temp'] = temporary.filter(no_loc_id__isnull=False)
        return context


class ResultLocationProduct(StaffRequiredMixin, PageTitleViewMixin, ListView):
    template_name = 'record_loc.html'
    title = title + 'Report'
    header = title + ' / ' + 'Product by location'

    def get_queryset(self):
        a = self.request.GET.get('no_loc1')
        b = self.request.GET.get('no_loc2')
        c = self.request.GET.get('assign')
        d = self.request.GET.get('status')
        # e = self.request.GET.get('prod_code')
        # query = a, b, c, d, e

        '''if a == "" and b == "" and c == "" and d == "":
            object_list = location
        elif a == "" and b == "" and c == "":
            object_list = location.filter(status=d)
        elif a == "" and b == "":
            object_list = location.filter(assign=c, status=d)
        elif a == "":
            object_list = location.filter(no_loc__lte=b, assign=c, status=d)
        elif c == "" and d == "":
            object_list = location.filter(no_loc__gte=a, no_loc__lte=b)
        else:
            object_list = location.filter(no_loc__gte=a, no_loc__lte=b, assign=c, status=d)'''

        if c == "" and d == "":
            object_list = location.filter(no_loc__gte=a, no_loc__lte=b)
        elif d == "":
            object_list = location.filter(no_loc__gte=a, no_loc__lte=b, assign=c)
        elif c == "":
            object_list = location.filter(no_loc__gte=a, no_loc__lte=b, status=d)
        else:
            object_list = location.filter(no_loc__gte=a, no_loc__lte=b, assign=c, status=d)

        paginator = Paginator(object_list, 10)  # 10 posts per page
        page = self.request.GET.get('page')

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        return page_obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tb_temp'] = temporary.filter(no_loc_id__isnull=False)
        return context


class ViewStockProduct(StaffRequiredMixin, PageTitleViewMixin, ListView):
    template_name = 'record_stock.html'
    title = title + 'Report'
    header = title + ' / ' + 'Stock product'
    paginate_by = 10

    def get_queryset(self):
        object_list = temporary.values('prod_code', 'prod_code__prod_desc', 'prod_code__stock_min',
                                       'prod_code__stock_max', 'prod_code__pack_size').annotate(
            mysum=Sum('qty')).filter(prod_code__status="ACTIVE").order_by('prod_code')
        return object_list


class ResultStockProduct(StaffRequiredMixin, PageTitleViewMixin, ListView):
    template_name = 'record_stock.html'
    title = title + 'Report'
    header = title + ' / ' + 'Stock product'

    def get_queryset(self):
        a = self.request.GET.get('q')
        b = self.request.GET.get('level')

        if a == "" and b == "":
            object_list = temporary.values('prod_code', 'prod_code__prod_desc', 'prod_code__stock_min',
                                           'prod_code__stock_max', 'prod_code__pack_size').annotate(
                mysum=Sum('qty')).filter(prod_code__status="ACTIVE").order_by('prod_code')
        elif a == "" and b == "B":  # Safety
            object_list = temporary.values('prod_code', 'prod_code__prod_desc', 'prod_code__stock_min',
                                           'prod_code__stock_max', 'prod_code__pack_size').annotate(
                mysum=Sum('qty')).filter(prod_code__status="ACTIVE", mysum__gt=F('prod_code__stock_min'),
                                         mysum__lte=F('prod_code__stock_max')).order_by('prod_code')
        elif a == "" and b == "S":  # Surplus
            object_list = temporary.values('prod_code', 'prod_code__prod_desc', 'prod_code__stock_min',
                                           'prod_code__stock_max', 'prod_code__pack_size').annotate(
                mysum=Sum('qty')).filter(prod_code__status="ACTIVE", mysum__gt=F('prod_code__stock_max')).order_by(
                'prod_code')
        elif a == "" and b == "E":  # Empty
            object_list = temporary.values('prod_code', 'prod_code__prod_desc', 'prod_code__stock_min',
                                           'prod_code__stock_max', 'prod_code__pack_size').annotate(
                mysum=Sum('qty')).filter(prod_code__status="ACTIVE", mysum=0).order_by(
                'prod_code')  # stok sama dengan 0
        elif a == "" and b == "C":  # Critical
            object_list = temporary.values('prod_code', 'prod_code__prod_desc', 'prod_code__stock_min',
                                           'prod_code__stock_max', 'prod_code__pack_size').annotate(
                mysum=Sum('qty')).filter(prod_code__status="ACTIVE", mysum__gt=0,
                                         mysum__lte=F('prod_code__stock_min')).order_by(
                'prod_code')  # stok sama dengan / dibawah min
        elif b == "":
            object_list = temporary.values('prod_code', 'prod_code__prod_desc', 'prod_code__stock_min',
                                           'prod_code__stock_max', 'prod_code__pack_size').annotate(
                mysum=Sum('qty')).filter(prod_code_id=a, prod_code__status="ACTIVE").order_by('prod_code')
        elif b == "B":
            object_list = temporary.values('prod_code', 'prod_code__prod_desc', 'prod_code__stock_min',
                                           'prod_code__stock_max', 'prod_code__pack_size').annotate(
                mysum=Sum('qty')).filter(prod_code_id=a, prod_code__status="ACTIVE",
                                         mysum__gt=F('prod_code__stock_min'),
                                         mysum__lte=F('prod_code__stock_max')).order_by('prod_code')
        elif b == "S":
            object_list = temporary.values('prod_code', 'prod_code__prod_desc', 'prod_code__stock_min',
                                           'prod_code__stock_max', 'prod_code__pack_size').annotate(
                mysum=Sum('qty')).filter(prod_code_id=a, prod_code__status="ACTIVE",
                                         mysum__gt=F('prod_code__stock_max')).order_by('prod_code')
        elif b == "E":
            object_list = temporary.values('prod_code', 'prod_code__prod_desc', 'prod_code__stock_min',
                                           'prod_code__stock_max', 'prod_code__pack_size').annotate(
                mysum=Sum('qty')).filter(prod_code_id=a, prod_code__status="ACTIVE", mysum=0).order_by(
                'prod_code')  # stok sama dengan 0
        elif b == "C":
            object_list = temporary.values('prod_code', 'prod_code__prod_desc', 'prod_code__stock_min',
                                           'prod_code__stock_max', 'prod_code__pack_size').annotate(
                mysum=Sum('qty')).filter(prod_code_id=a, prod_code__status="ACTIVE", mysum__gt=0,
                                         mysum__lte=F('prod_code__stock_min')).order_by('prod_code')

        paginator = Paginator(object_list, 10)  # 10 posts per page
        page = self.request.GET.get('page')

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        return page_obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tb_temp'] = temporary.filter(no_loc_id__isnull=False)
        return context
