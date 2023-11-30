from django.urls import path
from . import views

urlpatterns = [
    path('main', views.MainMenu.as_view(), name='MainMenu'),
    path('', views.Dashboard.as_view(), name='Dashboard'),
    path('label', views.ViewLabel.as_view(), name='ViewLabel'),
    path('label/search', views.ResultLabel.as_view(), name='ResultLabel'),
    path('login', views.LoginPageView.as_view(), name='LoginPageView'),

    # u/ user
    path('user', views.ViewUser.as_view(), name='ViewUser'),
    path('user/edit/<pk>', views.EditUser.as_view(), name='EditUser'),
    path('user/add', views.AddUser.as_view(), name='AddUser'),

    # url u/ location: view, search, add, edit, edit as delete
    path('location', views.ViewLocation.as_view(), name='ViewLocation'),
    path('location/search', views.ResultLocation.as_view(), name='ResultLocation'),
    path('location/add', views.AddLocation.as_view(), name='AddLocation'),
    path('location/edit/<pk>', views.EditLocation.as_view(), name='EditLocation'),
    path('location/delete/<pk>', views.DeleteLocation.as_view(), name='DeleteLocation'),

    # url u/ product view, search, add, edit, detail
    path('product', views.ViewProduct.as_view(), name='ViewProduct'),
    path('product/search', views.ResultProduct.as_view(), name='ResultProduct'),
    path('product/add', views.AddProduct.as_view(), name='AddProduct'),
    path('product/edit/<pk>', views.EditProduct.as_view(), name='EditProduct'),
    path('product/detail/<pk>', views.DetailProduct.as_view(), name='DetailProduct'),

    # url u/ adjustment view, search
    path('record/adjust', views.ViewAdjustmentRecord.as_view(), name='ViewAdjustmentRecord'),
    path('record/adjust/search', views.ResultAdjustmentRecord.as_view(), name='ResultAdjustmentRecord'),
    path('record/loc', views.ViewLocationProduct.as_view(), name='ViewLocationProduct'),
    path('record/loc/search', views.ResultLocationProduct.as_view(), name='ResultLocationProduct'),
    path('record/stock', views.ViewStockProduct.as_view(), name='ViewStockProduct'),
    path('record/stock/search', views.ResultStockProduct.as_view(), name='ResultStockProduct'),

    # url u/ newline view, search, edit, edit as delete
    path('newline', views.ViewNewline.as_view(), name='ViewNewline'),
    path('newline/search', views.ResultNewline.as_view(), name='ResultNewline'),
    path('newline/edit/<pk>', views.EditNewline.as_view(), name='EditNewline'),
    path('newline/delete/<pk>', views.DeleteNewline.as_view(), name='DeleteNewline'),

    # url u/ transfer
    path('transfer', views.ViewTransfer.as_view(), name='ViewTransfer'),
    path('transfer/search', views.ResultTransfer.as_view(), name='ResultTransfer'),
    path('transfer/edit/<pk>', views.UpdateTransfer.as_view(), name='UpdateTransfer'),

    # url u/ inbound view, search, add, edit
    path('receiving', views.ViewReceiving.as_view(), name='ViewReceiving'),
    path('receiving/search', views.ResultReceiving.as_view(), name='ResultReceiving'),
    path('receiving/add', views.AddReceiving.as_view(), name='AddReceiving'),
    path('receiving/edit/<pk>', views.UpdateReceiving.as_view(), name='UpdateReceiving'),

    # url u/ picking view, search, edit
    path('picking', views.ViewPicking.as_view(), name='ViewPicking'),
    path('picking/search', views.ResultPicking.as_view(), name='ResultPicking'),
    path('picking/edit/<pk>', views.UpdatePicking.as_view(), name='UpdatePicking'),

    # url u/ stock opname view, search, edit
    path('sto', views.ViewStockOpname.as_view(), name='ViewStockOpname'),
    path('sto/search', views.ResultStockOpname.as_view(), name='ResultStockOpname'),
    path('sto/update/<pk>', views.UpdateStockOpname.as_view(), name='UpdateStockOpname'),
    path('sto/free/<pk>', views.ConfirmStockOpname.as_view(), name='ConfirmStockOpname'),
    path('sto/clear', views.RemoveCheckStockOpname.as_view(), name='RemoveCheckStockOpname'),
    path('sto/add/<pk>', views.AddRsvStockOpname.as_view(), name='AddRsvStockOpname'),
    # path('sto/edit', views.UpdateStockOpname.as_view(), name='UpdateStockOpname'),
    # path('sto/edit/<pk>', views.UpdateStockOpname.as_view(), name='UpdateStockOpname'),
]
