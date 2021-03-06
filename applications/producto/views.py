# Django
from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
    View,
)
# local
from applications.venta.models import SaleDetail
from applications.users.mixins import AlmacenPermisoMixin
#
from .models import Product
from .forms import ProductForm
from applications.utils import render_to_pdf


class ProductListView(AlmacenPermisoMixin, ListView):
    template_name = "producto/lista.html"
    context_object_name = 'productos'

    def get_queryset(self):
        kword = self.request.GET.get("kword", '')
        order = self.request.GET.get("order", '')
        queryset = Product.objects.buscar_producto(kword, order)
        return queryset



class ProductCreateView(AlmacenPermisoMixin, CreateView):
    template_name = "producto/form_producto.html"
    form_class = ProductForm
    success_url = reverse_lazy('producto_app:producto-lista')


class ProductUpdateView(AlmacenPermisoMixin, UpdateView):
    template_name = "producto/form_producto.html"
    """ 
        UpdateView trabaja con el modelo a actualizar el cual se pasas por url (pk) 
        la instancia es obtenida y se mapea al formulario
    """
    model = Product # cahchado por pk pasado por url
    form_class = ProductForm
    success_url = reverse_lazy('producto_app:producto-lista')



class ProductDeleteView(AlmacenPermisoMixin, DeleteView):
    template_name = "producto/delete.html"
    model = Product
    success_url = reverse_lazy('producto_app:producto-lista')


class ProductDetailView(AlmacenPermisoMixin, DetailView):
    template_name = "producto/detail.html"
    model = Product #Objeto recuprado por el pk pasado por url

    """ 
        Todas la vista genéricas tiene el get_context_data 
        auí se pueden mandar contextos extra hacia el template,
        los parametros pueden ser recuperados en el diccionario **kwargs        
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) #Extraemos el context_data
        # Inyectamos un nuevo elemento en el contexto
        context["ventas_mes"] = SaleDetail.objects.ventas_mes_producto(
            self.kwargs['pk'] #extraemos el pk del context_data (el cual es pasado por url)
        )
        return context


class ProductDetailViewPdf(AlmacenPermisoMixin, View):
    """ 
        Considerar instalar el paquete xhtml2pdf para trabajar con ducmentos PDF 
        además de construir un utils.py el cual se encarte de la conversion de 
        HTML a PDF
    """
    def get(self, request, *args, **kwargs):
        # Sobrescribir el método get
        producto = Product.objects.get(id=self.kwargs['pk'])
        data = {
            'product': producto,
            'ventas_mes': SaleDetail.objects.ventas_mes_producto(self.kwargs['pk'])
        }
        pdf = render_to_pdf('producto/detail-print.html', data)
        return HttpResponse(pdf, content_type='application/pdf')


class FiltrosProductListView(AlmacenPermisoMixin, ListView):
    template_name = "producto/filtros.html"    
    context_object_name = 'productos' # Nombre del diccionario de contexto
    # sobreescribimos el metodo get_queryset, para mandar datoae en particular
    def get_queryset(self):
        queryset = Product.objects.filtrar( # conectamos el managger filtrar
            # Obtenemos los parametros url GET sobre los cuales se hará el filtrado
            kword=self.request.GET.get("kword", ''),
            date_start=self.request.GET.get("date_start", ''),
            date_end=self.request.GET.get("date_end", ''),
            provider=self.request.GET.get("provider", ''),
            marca=self.request.GET.get("marca", ''),
            order=self.request.GET.get("order", ''),
        )
        return queryset
    


    
