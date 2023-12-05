from django.urls import path
from . import views

urlpatterns = [
    path('main', views.MainMenu.as_view(), name='MainMenu'),
    path('', views.Dashboard.as_view(), name='Dashboard'),
    path('label', views.ViewLabel.as_view(), name='ViewLabel'),
    path('label/search', views.ResultLabel.as_view(), name='ResultLabel'),

    # url u/ registration
    path('signup', views.SignupPageView.as_view(), name='SignupPageView'),
    path('login', views.LoginPageView.as_view(), name='LoginPageView'),
    path('logout', views.LogoutPageView.as_view(), name='LogoutPageView'),
    path('user/<pk>/change-password', views.ChangePassPageView.as_view(), name='ChangePassPageView'),
    path('user/<pk>/reset-password', views.ResetPassPageView.as_view(), name='ResetPassPageView'),
    path('user', views.ViewUser.as_view(), name='ViewUser'),
    path('user/search', views.ResultUser.as_view(), name='ResultUser'),
    path('user/<pk>/edit', views.EditUser.as_view(), name='EditUser'),
    path('user/<pk>/delete', views.DeleteUser.as_view(), name='DeleteUser'),

    # url u/ user uid
    path('user-uid', views.ViewUserUID.as_view(), name='ViewUserUID'),
    path('user-uid/add', views.AddUserUID.as_view(), name='AddUserUID'),
    path('user-uid/edit/<pk>', views.EditUserUID.as_view(), name='EditUserUID'),
    path('user-uid/delete/<pk>', views.DeleteUserUID.as_view(), name='DeleteUserUID'),

    # url u/ location: view, search, add, edit, edit as delete
    path('location', views.ViewLocation.as_view(), name='ViewLocation'),  # lock_login
    path('location/search', views.ResultLocation.as_view(), name='ResultLocation'),  # lock_login
    path('location/add', views.AddLocation.as_view(), name='AddLocation'),  # lock_login
    path('location/edit/<pk>', views.EditLocation.as_view(), name='EditLocation'),  # lock_login
    path('location/delete/<pk>', views.DeleteLocation.as_view(), name='DeleteLocation'),  # lock_login

    # url u/ product view, search, add, edit, detail
    path('product', views.ViewProduct.as_view(), name='ViewProduct'),  # lock_login
    path('product/search', views.ResultProduct.as_view(), name='ResultProduct'),  # lock_login
    path('product/add', views.AddProduct.as_view(), name='AddProduct'),  # lock_login
    path('product/edit/<pk>', views.EditProduct.as_view(), name='EditProduct'),  # lock_login
    path('product/detail/<pk>', views.DetailProduct.as_view(), name='DetailProduct'),  # lock_login

    # url u/ adjustment view, search
    path('record/adjust', views.ViewAdjustmentRecord.as_view(), name='ViewAdjustmentRecord'),  # lock_login
    path('record/adjust/search', views.ResultAdjustmentRecord.as_view(), name='ResultAdjustmentRecord'),  # lock_login
    path('record/loc', views.ViewLocationProduct.as_view(), name='ViewLocationProduct'),  # lock_login
    path('record/loc/search', views.ResultLocationProduct.as_view(), name='ResultLocationProduct'),  # lock_login
    path('record/stock', views.ViewStockProduct.as_view(), name='ViewStockProduct'),  # lock_login
    path('record/stock/search', views.ResultStockProduct.as_view(), name='ResultStockProduct'),  # lock_login

    # url u/ assign location view, search, edit, edit as delete
    path('newline', views.ViewNewline.as_view(), name='ViewNewline'),  # lock_login
    path('newline/search', views.ResultNewline.as_view(), name='ResultNewline'),  # lock_login
    path('newline/edit/<pk>', views.EditNewline.as_view(), name='EditNewline'),  # lock_login
    path('newline/delete/<pk>', views.DeleteNewline.as_view(), name='DeleteNewline'),  # lock_login

    # url u/ transfer view, search, edit
    path('transfer', views.ViewTransfer.as_view(), name='ViewTransfer'),  # lock_login
    path('transfer/search', views.ResultTransfer.as_view(), name='ResultTransfer'),  # lock_login
    path('transfer/edit/<pk>', views.UpdateTransfer.as_view(), name='UpdateTransfer'),  # lock_login

    # url u/ inbound view, search, add, edit
    path('receiving', views.ViewReceiving.as_view(), name='ViewReceiving'),  # lock_login
    path('receiving/search', views.ResultReceiving.as_view(), name='ResultReceiving'),  # lock_login
    path('receiving/add', views.AddReceiving.as_view(), name='AddReceiving'),  # lock_login
    path('receiving/edit/<pk>', views.UpdateReceiving.as_view(), name='UpdateReceiving'),  # lock_login

    # url u/ picking view, search, edit
    path('picking', views.ViewPicking.as_view(), name='ViewPicking'),
    path('picking/search', views.ResultPicking.as_view(), name='ResultPicking'),
    path('picking/edit/<pk>', views.UpdatePicking.as_view(), name='UpdatePicking'),

    # url u/ stock opname view, search, edit,
    path('sto', views.ViewStockOpname.as_view(), name='ViewStockOpname'),  # lock_login
    path('sto/search', views.ResultStockOpname.as_view(), name='ResultStockOpname'),  # lock_login
    path('sto/update/<pk>', views.UpdateStockOpname.as_view(), name='UpdateStockOpname'),  # lock_login
    path('sto/free/<pk>', views.ConfirmStockOpname.as_view(), name='ConfirmStockOpname'),  # lock_login
    path('sto/add/<pk>', views.AddRsvStockOpname.as_view(), name='AddRsvStockOpname'),  # lock_login
    path('sto/clear', views.RemoveCheckStockOpname.as_view(), name='RemoveCheckStockOpname'),  # lock_login
]
